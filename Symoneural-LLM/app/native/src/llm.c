/* llm.c — libsymoneural-llm: the SyMoNeuRaL-owned inference ABI over libllama + libggml.
 *
 * Everything llama.cpp-specific lives in this one translation unit. The public
 * header (symoneural/llm.h) shows callers opaque handles, size-prefixed parameter
 * structs and negative status codes; it never shows llama.h. A model is named by
 * ID and resolved to <registry_root>/<id>.gguf here - a caller cannot supply a
 * filesystem path, and an ID cannot escape the registry directory.
 *
 * Bound to the pinned upstream API (llama.cpp 5266f24d / b10809, ggml e91ded11 /
 * v0.23.0): llama_model_load_from_file, llama_init_from_model, llama_memory_clear,
 * llama_vocab_is_eog, llama_set_abort_callback. Deprecated spellings are not used.
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */
#define _XOPEN_SOURCE 700   /* realpath(3); implies _POSIX_C_SOURCE 200809L */
#include "symoneural/llm.h"

#include <llama.h>
#include <gguf.h>
#include <ggml-backend.h>

#include <limits.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#define SYM_LLM_ID_MAX 128
#define SYM_LLM_PIECE_MAX 512

struct sym_llm_runtime {
    char registry_root[PATH_MAX];
    int  n_threads;
    int  gpu_layers;
};

struct sym_llm_model {
    sym_llm_runtime          *rt;
    struct llama_model       *model;
    const struct llama_vocab *vocab;
    char                      id[SYM_LLM_ID_MAX];
    bool                      vocab_only;
};

struct sym_llm_session {
    sym_llm_model        *m;
    struct llama_context *ctx;
    uint32_t              seed;
    atomic_int            cancel;   /* set by sym_llm_cancel from any thread */
    atomic_int            busy;     /* one generate at a time per session   */
};

/* ---- backend lifetime: one llama_backend_init per process ------------------ */

static pthread_mutex_t g_backend_lock = PTHREAD_MUTEX_INITIALIZER;
static int             g_backend_refs = 0;

/* libllama logs everything at INFO by default, including the model path it is
 * opening. Errors go to stderr; the rest only when SYM_LLM_LOG is set. */
static void quiet_log(enum ggml_log_level level, const char *text, void *user)
{
    (void)user;
    static int verbose = -1, last_shown = 0;
    if (verbose < 0) {
        const char *v = getenv("SYM_LLM_LOG");
        verbose = (v != NULL && *v != '\0') ? 1 : 0;
    }
    if (level == GGML_LOG_LEVEL_CONT) {
        if (last_shown) fputs(text, stderr);
        return;
    }
    last_shown = (verbose || level == GGML_LOG_LEVEL_ERROR);
    if (last_shown) fputs(text, stderr);
}

static void backend_acquire(void)
{
    pthread_mutex_lock(&g_backend_lock);
    if (g_backend_refs++ == 0) {
        llama_log_set(quiet_log, NULL);
        llama_backend_init();
    }
    pthread_mutex_unlock(&g_backend_lock);
}

static void backend_release(void)
{
    pthread_mutex_lock(&g_backend_lock);
    if (g_backend_refs > 0 && --g_backend_refs == 0)
        llama_backend_free();
    pthread_mutex_unlock(&g_backend_lock);
}

/* ---- version / status --------------------------------------------------------- */

uint32_t sym_llm_abi_version(void) { return SYM_LLM_ABI_VERSION; }

const char *sym_llm_version_string(void)
{
    static char v[16];
    snprintf(v, sizeof v, "%d.%d.%d", SYM_LLM_ABI_MAJOR, SYM_LLM_ABI_MINOR, SYM_LLM_ABI_PATCH);
    return v;
}

const char *sym_llm_strerror(int st)
{
    switch (st) {
    case SYM_LLM_OK:         return "ok";
    case SYM_LLM_EINVAL:     return "invalid argument";
    case SYM_LLM_ENOSPC:     return "buffer too small";
    case SYM_LLM_ENOENT:     return "no such model in the registry";
    case SYM_LLM_EIO:        return "I/O error";
    case SYM_LLM_EBUSY:      return "session busy";
    case SYM_LLM_ECANCELLED: return "cancelled";
    case SYM_LLM_EABI:       return "ABI mismatch";
    case SYM_LLM_EBACKEND:   return "inference backend failure";
    }
    return "unknown";
}

