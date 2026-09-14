# Symoneural-LLM architecture (reconstruction v1.1 §49–§56)

```
applications / demos           Claude adapter (POST /v1/messages)     [optional OpenAI adapter]
         │                                 │
         └──────────────► symoneural_llm.inference.InferenceService ◄─┘
                            models · sessions · generate · stream · cancel · capabilities
                                           │  Backend protocol (backend.py)
                                           ▼
                            ctypes → libsymoneural-llm  (C ABI, include/symoneural/llm.h)     [L3/L4]
                                           │
                                        libllama  (llama.cpp 5266f24d, library only, LLAMA_USE_SYSTEM_GGML)
                                           │
                                        libggml   (canonical ggml-org/ggml e91ded11 = v0.23.0)
```

State today (P9 CPU/native checkpoint, 2026-09-14): every layer of the diagram is
built, packaged and proven from the package feed in a clean root
(`tools/llm-clean-root-proof`, evidence in `generated/evidence/llm/`): libggml and
libllama (L2), `libsymoneural-llm.so.1` implementing the designed ABI (L3, `native/src/llm.c`),
`symoneural-llm` — the recorded unit `chat` on port 8802 with `SYM_CHAT_TOKEN`, fail-closed,
over `native.py` (ctypes) — and `symoneural-llm-util` (L4). Generation is BLOCKED on an
external model (none registered); the tokenize/detokenize path is proven end to end.
CUDA is deferred to P7. `P9-CHECKPOINT.md` holds the matrix.

Invariants: `llama-server` is a reference/differential target, never the product
boundary; the product never depends on upstream's bundled WebUI; clients name
models by id (the register resolves files); Anthropic protocol parsing lives in
Python (`claude.py`), never in C; libsymoneural-llm and libsymoneural-api are
separate libraries composed above the native boundary.

Upstream map: `tools/map-llama-upstreams.py` (pin b10809/v0.4.0 2026-09-04; ggml
embedded 0.23.0 sync e91ded11; canonical tree IDENTICAL; vendor/ closure; every
fetch point and its gating option).
