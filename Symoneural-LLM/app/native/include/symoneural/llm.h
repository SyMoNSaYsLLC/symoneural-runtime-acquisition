/* symoneural/llm.h — the stable C ABI of libsymoneural-llm (design v1.0.0, L3).
 *
 * A SyMoNeuRaL-owned inference boundary on top of libllama + libggml. Public
 * headers are C; libllama's C++ internals never appear here. Python binds to
 * THIS ABI, never to llama.h directly. Independent of libsymoneural-api: the two
 * compose above the native boundary and are never merged.
 *
 * Rules: C17 · no Python/C++ types · bounded buffers (ENOSPC, never truncation)
 * · versioned ABI · stable negative status codes · model identity is an ID that
 * the library resolves through a registry path set at runtime creation - a
 * client never supplies a filesystem path · no secret-bearing diagnostics ·
 * no protocol parsing (Anthropic/OpenAI live in Python).
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */
#ifndef SYMONEURAL_LLM_H
#define SYMONEURAL_LLM_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#define SYM_LLM_ABI_MAJOR 1
#define SYM_LLM_ABI_MINOR 1
#define SYM_LLM_ABI_PATCH 0
#define SYM_LLM_ABI_VERSION ((SYM_LLM_ABI_MAJOR << 16) | (SYM_LLM_ABI_MINOR << 8) | SYM_LLM_ABI_PATCH)

typedef enum {
    SYM_LLM_OK = 0, SYM_LLM_EINVAL = -1, SYM_LLM_ENOSPC = -2, SYM_LLM_ENOENT = -3,
    SYM_LLM_EIO = -4, SYM_LLM_EBUSY = -5, SYM_LLM_ECANCELLED = -6, SYM_LLM_EABI = -7,
    SYM_LLM_EBACKEND = -8            /* libllama / libggml reported failure */
} sym_llm_status;

typedef struct sym_llm_runtime sym_llm_runtime;   /* opaque: backends, thread pool, registry root */
typedef struct sym_llm_model   sym_llm_model;     /* opaque: a loaded model */
typedef struct sym_llm_session sym_llm_session;   /* opaque: KV cache + sampling state */

/* Versioned parameter structs: size first, so a newer library can accept an
 * older struct and an older library rejects a newer one with EABI. */
typedef struct {
    uint32_t    size;                 /* sizeof(sym_llm_runtime_params) */
    const char *registry_root;        /* directory the model register maps ids into */
    int         n_threads;            /* 0 = library default */
    int         gpu_layers;           /* 0 = CPU only; -1 = all (GPU backend must be present) */
} sym_llm_runtime_params;

typedef struct {
    uint32_t size;
    int      n_ctx;                   /* 0 = model default */
    uint32_t seed;
} sym_llm_session_params;

typedef struct {
    uint32_t size;
    int      max_tokens;
    float    temperature;
    float    top_p;
    int      top_k;
    float    repeat_penalty;
} sym_llm_sampling;

/* Stream callback: one decoded text piece per call; return 0 to continue,
 * non-zero to cancel (the generate call then returns ECANCELLED). Called on the
 * caller's thread. */
typedef int (*sym_llm_token_cb)(const char *piece, size_t len, void *user);

uint32_t    sym_llm_abi_version(void);
const char *sym_llm_version_string(void);
const char *sym_llm_strerror(int status);
/* space-separated: "text streaming cancellation tokenize gpu:<backend>|cpu";
 * gpu:<backend> only when a GPU device is enumerable in this process (1.1.0) */
int         sym_llm_capabilities(char *buf, size_t cap);

int  sym_llm_runtime_open(const sym_llm_runtime_params *p, sym_llm_runtime **out);
void sym_llm_runtime_close(sym_llm_runtime *rt);

/* Models are named by ID; the runtime resolves the file through its registry. */
int  sym_llm_model_load(sym_llm_runtime *rt, const char *model_id, sym_llm_model **out);
void sym_llm_model_unload(sym_llm_model *m);
int  sym_llm_model_info(const sym_llm_model *m, char *json, size_t cap);   /* id, n_ctx_train, n_vocab, arch */

int  sym_llm_session_open(sym_llm_model *m, const sym_llm_session_params *p, sym_llm_session **out);
void sym_llm_session_close(sym_llm_session *s);
int  sym_llm_session_reset(sym_llm_session *s);

/* Tokenisation into a bounded int32 array; *n_out receives the count. */
int  sym_llm_tokenize(const sym_llm_model *m, const char *text, int32_t *tokens, size_t cap, size_t *n_out);
int  sym_llm_detokenize(const sym_llm_model *m, const int32_t *tokens, size_t n, char *buf, size_t cap);

/* Generation streams through cb; returns OK, ECANCELLED, or a failure. The
 * stop reason and token accounting are reported through the out struct. */
typedef struct {
    uint32_t size;
    int      stop_reason;             /* 0 end_turn, 1 max_tokens, 2 cancelled */
    int      prompt_tokens;
    int      output_tokens;
} sym_llm_result;
int  sym_llm_generate(sym_llm_session *s, const char *prompt, const sym_llm_sampling *sp,
                      sym_llm_token_cb cb, void *user, sym_llm_result *out);
/* Cancel from another thread: the running generate returns ECANCELLED at the
 * next token boundary. */
int  sym_llm_cancel(sym_llm_session *s);

#ifdef __cplusplus
}
#endif
#endif /* SYMONEURAL_LLM_H */
