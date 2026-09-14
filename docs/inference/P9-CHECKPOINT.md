# P9 — LLM native reconstruction: CPU/native checkpoint (2026-09-14)

**P9 CPU/NATIVE CHECKPOINT COMPLETE — P7 CUDA AUTHORITY REQUIRED NEXT.**
Generation is BLOCKED on an external model, not on the estate.

Stack proven, top to bottom, from packages installed by opkg into a clean root and run
through the target loader (`tools/llm-clean-root-proof`, transcript
`generated/evidence/llm/LLM-CLEAN-ROOT-PROOF.txt`):

```
symoneural-llm (Python; unit `chat`, :8802, SYM_CHAT_TOKEN)  ──ctypes──►  libsymoneural-llm.so.1
                                                                                 │  sym_llm_* (16 symbols)
                                                                              libllama.so.0  (5266f24d / b10809)
                                                                                 │  243 ggml_* imported, 0 defined
                                                                              libggml.so.0 · libggml-base.so.0 · libggml-cpu.so.0  (e91ded11 / v0.23.0)
```

## Completion matrix

| Row | Status | Evidence |
| --- | --- | --- |
| LLM SOURCE VERIFIED | PASS | `tools/ingest-tree verify --all`: 92/92; ggml `e91ded11bdcd`, llama.cpp `5266f24da75d` VERIFIED |
| L1 ggml ↔ llama.cpp pairing | PASS | `UPSTREAM-MAP.{json,txt}`: `sync-ggml.last` = `e91ded11` = canonical pin; vendored copy IDENTICAL; recorded ruling `pending_collisions[ggml]` RESOLVED-FOR-LLM holds |
| ggml/libggml BUILD · PACKAGE | PASS · PASS | recipe unchanged since `3c9c7cd26`; QA 0 ERROR; `symoneural-ggml_0.23.0-r0` — three `.so.0` with the CPU backend linked statically into `libggml.so.0` |
| llama.cpp/libllama BUILD · PACKAGE | PASS · PASS | QA 0 ERROR; `libllama0_b10809-r0`, SONAME `libllama.so.0`, library only (no server/tools/UI) |
| libsymoneural-llm BUILD · PACKAGE | PASS · PASS | recipe `symoneural-llm` (symoneural-firstparty + cmake + pkgconfig): QA 0 ERROR, 0 QA issues; `symoneural-llm_1.0.0-r0`: `libsymoneural-llm.so.1.0.0` NEEDED exactly `libggml-base.so.0 libllama.so.0 libc.so.6`, no RUNPATH, no build-path bytes, 16 exported symbols all `sym_llm_*`, `SOURCE-TREE == HEAD:Symoneural-LLM/app` |
| symoneural-llm BUILD · PACKAGE | PASS · PASS | recipes `symoneural-llm-python` (flit, `dependencies = []`) and `symoneural-llm-util`: QA 0 ERROR; image `symoneural-image-llm` 4770 tasks all succeeded, 0 ERROR (three consecutive builds) |
| native linkage (§69) | PASS | `NATIVE-LINKAGE.json`: nothing NOT STARTED; libllama defines 0 / imports 243 `ggml_*`; `rule_independent_of_api` PASS; `rule_no_embedded_ggml` PASS; `links_shared_libggml` PASS |
| clean install | PASS | rootfs `rootfs-20260914111643` (40 packages, 841 files, sha256 `bcf2f32e…`), extracted and run with `env -i` through the target `ld.so`; every NEEDED of every native library resolves inside the root; no source tree, no PYTHONPATH, no build frontend |
| runtime/worker path | PASS | `symoneural-llm-util` version 1.0.0 / ABI 65536 / capabilities `text streaming cancellation tokenize cpu`; `symoneural-llm capabilities` reports native 1.0.0 through ctypes; `request --fake` returns an Anthropic-shaped message; the chat unit serves `/api/health` 200, `/v1/models` and `/v1/capabilities` 200 with the token, 401 without or with a wrong one, `/v1/messages` 404 for an unregistered model, refuses to start without `SYM_CHAT_TOKEN` (exit 78), exits 0 on SIGTERM, logs no path |
| tokenize path (partial consumer evidence) | PASS | qwen2 (151936-token) and llama-bpe vocabularies — llama.cpp's tensor-free `models/ggml-vocab-*.gguf` fixtures from the PINNED tree, copied into the throwaway root's registry — load through `gguf.h`/libllama; tokenize → detokenize round-trip equals the input on both; `generate` on a vocabulary is refused (`session_open: EINVAL`) as designed |
| **meaningful consumer (generation)** | **BLOCKED — compatible external model unavailable** | `acquisition/model-register.json`: LLM row `Qwen2.5-7B-Instruct-Q4_K_M.gguf` ABSENT; `/home/google/symoneural-models/llm/` empty; no GGUF weights anywhere outside the repo. Nothing was downloaded, committed or fetched during a build |
| closure / provider ownership | PASS | `check-python-runtime-closures.py --runtime LLM`: 1 direct wheel, 0 runtime requirements, RESULT PASS (`LLM-RUNTIME-CLOSURE.json`); native providers SYMONEURAL-OWNED by recorded ruling; `verify-acquisition.py` CONTROL-PLANE PASS / ESTATE-COMPLETENESS PASS, 0 WARN; `check-determinism.py` identical; `audit-workscope.sh` LLM 4/4 committed · 2/2 packaged |
| pristine / no-hidden-network | PASS | pristine 92/92; every fetch point in llama.cpp/ggml switched off (`UPSTREAM-CLOSURE.md`); the first-party recipes have no `SRC_URI`; the proof's registry contains fixtures only |
| REPRODUCIBILITY | NOT TESTED | no differing-build-root comparison run for LLM |
| INTEGRATION | NOT TESTED | the API's unit registry still records `chat` as `backed_by=("symoneural-llama-cpp",)` "via llama-server" (A0 baseline); updating it is an API-side change that invalidates the API's packaged-subtree gate until the API is rebuilt — recorded, not done in P9 |
| CUDA variant | DEFERRED TO P7 | libggml is CPU-only (`llama_supports_gpu_offload()` false, capabilities say `cpu`); ruling `cuda-toolkit-authority` exists; nothing chosen here |

