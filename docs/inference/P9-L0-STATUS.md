# P9 — L0 forensic recovery (2026-09-14, HEAD 4b3d7c020)

What exists, what is proven, what is not. Read from disk; nothing below is recalled.

| Stage | Status | Evidence |
| --- | --- | --- |
| LLM SOURCE VERIFIED | PASS | `tools/ingest-tree verify --all`: ggml `e91ded11bdcd` VERIFIED, llama.cpp `5266f24da75d` VERIFIED (0 submodules — the pin store holds the tree; `SRC_URI` says `gitsm` but the committed tree carries the vendored content); triton/vllm VERIFIED, `REFERENCE_ONLY` by recorded ruling |
| L1 ggml ↔ llama.cpp pairing | PASS | `tools/map-llama-upstreams.py` re-run today: llama.cpp `5266f24d` (tags b10809, v0.4.0) → `scripts/sync-ggml.last` = `e91ded11`; canonical ggml present at `e91ded11` (v0.23.0); vendored `ggml/` vs canonical **IDENTICAL** (include/src/cmake/CMakeLists.txt: 0 differing). Design (b) — separately packaged matching ggml — is the recorded ruling (`provider-decisions.json` `pending_collisions[ggml]`, RESOLVED-FOR-LLM). Saved: `generated/evidence/llm/UPSTREAM-MAP.{json,txt}` |
| L2 ggml/libggml BUILD + PACKAGE | PASS, valid at HEAD | recipe unchanged since checkpoint `3c9c7cd26` (mtime 00:04; QA log 01:54, 0 ERROR, 0 QA issues); `symoneural-ggml_0.23.0-r0` ipk: `libggml.so.0`, `libggml-base.so.0`, `libggml-cpu.so.0` (CPU backend linked statically into `libggml.so.0`, no dynamic backend loading); -dev ships `ggml.h gguf.h ggml-backend.h …`, `ggml-config.cmake`, `ggml.pc` |
| L2 llama.cpp/libllama BUILD + PACKAGE | PASS, valid at HEAD | recipe unchanged (mtime 00:04; QA 01:55, 0 ERROR); package `libllama0_b10809-r0` (debian auto-rename of `symoneural-llama-cpp`), `SONAME libllama.so.0`, NEEDED `libggml.so.0 libggml-base.so.0 libstdc++ libm libgcc_s libc`; -dev ships `llama.h llama-cpp.h`, `llama-config.cmake`, `llama.pc` (`-lggml -lggml-base -lllama`) |
| native linkage (§69) | PASS | `tools/check-native-linkage.py` today: libllama defines **0** `ggml_*`, imports **243**; libggml-base defines 550; no RUNPATH into a build tree; API↔LLM independence rule cannot run until L3 exists |
| L3 libsymoneural-llm | NOT STARTED | `Symoneural-LLM/app/native/include/symoneural/llm.h` is a designed v1.0.0 ABI (opaque handles, size-first param structs, negative status codes, model-by-ID via `registry_root`); no `.c`, no recipe, no package |
| L4 symoneural-llm runtime | NOT STARTED | `Symoneural-LLM/app/symoneural_llm/` holds `inference.py` (InferenceService), `backend.py` (Backend protocol + FakeBackend), `claude.py` (Anthropic Messages adapter); 11 unit tests against FakeBackend; no ctypes backend, no service entrypoint, no `pyproject.toml`, no recipe |
| L5 worker/router | NOT TESTED | API registry (`Symoneural-API/app/symoneural_api/units.py`) records unit `chat` on port 8802, supervised by argv, bearer token `SYM_CHAT_TOKEN`; it still says `backed_by=("symoneural-llama-cpp",)` "via llama-server" — the A0 baseline P9 supersedes; that edit is an API-side integration item (touching it invalidates the API's packaged-subtree gate until the API is rebuilt) |
| L6 clean install | NOT STARTED | no LLM packagegroup or image; LLM feed holds the two native ipks + a full python3 set |
| L7 meaningful consumer | BLOCKED — compatible external model unavailable | `acquisition/model-register.json`: LLM row `Qwen2.5-7B-Instruct-Q4_K_M.gguf` state ABSENT; `/home/google/symoneural-models/llm/` empty; no GGUF anywhere outside the repo. The pinned llama.cpp tree ships **vocabulary-only** GGUF test fixtures (`models/ggml-vocab-*.gguf`, no tensors): usable to prove the tokenize/detokenize path through the whole native stack, never generation |
| CUDA variant | DEFERRED TO P7 | ruling `cuda-toolkit-authority` exists (13.4.1); nothing chosen in P9 |
| REPRODUCIBILITY / INTEGRATION | NOT TESTED | — |

Estate-wide `ACQUISITION-STATE` remains FAIL; Common's matrix is unchanged by this phase.