static int put(char *buf, size_t cap, const char *s)
{
    if (buf == NULL || cap == 0) return SYM_LLM_EINVAL;
    size_t n = strlen(s);
    if (n + 1 > cap) return SYM_LLM_ENOSPC;
    memcpy(buf, s, n + 1);
    return SYM_LLM_OK;
}

/* "gpu:<backend>" names the ggml backend of the first GPU device the registry can
 * see at call time - which needs the driver's libcuda.so.1 to be loadable - and
 * "cpu" is reported when no GPU device is enumerable, whether or not a GPU backend
 * was compiled in. So the token is a statement about this process on this machine,
 * not about the build. ABI 1.1.0: the token set grew; nothing was removed. */
int sym_llm_capabilities(char *buf, size_t cap)
{
    const char *gpu = NULL;
    for (size_t i = 0; i < ggml_backend_dev_count(); i++) {
        ggml_backend_dev_t dev = ggml_backend_dev_get(i);
        if (ggml_backend_dev_type(dev) == GGML_BACKEND_DEVICE_TYPE_GPU) {
            gpu = ggml_backend_reg_name(ggml_backend_dev_backend_reg(dev));
            break;
        }
    }
    char s[256];
    snprintf(s, sizeof s, "text streaming cancellation tokenize %s%s",
             gpu ? "gpu:" : "cpu", gpu ? gpu : "");
    return put(buf, cap, s);
}

/* ---- runtime -------------------------------------------------------------------- */

int sym_llm_runtime_open(const sym_llm_runtime_params *p, sym_llm_runtime **out)
{
    if (p == NULL || out == NULL) return SYM_LLM_EINVAL;
    *out = NULL;
    /* v1 knows one layout; a struct of another size is another ABI */
    if (p->size != sizeof *p) return SYM_LLM_EABI;
    if (p->registry_root == NULL || p->registry_root[0] == '\0') return SYM_LLM_EINVAL;
    if (p->n_threads < 0 || p->gpu_layers < -1) return SYM_LLM_EINVAL;

    struct stat st;
    if (stat(p->registry_root, &st) != 0) return SYM_LLM_ENOENT;
    if (!S_ISDIR(st.st_mode)) return SYM_LLM_EINVAL;
    /* GPU layers need a GPU backend compiled into libggml; this build says so itself */
    if (p->gpu_layers != 0 && !llama_supports_gpu_offload()) return SYM_LLM_EBACKEND;

    sym_llm_runtime *rt = calloc(1, sizeof *rt);
    if (rt == NULL) return SYM_LLM_EIO;
    if (realpath(p->registry_root, rt->registry_root) == NULL) { free(rt); return SYM_LLM_ENOENT; }
    rt->n_threads  = p->n_threads;
    rt->gpu_layers = p->gpu_layers;
    backend_acquire();
    *out = rt;
    return SYM_LLM_OK;
}

void sym_llm_runtime_close(sym_llm_runtime *rt)
{
    if (rt == NULL) return;
    backend_release();
    free(rt);
}

/* ---- model identity -> registry file ----------------------------------------- */

/* ^[A-Za-z0-9][A-Za-z0-9._-]{0,126}$ and never "..": the ID can only ever name a
 * regular file directly inside the registry root. */
