/* util-main.c — symoneural-llm-util: an argv-driven operator/proof tool over the
 * libsymoneural-llm ABI. It exists so a clean root can exercise the native chain
 * without Python. Every argument is positional; there is no shell, no config file,
 * and the registry root is whatever the operator passes - the same rule the
 * runtime enforces for its clients.
 *
 *   symoneural-llm-util version | abi | capabilities
 *   symoneural-llm-util models   <registry_root>
 *   symoneural-llm-util info     <registry_root> <model_id>
 *   symoneural-llm-util tokenize <registry_root> <model_id> <text>
 *   symoneural-llm-util generate <registry_root> <model_id> <prompt> [max_tokens] [temperature] [seed]
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */
#define _POSIX_C_SOURCE 200809L
#include "symoneural/llm.h"

#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int fail(const char *what, int st)
{
    fprintf(stderr, "symoneural-llm-util: %s: %s (%d)\n", what, sym_llm_strerror(st), st);
    return 1;
}

static int usage(void)
{
    fputs("usage: symoneural-llm-util version|abi|capabilities\n"
          "       symoneural-llm-util models   <registry_root>\n"
          "       symoneural-llm-util info     <registry_root> <model_id>\n"
          "       symoneural-llm-util tokenize <registry_root> <model_id> <text>\n"
          "       symoneural-llm-util generate <registry_root> <model_id> <prompt> [max_tokens] [temperature] [seed]\n", stderr);
    return 2;
}

static int open_runtime(const char *root, sym_llm_runtime **rt)
{
    sym_llm_runtime_params p = { .size = sizeof p, .registry_root = root, .n_threads = 0, .gpu_layers = 0 };
    return sym_llm_runtime_open(&p, rt);
}

static int on_piece(const char *piece, size_t len, void *user)
{
    (void)user;
    fwrite(piece, 1, len, stdout);
    fflush(stdout);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2) return usage();
    const char *cmd = argv[1];

    if (strcmp(cmd, "version") == 0)      { puts(sym_llm_version_string()); return 0; }
    if (strcmp(cmd, "abi") == 0)          { printf("%u\n", sym_llm_abi_version()); return 0; }
    if (strcmp(cmd, "capabilities") == 0) {
        char buf[256]; int st = sym_llm_capabilities(buf, sizeof buf);
        if (st) return fail("capabilities", st);
        puts(buf); return 0;
    }

    if (strcmp(cmd, "models") == 0) {
        if (argc != 3) return usage();
        /* the registry is a directory of <id>.gguf; list the ids the library would accept */
        sym_llm_runtime *rt; int st = open_runtime(argv[2], &rt);
        if (st) return fail("runtime_open", st);
        DIR *d = opendir(argv[2]);
        if (d == NULL) { sym_llm_runtime_close(rt); return fail("registry", SYM_LLM_EIO); }
        struct dirent *e;
        while ((e = readdir(d)) != NULL) {
            size_t n = strlen(e->d_name);
            if (n > 5 && strcmp(e->d_name + n - 5, ".gguf") == 0 && e->d_name[0] != '.')
                printf("%.*s\n", (int)(n - 5), e->d_name);
        }
        closedir(d); sym_llm_runtime_close(rt); return 0;
    }

    if (argc < 4) return usage();
    sym_llm_runtime *rt; int st = open_runtime(argv[2], &rt);
    if (st) return fail("runtime_open", st);
    sym_llm_model *m; st = sym_llm_model_load(rt, argv[3], &m);
    if (st) { sym_llm_runtime_close(rt); return fail("model_load", st); }
    int rc = 0;

    if (strcmp(cmd, "info") == 0) {
        char json[1024]; st = sym_llm_model_info(m, json, sizeof json);
        if (st) rc = fail("model_info", st); else puts(json);
    } else if (strcmp(cmd, "tokenize") == 0) {
        if (argc != 5) { rc = usage(); goto out; }
        size_t n = 0;
        st = sym_llm_tokenize(m, argv[4], NULL, 0, &n);
        if (st != SYM_LLM_ENOSPC && st != SYM_LLM_OK) { rc = fail("tokenize", st); goto out; }
        int32_t *toks = calloc(n ? n : 1, sizeof *toks);
        if (toks == NULL) { rc = fail("tokenize", SYM_LLM_EIO); goto out; }
        st = sym_llm_tokenize(m, argv[4], toks, n, &n);
        if (st) { free(toks); rc = fail("tokenize", st); goto out; }
        printf("{\"n_tokens\":%zu,\"tokens\":[", n);
        for (size_t i = 0; i < n; i++) printf("%s%d", i ? "," : "", toks[i]);
        char text[4096]; st = sym_llm_detokenize(m, toks, n, text, sizeof text);
        printf("],\"detokenize_status\":%d,\"round_trip\":\"", st);
        for (const char *c = text; st == 0 && *c; c++) {
            if (*c == '"' || *c == '\\') printf("\\%c", *c);
            else if ((unsigned char)*c < 0x20) printf("\\u%04x", (unsigned char)*c);
            else putchar(*c);
        }
        puts("\"}");
        free(toks);
    } else if (strcmp(cmd, "generate") == 0) {
        if (argc < 5 || argc > 8) { rc = usage(); goto out; }
        sym_llm_session_params sp = { .size = sizeof sp, .n_ctx = 0, .seed = argc > 7 ? (uint32_t)strtoul(argv[7], NULL, 10) : 0 };
        sym_llm_session *s; st = sym_llm_session_open(m, &sp, &s);
        if (st) { rc = fail("session_open", st); goto out; }
        sym_llm_sampling smp = { .size = sizeof smp, .max_tokens = argc > 5 ? atoi(argv[5]) : 64,
                                 .temperature = argc > 6 ? (float)atof(argv[6]) : 0.0f,
                                 .top_p = 0.95f, .top_k = 40, .repeat_penalty = 1.0f };
        sym_llm_result r = { .size = sizeof r };
        st = sym_llm_generate(s, argv[4], &smp, on_piece, NULL, &r);
        putchar('\n');
        fprintf(stderr, "{\"status\":%d,\"stop_reason\":%d,\"prompt_tokens\":%d,\"output_tokens\":%d}\n",
                st, r.stop_reason, r.prompt_tokens, r.output_tokens);
        sym_llm_session_close(s);
        if (st) rc = fail("generate", st);
    } else {
        rc = usage();
    }
out:
    sym_llm_model_unload(m);
    sym_llm_runtime_close(rt);
    return rc;
}
