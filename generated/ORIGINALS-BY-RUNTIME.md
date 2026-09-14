# SyMoNeuRaL: the ORIGINAL upstream sources, sectioned by future runtime

Generated 2026-09-14 18:08 EDT from acquisition/source-lock.json, source-manifest.json, component-state.json,
pending-acquisitions.json and tools/audit-workscope.sh (run at the same time). Nothing here was renamed or moved:
every row is an upstream project committed at its pin under `Symoneural-<Runtime>/src/<category>/source/<component>/`
and verified byte-identical to upstream (`tools/ingest-tree verify --all`: 93 of 93).

Build-status vocabulary (audit): PACKAGED = an estate package was produced from this tree in the runtime's build
directory (historical pkgdata; QA/consumer proofs are recorded separately in generated/evidence/); RECIPE, NEVER
PACKAGED = recipe exists, nothing built; STUB = placeholder recipe without a build class; REFERENCE_ONLY /
RETIRED_TO_PROVIDER = acquired and pinned, never built for a target, by recorded ruling.


## Symoneural-API  (16 upstream sources)

Image on disk: `symoneural-image-api-qemux86-64.rootfs-20260914061826.tar.gz`; runtime proofs: `generated/evidence/api/`

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| annotated-doc | gh:fastapi/annotated-doc | 0.0.5 | `ef48d6ad51d2` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| annotated-types | gh:annotated-types/annotated-types | v0.8.0 | `9eb966801382` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| anyio | gh:agronholm/anyio | 4.15.1 | `ffcd1542cd6d` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| certifi | gh:certifi/python-certifi | 2026.07.22 | `f4bc676bc101` | MPL-2.0 | TARGET | PKGDATA EXISTS; NOT QA |
| click | gh:pallets/click | 8.5.0 | `8b19813f2bfc` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| fastapi | gh:fastapi/fastapi | 0.141.1 | `95f8322ee1dc` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| h11 | gh:python-hyper/h11 | v0.16.0 | `1c5b07581f05` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| httpcore | gh:encode/httpcore | 1.0.9 | `98209758cc14` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| httpx | gh:encode/httpx | 0.28.1 | `26d48e0634e6` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| idna | gh:kjd/idna | v3.19 | `03a9a11dd8ae` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| pydantic | gh:pydantic/pydantic | v2.13.5 (also core-v2.46.5) | `001dea020e08` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| sniffio | gh:python-trio/sniffio | v1.3.1 | `ae020e13b98d` | MIT OR Apache-2.0 | TARGET | PKGDATA EXISTS; NOT QA |
| starlette | gh:encode/starlette | 1.6.0 | `4f250d6b8145` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| typing-extensions | gh:python/typing_extensions | 4.16.0 | `f29cd28d8ed7` | PSF-2.0 | TARGET | PKGDATA EXISTS; NOT QA |
| typing-inspection | gh:pydantic/typing-inspection | v0.4.4 | `83d4dbb74fc3` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| uvicorn | gh:encode/uvicorn | 0.52.4 | `8988c23704fc` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |

## Symoneural-Adaptive-Fabric  (1 upstream source)

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| FreeToken | gh:FlashML-org/FreeToken | v0.1.2 | `9db1a39455a3` | Apache-2.0 | TARGET | RECIPE, NEVER PACKAGED |

## Symoneural-Build  (7 upstream sources)

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| autoconf | https://git.savannah.gnu.org/git/autoconf.git | 2.73 | `44d712a26b0e` | GPL-3.0-or-later | RETIRED_TO_PROVIDER | RETIRED_TO_PROVIDER -> O |
| automake | https://git.savannah.gnu.org/git/automake.git | 1.19 | `e82d2d34d462` | GPL-2.0-or-later | RETIRED_TO_PROVIDER | RETIRED_TO_PROVIDER -> O |
| bitbake | https://git.openembedded.org/bitbake | UNTAGGED yocto-6.1_M2-99-g046a90b0e (bitbake 2.19.1) | `046a90b0e9b7` | GPL-2.0-only AND MIT | REFERENCE_ONLY | REFERENCE_ONLY |
| libtool | https://git.savannah.gnu.org/git/libtool.git | 2.6.2 | `309bb53a8adf` | GPL-2.0-or-later AND LGPL-2.1-or-later | RETIRED_TO_PROVIDER | RETIRED_TO_PROVIDER -> O |
| m4 | https://git.savannah.gnu.org/git/m4.git | 1.4.21 | `fe2f13ab9ab9` | GPL-3.0-or-later | RETIRED_TO_PROVIDER | RETIRED_TO_PROVIDER -> O |
| ninja | gh:ninja-build/ninja | 1.13.2 | `3441b633c2fe` | Apache-2.0 | RETIRED_TO_PROVIDER | RETIRED_TO_PROVIDER -> O |
| openembedded-core | https://git.openembedded.org/openembedded-core | UNTAGGED uninative-5.2-753-gfe7a24bc67 (master) | `fe7a24bc6711` | MIT AND GPL-2.0-only | REFERENCE_ONLY | REFERENCE_ONLY |