Estate-wide `ACQUISITION-STATE` remains FAIL (unchanged). Common's matrix is unchanged.

## What the clean-root proof found and fixed

The first proof run against `rootfs-20260914111331` passed the native chain and then
failed at the Python runtime: `http/server.py:95 import html` →
`ModuleNotFoundError`. The image carried `python3-netclient` (the `http` package) but
not `python3-html`. Edge added to `symoneural-llm-python` from oe-core's
`python3-manifest.json` (commit `77c131c5f`); the rebuilt image
(`rootfs-20260914111643`) passes. A stale-extraction cache in
`tools/check-native-linkage.py` (keyed by ipk basename, blind to a rebuilt ipk under
the same `r0` name) produced one false "STALE PACKAGE"; it now honours mtimes.

## Design decisions recorded here

- **Registry, not paths.** `sym_llm_model_load(rt, id)` opens `<registry_root>/<id>.gguf`
  with `^[A-Za-z0-9][A-Za-z0-9._-]{0,126}$` and no `..`. The runtime's `--allowed-models`
  / `SYM_LLM_ALLOWED_MODELS` is the policy over the registry's contents. A request can
  name a model; it cannot name a file or a command.
- **The unit is the recorded architecture.** `units.py` records `chat` as an HTTP unit
  on 8802 with a fixed argv and a bearer token; `symoneural-llm serve` is that, on the
  stdlib HTTP server, with no framework and no Python dependency. `llama-server` is
  reference material only and is not built.
- **Vocabulary-only loading** is a library feature, not a test hack: a GGUF with zero
  tensors is loaded `vocab_only` and supports tokenize/detokenize/model_info; sessions
  refuse it. That is what made a truthful partial proof possible without weights.

## Next

1. **P7** — the CUDA toolkit authority; then `-DGGML_CUDA=ON` in the ggml recipe per
   `UPSTREAM-CLOSURE.md`, `gpu_layers` through the existing ABI, the GPU lock at unit start.
2. **External model** — register a compatible GGUF through the model-register workflow
   (weights external, sha256 recorded); then `tools/llm-clean-root-proof` gains a real
   generation step and the generation row can become PASS.
3. **Integration** — API registry `chat` row → `symoneural-llm`; DispatchOS `allowed_models`
   from the register; API rebuild; INTEGRATION proof.
