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
gpu:<backend>|cpu|backend:none" — what this process can see on this machine, not
what was built: `gpu:CUDA` when the cuda module loaded and a GPU is enumerable,
`cpu` when only the CPU module loaded, `backend:none` when no module loaded). Errors: `OK 0, EINVAL, ENOSPC, ENOENT, EIO, EBUSY,
ECANCELLED, EABI, EBACKEND`.

Threading: one session is used by one thread at a time; `cancel` is the only
call safe from another thread on a busy session. Linkage evidence to be recorded
in `LINKAGE-EVIDENCE.md` when built (readelf: libllama, libggml, libc/libstdc++).

## Implementation (v1.0.0, 2026-09-14 — `Symoneural-LLM/app/native/src/llm.c`)

Bound to the pinned upstream API only (llama.cpp `5266f24d`, ggml `e91ded11`); no
deprecated spelling is used, so a future pin that removes one fails at compile time,
not at run time.

- **Registry layout.** `model_id` matches `^[A-Za-z0-9][A-Za-z0-9._-]{0,126}$` and never
  contains `..`; the library opens exactly `<registry_root>/<id>.gguf` (root taken by
  `realpath` at `runtime_open`). Anything else is `EINVAL`/`ENOENT`. A client cannot
  name a path.
- **Vocabulary-only models.** A GGUF with zero tensors (read through `gguf.h` before
  loading) is loaded `vocab_only`: `tokenize`/`detokenize`/`model_info` work,
  `session_open` returns `EINVAL`. This is what llama.cpp's own `models/ggml-vocab-*.gguf`
  fixtures are.
- **Generate semantics.** Each call clears the session memory and evaluates the whole
  prompt (the Python layer sends the full transcript). Prompt is tokenised with BOS and
  special tokens parsed; decoded in `n_batch` chunks. Sampler chain from the caller's
  parameters: `temperature <= 0` → greedy; otherwise penalties (last 64, if
  `repeat_penalty` is set and ≠ 1) → `top_k` → `top_p` (min_keep 1) → temp → dist.
  `seed == 0` means llama's default (non-deterministic); any other value is fixed.
  Stop reasons: `0` end-of-generation token, `1` `max_tokens` **or context full**,
  `2` cancelled (callback returned non-zero, or `sym_llm_cancel` from another thread —
  delivered through llama's abort callback, so a long `llama_decode` also stops).
- **Concurrency.** One `generate` per session at a time (`EBUSY` otherwise);
  `cancel` is the only call safe from another thread on a busy session (atomics).
  `llama_backend_init/free` are reference-counted across runtimes under a mutex.
- **Diagnostics.** libllama's log goes to stderr only at ERROR level unless
  `SYM_LLM_LOG` is set; status codes and `strerror` text never carry a path.
- **Linkage.** `llama.pc` → `-lggml -lggml-base -lllama`; `gguf_*` comes from
  libggml-base, the device registry from libggml. The public header is C17 with no
  llama type in it.
- **Backends (1.1.1, P7 C6).** ggml is built with `GGML_BACKEND_DL`: each backend is
  a dlopen'ed module in `<libdir>/ggml/` (`libggml-cpu.so` in symoneural-ggml,
  `libggml-cuda.so` in symoneural-ggml-cuda), so libggml itself never NEEDs the
  driver. The library loads the modules once per process from the directory next to
  itself (`dladdr` → `<dir>/ggml`) before anything asks the registry; because llama
  only runs its own `ggml_backend_load_all` (compiled-in dir, executable dir, cwd) when
  nothing is registered yet, that fallback never runs while the packages are intact.
  A module whose dependencies are missing — the cuda module without the driver's
  `libcuda.so.1` — fails to dlopen and that backend is absent; nothing else changes.
- **Version integer.** `abi_version()` is `major<<16 | minor<<8 | patch`: 1.1.0 →
  65792, 1.1.1 → 65793. Consumers compare the major (the Python binding does).
- **Consumers.** `symoneural_llm/native.py` (ctypes, ABI-major-checked, runs the
  blocking call on a worker thread and streams pieces through an incremental UTF-8
  decoder) and `symoneural-llm-util` (argv-only operator/proof tool).