## Symoneural-CLI  (20 upstream sources)

Image on disk: `symoneural-image-cli-qemux86-64.rootfs-20260914053558.tar.gz`; runtime proofs: `generated/evidence/cli/`

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| anthropic-sdk-python | gh:anthropics/anthropic-sdk-python | v1.5.0 | `eb21a4352015` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| anthropic-sdk-typescript | gh:anthropics/anthropic-sdk-typescript | sdk-v0.125.0 | `135f71e92976` | MIT | REFERENCE_ONLY | REFERENCE_ONLY |
| attrs | gh:python-attrs/attrs | 26.1.0 | `7bfc49e9b22d` | MIT | - | PKGDATA EXISTS; NOT QA |
| cffi | gh:python-cffi/cffi | v2.1.1 | `fd33e7700f0e` | MIT-0 | - | PKGDATA EXISTS; NOT QA |
| cryptography | gh:pyca/cryptography | 50.0.1 | `ffde75a2b594` | Apache-2.0 OR BSD-3-Clause | - | PKGDATA EXISTS; NOT QA |
| docstring-parser | gh:rr-/docstring_parser | 0.18.0 | `87dca55a7b5b` | MIT | - | PKGDATA EXISTS; NOT QA |
| httpx2 | gh:pydantic/httpx2 | v2.12.0 | `71ae23be5448` | BSD-3-Clause | - | PKGDATA EXISTS; NOT QA |
| jiter | gh:pydantic/jiter | v0.17.0 | `2b5ec63e505b` | MIT | - | PKGDATA EXISTS; NOT QA |
| jsonschema | gh:python-jsonschema/jsonschema | v4.26.0 | `a7277432b0f7` | MIT | - | PKGDATA EXISTS; NOT QA |
| jsonschema-specifications | gh:python-jsonschema/jsonschema-specifications | v2025.9.1 | `3b846010c34c` | MIT | - | PKGDATA EXISTS; NOT QA |
| opentelemetry-python | gh:open-telemetry/opentelemetry-python | v1.44.0 | `53a5a40c9604` | Apache-2.0 | - | PKGDATA EXISTS; NOT QA |
| pycparser | gh:eliben/pycparser | release_v3.00 | `77de509f0268` | BSD-3-Clause | - | PKGDATA EXISTS; NOT QA |
| pyjwt | gh:jpadilla/pyjwt | 2.14.0 | `c6fe464b356f` | MIT | - | PKGDATA EXISTS; NOT QA |
| python-multipart | gh:Kludex/python-multipart | 0.0.32 | `238ead62a0bb` | Apache-2.0 | - | PKGDATA EXISTS; NOT QA |
| python-sdk | gh:modelcontextprotocol/python-sdk | v2.2.0 | `9972c21aa420` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| referencing | gh:python-jsonschema/referencing | v0.37.0 | `944ed5a20bc5` | MIT | - | PKGDATA EXISTS; NOT QA |
| rpds-py | gh:crate-py/rpds | v2026.6.3 | `7277eb681f6e` | MIT | - | PKGDATA EXISTS; NOT QA |
| sse-starlette | gh:sysid/sse-starlette | v3.4.11 | `6754ef387da9` | BSD-3-Clause | - | PKGDATA EXISTS; NOT QA |
| truststore | gh:sethmlarson/truststore | v0.10.4 | `0714f72a739d` | MIT | - | PKGDATA EXISTS; NOT QA |
| typescript-sdk | gh:modelcontextprotocol/typescript-sdk | v2 GA 2.0.0 | `cc4b41617ce3` | - | REFERENCE_ONLY | REFERENCE_ONLY |

## Symoneural-Common  (24 upstream sources)