static bool valid_id(const char *id)
{
    size_t n = strlen(id);
    if (n == 0 || n >= SYM_LLM_ID_MAX) return false;
    for (size_t i = 0; i < n; i++) {
        unsigned char c = (unsigned char)id[i];
        bool alnum = (c >= '0' && c <= '9') || (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
        if (i == 0 ? !alnum : !(alnum || c == '.' || c == '_' || c == '-')) return false;
    }
    return strstr(id, "..") == NULL;
}

int sym_llm_model_load(sym_llm_runtime *rt, const char *model_id, sym_llm_model **out)
{
    if (rt == NULL || model_id == NULL || out == NULL) return SYM_LLM_EINVAL;
    *out = NULL;
    if (!valid_id(model_id)) return SYM_LLM_EINVAL;

    char path[PATH_MAX];
    int n = snprintf(path, sizeof path, "%s/%s.gguf", rt->registry_root, model_id);
    if (n < 0 || (size_t)n >= sizeof path) return SYM_LLM_EINVAL;
    struct stat st;
    if (stat(path, &st) != 0 || !S_ISREG(st.st_mode)) return SYM_LLM_ENOENT;

    /* A GGUF with no tensors is a vocabulary: load it as one (tokenize/detokenize
     * only; session_open refuses it). Read the header without allocating tensors. */
    struct gguf_init_params gp = { .no_alloc = true, .ctx = NULL };
    struct gguf_context *g = gguf_init_from_file(path, gp);
    if (g == NULL) return SYM_LLM_EIO;
    bool vocab_only = gguf_get_n_tensors(g) == 0;
    gguf_free(g);

    struct llama_model_params mp = llama_model_default_params();
    mp.vocab_only   = vocab_only;
    mp.n_gpu_layers = rt->gpu_layers;
    struct llama_model *lm = llama_model_load_from_file(path, mp);
    if (lm == NULL) return SYM_LLM_EBACKEND;

    sym_llm_model *m = calloc(1, sizeof *m);
    if (m == NULL) { llama_model_free(lm); return SYM_LLM_EIO; }
    m->rt = rt; m->model = lm; m->vocab = llama_model_get_vocab(lm); m->vocab_only = vocab_only;
    snprintf(m->id, sizeof m->id, "%s", model_id);
    *out = m;
    return SYM_LLM_OK;
}

void sym_llm_model_unload(sym_llm_model *m)
{
    if (m == NULL) return;
    llama_model_free(m->model);
    free(m);
}

/* minimal JSON string escaping for metadata values we did not write */
static void json_escape(const char *s, char *out, size_t cap)
{
    size_t o = 0;
    for (; *s && o + 7 < cap; s++) {
        unsigned char c = (unsigned char)*s;
        if (c == '"' || c == '\\') { out[o++] = '\\'; out[o++] = (char)c; }
        else if (c < 0x20) o += (size_t)snprintf(out + o, cap - o, "\\u%04x", c);
        else out[o++] = (char)c;
    }
    out[o] = '\0';
}

int sym_llm_model_info(const sym_llm_model *m, char *json, size_t cap)
{
    if (m == NULL || json == NULL || cap == 0) return SYM_LLM_EINVAL;
    char arch[64] = "", name[128] = "", desc[128] = "";
    char earch[160], ename[320], edesc[320];
    if (llama_model_meta_val_str(m->model, "general.architecture", arch, sizeof arch) < 0) arch[0] = '\0';
    if (llama_model_meta_val_str(m->model, "general.name", name, sizeof name) < 0) name[0] = '\0';
    if (llama_model_desc(m->model, desc, sizeof desc) < 0) desc[0] = '\0';
    json_escape(arch, earch, sizeof earch);
    json_escape(name, ename, sizeof ename);
    json_escape(desc, edesc, sizeof edesc);
    int n = snprintf(json, cap,
        "{\"id\":\"%s\",\"arch\":\"%s\",\"name\":\"%s\",\"desc\":\"%s\","
        "\"n_ctx_train\":%d,\"n_vocab\":%d,\"n_params\":%llu,\"vocab_only\":%s}",
        m->id, earch, ename, edesc,
        (int)llama_model_n_ctx_train(m->model), (int)llama_vocab_n_tokens(m->vocab),
        (unsigned long long)llama_model_n_params(m->model), m->vocab_only ? "true" : "false");
    if (n < 0) return SYM_LLM_EIO;
    if ((size_t)n >= cap) { json[0] = '\0'; return SYM_LLM_ENOSPC; }
    return SYM_LLM_OK;
}

/* ---- sessions --------------------------------------------------------------------- */

static bool abort_cb(void *data)
{
    return atomic_load(&((sym_llm_session *)data)->cancel) != 0;
}

int sym_llm_session_open(sym_llm_model *m, const sym_llm_session_params *p, sym_llm_session **out)
{
    if (m == NULL || p == NULL || out == NULL) return SYM_LLM_EINVAL;
    *out = NULL;
    if (p->size != sizeof *p) return SYM_LLM_EABI;
    if (p->n_ctx < 0) return SYM_LLM_EINVAL;
    if (m->vocab_only) return SYM_LLM_EINVAL;   /* a vocabulary carries no weights to run */

    sym_llm_session *s = calloc(1, sizeof *s);
    if (s == NULL) return SYM_LLM_EIO;
    s->m = m; s->seed = p->seed;
    atomic_init(&s->cancel, 0);
    atomic_init(&s->busy, 0);

    struct llama_context_params cp = llama_context_default_params();
    if (p->n_ctx > 0) cp.n_ctx = (uint32_t)p->n_ctx;
    if (m->rt->n_threads > 0) { cp.n_threads = m->rt->n_threads; cp.n_threads_batch = m->rt->n_threads; }
    cp.no_perf = true;
    cp.abort_callback = abort_cb;
    cp.abort_callback_data = s;
    s->ctx = llama_init_from_model(m->model, cp);
    if (s->ctx == NULL) { free(s); return SYM_LLM_EBACKEND; }
    *out = s;
    return SYM_LLM_OK;
}

void sym_llm_session_close(sym_llm_session *s)
{
    if (s == NULL) return;
    llama_free(s->ctx);
    free(s);
}

int sym_llm_session_reset(sym_llm_session *s)
{
    if (s == NULL) return SYM_LLM_EINVAL;
    if (atomic_load(&s->busy)) return SYM_LLM_EBUSY;
    llama_memory_clear(llama_get_memory(s->ctx), true);
    atomic_store(&s->cancel, 0);
    return SYM_LLM_OK;
}

int sym_llm_cancel(sym_llm_session *s)
{
    if (s == NULL) return SYM_LLM_EINVAL;
    atomic_store(&s->cancel, 1);
    return SYM_LLM_OK;
}

/* ---- tokens ----------------------------------------------------------------------- */

int sym_llm_tokenize(const sym_llm_model *m, const char *text, int32_t *tokens, size_t cap, size_t *n_out)
{
    if (m == NULL || text == NULL || n_out == NULL) return SYM_LLM_EINVAL;
    if (tokens == NULL && cap != 0) return SYM_LLM_EINVAL;
    if (cap > INT32_MAX) return SYM_LLM_EINVAL;
    size_t len = strlen(text);
    if (len > INT32_MAX) return SYM_LLM_EINVAL;
    int32_t n = llama_tokenize(m->vocab, text, (int32_t)len, tokens, (int32_t)cap, true, true);
    if (n < 0) { *n_out = (size_t)(-n); return SYM_LLM_ENOSPC; }   /* *n_out says how many */
    *n_out = (size_t)n;
    return SYM_LLM_OK;
}

int sym_llm_detokenize(const sym_llm_model *m, const int32_t *tokens, size_t n, char *buf, size_t cap)
{
    if (m == NULL || buf == NULL || cap == 0) return SYM_LLM_EINVAL;
    if ((tokens == NULL && n != 0) || n > INT32_MAX || cap > INT32_MAX) return SYM_LLM_EINVAL;
    int32_t r = llama_detokenize(m->vocab, tokens, (int32_t)n, buf, (int32_t)(cap - 1), false, false);
    if (r < 0) { buf[0] = '\0'; return SYM_LLM_ENOSPC; }
    buf[r] = '\0';
    return SYM_LLM_OK;
}

/* ---- generation ------------------------------------------------------------------ */

static int decode_batch(sym_llm_session *s, llama_token *toks, int32_t n)
{
    if (atomic_load(&s->cancel)) return SYM_LLM_ECANCELLED;
    int rc = llama_decode(s->ctx, llama_batch_get_one(toks, n));
    if (rc == 0) return SYM_LLM_OK;
    if (rc == 2) return SYM_LLM_ECANCELLED;   /* aborted through abort_cb */
    return SYM_LLM_EBACKEND;                  /* 1: no memory slot; <0: error */
}

int sym_llm_generate(sym_llm_session *s, const char *prompt, const sym_llm_sampling *sp,
                     sym_llm_token_cb cb, void *user, sym_llm_result *out)
{
    if (s == NULL || prompt == NULL || sp == NULL || out == NULL) return SYM_LLM_EINVAL;
    if (sp->size != sizeof *sp || out->size != sizeof *out) return SYM_LLM_EABI;
    if (sp->max_tokens <= 0) return SYM_LLM_EINVAL;
    if (atomic_exchange(&s->busy, 1)) return SYM_LLM_EBUSY;

    int rc = SYM_LLM_OK;
    struct llama_sampler *smpl = NULL;
    llama_token *ptoks = NULL;
    const struct llama_vocab *vocab = s->m->vocab;

    atomic_store(&s->cancel, 0);
    out->stop_reason = 0; out->prompt_tokens = 0; out->output_tokens = 0;

    /* Each call evaluates its prompt from a cleared memory: the caller sends the
     * whole transcript (that is how symoneural_llm.inference drives it). */
    llama_memory_clear(llama_get_memory(s->ctx), true);

    size_t plen = strlen(prompt);
    if (plen == 0 || plen > INT32_MAX) { rc = SYM_LLM_EINVAL; goto done; }
    int32_t n_prompt = -llama_tokenize(vocab, prompt, (int32_t)plen, NULL, 0, true, true);
    if (n_prompt <= 0) { rc = SYM_LLM_EINVAL; goto done; }
    uint32_t n_ctx = llama_n_ctx(s->ctx);
    if ((uint32_t)n_prompt >= n_ctx) { rc = SYM_LLM_EINVAL; goto done; }   /* prompt does not fit */

    ptoks = malloc((size_t)n_prompt * sizeof *ptoks);
    if (ptoks == NULL) { rc = SYM_LLM_EIO; goto done; }
    if (llama_tokenize(vocab, prompt, (int32_t)plen, ptoks, n_prompt, true, true) < 0) { rc = SYM_LLM_EBACKEND; goto done; }
    out->prompt_tokens = n_prompt;

    int32_t n_batch = (int32_t)llama_n_batch(s->ctx);
    if (n_batch <= 0) n_batch = 512;
    for (int32_t i = 0; i < n_prompt; i += n_batch) {
        int32_t n = (n_prompt - i < n_batch) ? n_prompt - i : n_batch;
        if ((rc = decode_batch(s, ptoks + i, n)) != SYM_LLM_OK) goto done;
    }
    int32_t n_past = n_prompt;

    struct llama_sampler_chain_params scp = llama_sampler_chain_default_params();
    scp.no_perf = true;
    smpl = llama_sampler_chain_init(scp);
    if (smpl == NULL) { rc = SYM_LLM_EBACKEND; goto done; }
    if (sp->temperature <= 0.0f) {
        llama_sampler_chain_add(smpl, llama_sampler_init_greedy());
    } else {
        if (sp->repeat_penalty > 0.0f && sp->repeat_penalty != 1.0f)
            llama_sampler_chain_add(smpl, llama_sampler_init_penalties(llama_vocab_n_tokens(vocab), 64, sp->repeat_penalty, 0.0f, 0.0f));
        if (sp->top_k > 0) llama_sampler_chain_add(smpl, llama_sampler_init_top_k(sp->top_k));
        if (sp->top_p > 0.0f && sp->top_p < 1.0f) llama_sampler_chain_add(smpl, llama_sampler_init_top_p(sp->top_p, 1));
        llama_sampler_chain_add(smpl, llama_sampler_init_temp(sp->temperature));
        llama_sampler_chain_add(smpl, llama_sampler_init_dist(s->seed != 0 ? s->seed : LLAMA_DEFAULT_SEED));
    }

    char piece[SYM_LLM_PIECE_MAX];
    for (;;) {
        if (atomic_load(&s->cancel)) { out->stop_reason = 2; rc = SYM_LLM_ECANCELLED; goto done; }
        llama_token tok = llama_sampler_sample(smpl, s->ctx, -1);   /* samples and accepts */
        if (llama_vocab_is_eog(vocab, tok)) { out->stop_reason = 0; break; }
        int32_t n = llama_token_to_piece(vocab, tok, piece, (int32_t)sizeof piece, 0, true);
        if (n < 0) { rc = SYM_LLM_EBACKEND; goto done; }
        out->output_tokens++;
        if (cb != NULL && n > 0 && cb(piece, (size_t)n, user) != 0) { out->stop_reason = 2; rc = SYM_LLM_ECANCELLED; goto done; }
        if (out->output_tokens >= sp->max_tokens) { out->stop_reason = 1; break; }
        if ((uint32_t)n_past + 1 >= n_ctx) { out->stop_reason = 1; break; }   /* context full */
        if ((rc = decode_batch(s, &tok, 1)) != SYM_LLM_OK) { if (rc == SYM_LLM_ECANCELLED) out->stop_reason = 2; goto done; }
        n_past++;
    }
    rc = SYM_LLM_OK;

done:
    if (smpl != NULL) llama_sampler_free(smpl);
    free(ptoks);
    atomic_store(&s->busy, 0);
    return rc;
}
