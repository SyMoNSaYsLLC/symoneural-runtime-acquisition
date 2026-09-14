# libsymoneural-llm C ABI (design v1.0.0 — L3, implementation pending libllama)

Header: `Symoneural-LLM/app/native/include/symoneural/llm.h`. C17; Python binds
here, never to `llama.h`. Version `(MAJOR<<16)|(MINOR<<8)|PATCH`; size-prefixed
parameter structs so mismatches fail with `EABI`.

Lifecycle: `runtime_open(params{registry_root, n_threads, gpu_layers})` →
`model_load(rt, model_id)` (id resolved through the registry; no client paths) →
`session_open(model, {n_ctx, seed})` → `generate(session, prompt, sampling, cb,
user, result)` streaming one decoded piece per callback, cancellable from another
thread (`cancel` → `ECANCELLED` at the next token) → `session_close` →
`model_unload` → `runtime_close`. Also `tokenize`/`detokenize` (bounded),
`model_info` JSON, `capabilities` ("text streaming cancellation tokenize
gpu:<backend>|cpu"). Errors: `OK 0, EINVAL, ENOSPC, ENOENT, EIO, EBUSY,
ECANCELLED, EABI, EBACKEND`.

Threading: one session is used by one thread at a time; `cancel` is the only
call safe from another thread on a busy session. Linkage evidence to be recorded
in `LINKAGE-EVIDENCE.md` when built (readelf: libllama, libggml, libc/libstdc++).