Image on disk: `symoneural-image-common-qemux86-64.rootfs-20260914203500.tar.gz`; runtime proofs: `generated/evidence/common/`

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| accelerate | gh:huggingface/accelerate | 1.15.0+git | `6afc1e5ee217` | Apache-2.0 | TARGET | PKGDATA EXISTS; NOT QA |
| filelock | gh:tox-dev/filelock | 3.32.6 | `4efd93e0482e` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| fsspec | gh:fsspec/filesystem_spec | 2026.7.0 | `9e22b60ea6e9` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| hf-xet | gh:huggingface/xet-core | v1.6.0 | `de71453d952b` | Apache-2.0 | TARGET | PKGDATA EXISTS; NOT QA |
| huggingface-hub | gh:huggingface/huggingface_hub | v1.31.0 | `495b17c85296` | Apache-2.0 | TARGET | PKGDATA EXISTS; NOT QA |
| jinja2 | gh:pallets/jinja | 3.1.6 | `15206881c006` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| markdown-it-py | gh:executablebooks/markdown-it-py | v4.2.0 | `36c5f547144d` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| markupsafe | gh:pallets/markupsafe | 3.0.3 | `297fc8e356e6` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| mdurl | gh:executablebooks/mdurl | 0.1.2 | `596bf1c8752d` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| networkx | gh:networkx/networkx | networkx-3.6.1 | `7530809bfa1e` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| packaging | gh:pypa/packaging | 26.3 | `929fd4b1410a` | Apache-2.0 OR BSD-2-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| psutil | gh:giampaolo/psutil | release-7.2.2 | `9eea97dd6f1d` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| pygments | gh:pygments/pygments | 2.21.0 | `a43b45dcf081` | BSD-2-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| pytorch | gh:pytorch/pytorch | v2.14.0 | `2b3ec3482903` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| pyyaml | gh:yaml/pyyaml | 6.0.3 | `49790e73684b` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| regex | gh:mrabarnett/mrab-regex | 2026.9.10 | `7dd71c15c4fb` | Apache-2.0 AND CNRI-Python | TARGET | PKGDATA EXISTS; NOT QA |
| rich | gh:Textualize/rich | v15.0.0 | `6ac483cbea39` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| safetensors | gh:huggingface/safetensors | v0.8.0 | `a406ca3e7a90` | Apache-2.0 | TARGET | PKGDATA EXISTS; NOT QA |
| setuptools | gh:pypa/setuptools | v84.0.0 | `72e919a8b10a` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| shellingham | gh:sarugaku/shellingham | 1.5.4 | `cba059e7f29f` | ISC | TARGET | PKGDATA EXISTS; NOT QA |
| tokenizers | gh:huggingface/tokenizers | v0.23.2 | `88a4498ad4ea` | Apache-2.0 AND MIT | TARGET | PKGDATA EXISTS; NOT QA |
| tqdm | gh:tqdm/tqdm | v4.70.1 | `9cf5a12b1f95` | MIT AND MPL-2.0 | TARGET | PKGDATA EXISTS; NOT QA |
| transformers | gh:huggingface/transformers | 5.17.0+git | `856157a2f3e9` | Apache-2.0 | TARGET | PKGDATA EXISTS; NOT QA |
| typer | gh:fastapi/typer | 0.27.2 | `99eb220df7c6` | MIT | TARGET | PKGDATA EXISTS; NOT QA |

- BINARY-EXTERNAL inputs (not sources): cuda-toolkit-bin 13.4.1 (NVIDIA EULA), cudnn-bin 9.25.1.1 (NVIDIA SLA; Common only) - pinned by NVIDIA debian13 index sha256.

## Symoneural-Crypto  (3 upstream sources)

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| stratum | gh:stratum-mining/stratum | v1.11.1 | `c1a799139425` | Apache-2.0 AND MIT | TARGET | RECIPE, NEVER PACKAGED |
| sv2-apps | gh:stratum-mining/sv2-apps | v0.7.0 | `d7d556d1a3c7` | Apache-2.0 AND MIT | TARGET | STUB — no build class |
| sv2-spec | gh:stratum-mining/sv2-spec | UNTAGGED (commit pin 67d2178e12b2) | `67d2178e12b2` | BSD-3-Clause OR CC0-1.0 | REFERENCE_ONLY | REFERENCE_ONLY |

- Pending: kawpowminer - DEFERRED to P11 / Phase 20e (GPL-3.0 product/distribution ruling required).

## Symoneural-Live  (1 upstream source)

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| gstreamer | https://gitlab.freedesktop.org/gstreamer/gstreamer.git | 1.28.7 | `070125524a84` | LGPL-2.1-or-later | TARGET | STUB — no build class |

## Symoneural-LLM  (4 upstream sources)

Image on disk: `symoneural-image-llm-qemux86-64.rootfs-20260914133906.tar.gz`; runtime proofs: `generated/evidence/llm/`

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| ggml | gh:ggml-org/ggml | v0.23.0 (= llama.cpp scripts/sync-ggml.last e91ded11) | `e91ded11bdcd` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| llama.cpp | gh:ggml-org/llama.cpp | b10809 (also v0.4.0) | `5266f24da75d` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| triton | gh:triton-lang/triton | v3.8.0 | `c01b6774b186` | MIT | REFERENCE_ONLY | REFERENCE_ONLY |
| vllm | gh:vllm-project/vllm | v0.29.0 | `98dff2a81d74` | Apache-2.0 AND MIT | REFERENCE_ONLY | REFERENCE_ONLY |

