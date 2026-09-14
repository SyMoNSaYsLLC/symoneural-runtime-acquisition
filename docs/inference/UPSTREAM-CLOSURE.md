# Inference upstream closure

| Component | Upstream | Pin | Role |
|---|---|---|---|
| llama.cpp | https://github.com/ggml-org/llama.cpp | `5266f24da75d` (b10809, v0.4.0) | libllama + llama.h (library only) |
| ggml | https://github.com/ggml-org/ggml | `e91ded11bdcd` (v0.23.0) = llama.cpp `scripts/sync-ggml.last` | libggml; vendored copy proven byte-identical |
| vendor/ in llama.cpp | cpp-httplib, hash (rotate-bits, sha256, xxhash), miniaudio, nlohmann json, sheredom utf8, stb | in-tree, licences listed in the recipe | used by server/tools/examples only — not built |
| triton, vllm | acquired trees | REFERENCE_ONLY (component-state.json) | not built |

Build-time network fetches in the trees and how the library-only build avoids each
(`tools/map-llama-upstreams.py`): `scripts/ui-assets.cmake` WebUI archive
(LLAMA_BUILD_SERVER + LLAMA_USE_PREBUILT_UI → both OFF); `common/` llguidance
ExternalProject (LLAMA_LLGUIDANCE OFF); ggml: KleidiAI FetchContent
(GGML_CPU_KLEIDIAI OFF), CUB 3.2 (GGML_CUDA_CUB_3DOT2 OFF), Windows OpenMP
installer (GGML_OPENMP_FETCH OFF, WIN32 only), Vulkan shader ExternalProject
(GGML_VULKAN OFF), hexagon/virtgpu/zendnn backends (off); cpp-httplib
boringssl/libressl FetchContent (vendor not built); `cmake/download-models.cmake`
(tests/examples off).

CUDA: arrives through the estate toolkit recipe only (ruling
`cuda-toolkit-authority`, 13.4.1); `-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120`
is added to the ggml recipe when that recipe exists — never `/usr/local/cuda`.
