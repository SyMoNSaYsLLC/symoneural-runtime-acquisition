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

State today: the Python layer exists and is tested against `FakeBackend`
(`Symoneural-LLM/app/symoneural_llm/`, 11 tests); the ABI header is designed
(`native/include/symoneural/llm.h`); libggml and libllama recipes are written
library-only with every network fetch unreachable; the C implementation of
`libsymoneural-llm` (L3) waits for libllama to be built and packaged.

Invariants: `llama-server` is a reference/differential target, never the product
boundary; the product never depends on upstream's bundled WebUI; clients name
models by id (the register resolves files); Anthropic protocol parsing lives in
Python (`claude.py`), never in C; libsymoneural-llm and libsymoneural-api are
separate libraries composed above the native boundary.

Upstream map: `tools/map-llama-upstreams.py` (pin b10809/v0.4.0 2026-09-04; ggml
embedded 0.23.0 sync e91ded11; canonical tree IDENTICAL; vendor/ closure; every
fetch point and its gating option).