- BINARY-EXTERNAL inputs (not sources): cuda-toolkit-bin 13.4.1 (NVIDIA EULA), cudnn-bin 9.25.1.1 (NVIDIA SLA; Common only) - pinned by NVIDIA debian13 index sha256.

## Symoneural-Platform  (1 upstream source)

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| open-gpu-kernel-modules | gh:NVIDIA/open-gpu-kernel-modules | 615.71.09 | `61dcc93722ec` | MIT OR GPL-2.0-only | TARGET | STUB — no build class |

- BINARY-EXTERNAL build inputs (not sources): Debian linux-headers/kbuild/image 6.12.107+deb13-amd64 (6.12.107-1) pinned by sha256 - Debian profile only.

- Pending (NOT ACQUIRED): AWCC v1.19.0 `0ec42c4b3ddc` gh:tr1xem/AWCC - GPL-3.0; rulings open (distribution posture, runtime placement, FetchContent closure, acpi_call module).

- External providers still missing for a fresh-machine GPU: NVIDIA driver userspace (libcuda.so.1 ...) and GSP firmware 615.71.09 - BLOCKED.

## Symoneural-Ravencalc  (12 upstream sources)

Image on disk: `symoneural-image-ravencalc-qemux86-64.rootfs-20260914051529.tar.gz`; runtime proofs: `generated/evidence/ravencalc/`

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| cloudpickle | gh:cloudpipe/cloudpickle | v3.1.2 | `7576fff24b97` | BSD-3-Clause | - | PKGDATA EXISTS; NOT QA |
| cython | gh:cython/cython | 3.2.5 | `ec152091ca7c` | Apache-2.0 | TARGET | RECIPE, NEVER PACKAGED |
| joblib | gh:joblib/joblib | 1.6.0 | `cd9a6b05fc4f` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| mpmath | gh:mpmath/mpmath | 1.3.0 | `b5c04506ef0c` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| narwhals | gh:narwhals-dev/narwhals | v2.26.0 | `e34715d1e9e2` | MIT | TARGET | PKGDATA EXISTS; NOT QA |
| numpy | gh:numpy/numpy | 2.5.3 | `dd88c0c19b54` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| openblas | gh:OpenMathLib/OpenBLAS | 0.3.34 | `e0166008be8e` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| pybind11 | gh:pybind/pybind11 | v3.0.4 | `d03662f0984f` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| scikit-learn | gh:scikit-learn/scikit-learn | 1.9.1 | `866c0f51e756` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| scipy | gh:scipy/scipy | 1.18.1 | `e4e854eaa8f1` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |
| sympy | gh:sympy/sympy | 1.14.0 | `16fa855354eb` | BSD-3-Clause AND MIT | TARGET | PKGDATA EXISTS; NOT QA |
| threadpoolctl | gh:joblib/threadpoolctl | 3.6.0 | `d5bf10bcf90d` | BSD-3-Clause | TARGET | PKGDATA EXISTS; NOT QA |

## Symoneural-Remix  (1 upstream source)

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| librespot | gh:librespot-org/librespot | v0.8.0 | `d36f9f1907e8` | MIT | TARGET | PKGDATA EXISTS; NOT QA |

## Symoneural-Streamer  (1 upstream source)

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| hls.js | gh:video-dev/hls.js | v1.7.3 | `e5ff3583965e` | Apache-2.0 | TARGET | PKGDATA EXISTS; NOT QA |

## Symoneural-Web  (2 upstream sources)

| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |
|---|---|---|---|---|---|---|
| workerd | gh:cloudflare/workerd | v1.20260911.1 | `925464ba9fe5` | Apache-2.0 AND ISC AND MIT | REFERENCE_ONLY | REFERENCE_ONLY |
| workers-sdk | gh:cloudflare/workers-sdk | wrangler@4.131.1 | `00ae21fa8375` | - | REFERENCE_ONLY | REFERENCE_ONLY |


## Planned runtimes without a source directory yet

Named in the estate records as future consumers but with no `Symoneural-<Runtime>/` directory and no acquired source: **Tune** (CuPy / cuda-python), **Diffuse** (diffusers; ComfyUI was rejected: GPL-3.0), **Studio**. Nothing to section for them yet.


## Recorded as NOT ACQUIRED (by ruling)

- ComfyUI: GPL-3.0; replaced by diffusers. NOT ACQUIRED.
- nvidia-ml-py: PyPI sdist, not a git tag - acquired with sdist sha256 in its own phase.
- CUDA Toolkit 13.3 / driver 610.57.04: BINARY / REFERENCE under NVIDIA EULA - not a source acquisition.


Total upstream originals committed: 93. Runtime directories on disk: 14 (13 application/build runtimes + Platform).
