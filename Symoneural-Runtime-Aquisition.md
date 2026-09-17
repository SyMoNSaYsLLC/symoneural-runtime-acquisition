# SyMoNeuRaL Runtime Acquisition

> **GENERATED FILE — do not edit.** Rendered by `tools/generate-runtime-acquisition.py`
> from `acquisition/*.json`. Every number below is derived from those records and
> re-asserted against them at render time. To change this report, change the records.

| | |
|---|---|
| Parent HEAD | `6dfbb00b67ce0054096aa2aff5f6ddb1e5757485` |
| Working tree | modified, uncommitted |
| Records | `acquisition/` (15 JSON + SHA256SUMS) |
| Scanner identity | `acquisition/control-plane.json` (20 tools hashed) |
| Determinism verified | YES |
| Tree inventory | `generated/runtime-tree.txt` (32278 dirs) |
| Tree SHA-256 | `7bdda07b5003b08feec6371819893814b605740225386954c88ed351dafa8887` |
| Report self-validation | PASS (10/10 totals re-derived) |

## Verdicts

Two verdicts are tracked separately. The control plane must be trustworthy
before its description of the estate means anything.

| Verdict | Result | Meaning |
|---|---|---|
| **CONTROL-PLANE** | see `tools/verify-acquisition.py` | Can the scanner be trusted to describe the estate? |
| **ACQUISITION-STATE** | **FAIL** | Has the estate resolved its acquisition decisions? |

Acquisition FAIL reasons:

- 97 provider collision(s) unresolved (58 direct-vs-OE-Core)
- 406 vendored decision(s) unresolved
- 574 licence file(s) without an established identifier
- 3 explicit control-plane decisions open (FreeToken/torch, nvidia-userspace-driver-provider, nvidia-gsp-firmware-provider)

This FAIL is expected and is a statement of open decisions, not a defect.


## Repository census

| Method | Count |
|---|---|
| A — filesystem candidate + `git rev-parse` validation | 101 |
| B — independent git work-tree-top census | 101 |
| **Sets identical** | **YES** |

`.git` is accepted as a file or a directory; submodules are excluded from the
top-level set via `--show-superproject-working-tree`, which is representation-independent.


## Build-stack identity

| Component | SHA |
|---|---|
| bitbake | `046a90b0e9b7b914b7a95aec579cdc3fc9c7617a` |
| meta-openembedded | `43b79d8e372c4f69ebab6c85b39d97b41522080f` |
| openembedded-core | `fe7a24bc67118e7e184b5f5247258715e3904e7c` |

This locks the **build stack only**, never the application sources.


## Runtime inventory

| Runtime | Components | Verified | Clean |
|---|---|---|---|
| API | 16 | 16 | 16 |
| Adaptive-Fabric | 1 | 1 | 1 |
| Build | 7 | 7 | 7 |
| CLI | 20 | 19 | 20 |
| Common | 24 | 24 | 24 |
| Crypto | 3 | 3 | 3 |
| Diffuse | 1 | 1 | 1 |
| LLM | 4 | 4 | 4 |
| Live | 1 | 1 | 1 |
| Platform | 8 | 8 | 8 |
| Ravencalc | 12 | 12 | 12 |
| Remix | 1 | 1 | 1 |
| Streamer | 1 | 1 | 1 |
| Web | 2 | 1 | 2 |
| **TOTAL** | **101** | **99** | **101** |

## Top-level source lock

| Runtime | Component | Commit | State | Subs | Recipe |
|---|---|---|---|---|---|
| API | anyio | `ffcd1542cd6d` | VERIFIED | 0 | yes |
| API | certifi | `f4bc676bc101` | VERIFIED | 0 | yes |
| API | h11 | `1c5b07581f05` | VERIFIED | 0 | yes |
| API | httpcore | `98209758cc14` | VERIFIED | 0 | yes |
| API | httpx | `26d48e0634e6` | VERIFIED | 0 | yes |
| API | idna | `03a9a11dd8ae` | VERIFIED | 0 | yes |
| API | sniffio | `ae020e13b98d` | VERIFIED | 0 | yes |
| API | annotated-doc | `ef48d6ad51d2` | VERIFIED | 0 | yes |
| API | annotated-types | `9eb966801382` | VERIFIED | 0 | yes |
| API | pydantic | `001dea020e08` | VERIFIED | 0 | yes |
| API | typing-extensions | `f29cd28d8ed7` | VERIFIED | 0 | yes |
| API | typing-inspection | `83d4dbb74fc3` | VERIFIED | 0 | yes |
| API | click | `8b19813f2bfc` | VERIFIED | 0 | yes |
| API | fastapi | `95f8322ee1dc` | VERIFIED | 0 | yes |
| API | starlette | `4f250d6b8145` | VERIFIED | 0 | yes |
| API | uvicorn | `8988c23704fc` | VERIFIED | 0 | yes |
| Adaptive-Fabric | FreeToken | `9db1a39455a3` | VERIFIED | 0 | yes |
| Build | autoconf | `44d712a26b0e` | VERIFIED | 0 | yes |
| Build | automake | `e82d2d34d462` | VERIFIED | 0 | yes |
| Build | libtool | `309bb53a8adf` | VERIFIED | 2 | yes |
| Build | m4 | `fe2f13ab9ab9` | VERIFIED | 2 | yes |
| Build | bitbake | `046a90b0e9b7` | VERIFIED | 0 | yes |
| Build | openembedded-core | `fe7a24bc6711` | VERIFIED | 0 | yes |
| Build | ninja | `3441b633c2fe` | VERIFIED | 0 | yes |
| CLI | anthropic-sdk-python | `eb21a4352015` | VERIFIED | 0 | yes |
| CLI | anthropic-sdk-typescript | `135f71e92976` | VERIFIED | 0 | yes |
| CLI | cryptography | `ffde75a2b594` | VERIFIED | 0 | yes |
| CLI | pyjwt | `c6fe464b356f` | VERIFIED | 0 | yes |
| CLI | attrs | `7bfc49e9b22d` | VERIFIED | 0 | yes |
| CLI | cffi | `fd33e7700f0e` | VERIFIED | 0 | yes |
| CLI | pycparser | `77de509f0268` | VERIFIED | 0 | yes |
| CLI | httpx2 | `71ae23be5448` | VERIFIED | 0 | yes |
| CLI | python-multipart | `238ead62a0bb` | VERIFIED | 0 | yes |
| CLI | sse-starlette | `6754ef387da9` | VERIFIED | 0 | yes |
| CLI | jiter | `2b5ec63e505b` | VERIFIED | 0 | yes |
| CLI | jsonschema | `a7277432b0f7` | VERIFIED | 0 | yes |
| CLI | jsonschema-specifications | `3b846010c34c` | VERIFIED | 0 | yes |
| CLI | referencing | `944ed5a20bc5` | VERIFIED | 1 | yes |
| CLI | rpds-py | `7277eb681f6e` | VERIFIED | 0 | yes |
| CLI | python-sdk | `9972c21aa420` | VERIFIED | 0 | yes |
| CLI | typescript-sdk | `cc4b41617ce3` | UNRESOLVED | 0 | **none** |
| CLI | opentelemetry-python | `53a5a40c9604` | VERIFIED | 0 | yes |
| CLI | docstring-parser | `87dca55a7b5b` | VERIFIED | 0 | yes |
| CLI | truststore | `0714f72a739d` | VERIFIED | 0 | yes |
| Common | pyyaml | `49790e73684b` | VERIFIED | 0 | yes |
| Common | accelerate | `6afc1e5ee217` | VERIFIED | 0 | yes |
| Common | hf-xet | `de71453d952b` | VERIFIED | 0 | yes |
| Common | huggingface-hub | `495b17c85296` | VERIFIED | 0 | yes |
| Common | pytorch | `2b3ec3482903` | VERIFIED | 65 | yes |
| Common | safetensors | `a406ca3e7a90` | VERIFIED | 0 | yes |
| Common | tokenizers | `88a4498ad4ea` | VERIFIED | 0 | yes |
| Common | transformers | `856157a2f3e9` | VERIFIED | 0 | yes |
| Common | jinja2 | `15206881c006` | VERIFIED | 0 | yes |
| Common | markdown-it-py | `36c5f547144d` | VERIFIED | 0 | yes |
| Common | markupsafe | `297fc8e356e6` | VERIFIED | 0 | yes |
| Common | mdurl | `596bf1c8752d` | VERIFIED | 0 | yes |
| Common | pygments | `a43b45dcf081` | VERIFIED | 0 | yes |
| Common | regex | `7dd71c15c4fb` | VERIFIED | 0 | yes |
| Common | rich | `6ac483cbea39` | VERIFIED | 0 | yes |
| Common | filelock | `4efd93e0482e` | VERIFIED | 0 | yes |
| Common | fsspec | `9e22b60ea6e9` | VERIFIED | 0 | yes |
| Common | networkx | `7530809bfa1e` | VERIFIED | 0 | yes |
| Common | packaging | `929fd4b1410a` | VERIFIED | 0 | yes |
| Common | psutil | `9eea97dd6f1d` | VERIFIED | 0 | yes |
| Common | setuptools | `72e919a8b10a` | VERIFIED | 0 | yes |
| Common | shellingham | `cba059e7f29f` | VERIFIED | 0 | yes |
| Common | tqdm | `9cf5a12b1f95` | VERIFIED | 0 | yes |
| Common | typer | `99eb220df7c6` | VERIFIED | 0 | yes |
| Crypto | stratum | `c1a799139425` | VERIFIED | 0 | yes |
| Crypto | sv2-apps | `d7d556d1a3c7` | VERIFIED | 0 | yes |
| Crypto | sv2-spec | `67d2178e12b2` | VERIFIED | 0 | yes |
| Diffuse | stable-diffusion.cpp | `7f410a3793c5` | VERIFIED | 4 | yes |
| LLM | ggml | `e91ded11bdcd` | VERIFIED | 0 | yes |
| LLM | llama.cpp | `5266f24da75d` | VERIFIED | 0 | yes |
| LLM | triton | `c01b6774b186` | VERIFIED | 0 | yes |
| LLM | vllm | `98dff2a81d74` | VERIFIED | 0 | yes |
| Live | gstreamer | `070125524a84` | VERIFIED | 1 | yes |
| Platform | AWCC | `0ec42c4b3ddc` | VERIFIED | 0 | yes |
| Platform | glfw | `d9d6f0f1f967` | VERIFIED | 0 | yes |
| Platform | imgui | `f1cc2ae15e53` | VERIFIED | 0 | yes |
| Platform | json | `55f93686c015` | VERIFIED | 0 | yes |
| Platform | libusb-cmake | `c8477c10ac2a` | VERIFIED | 0 | yes |
| Platform | loguru | `ba2240d19bae` | VERIFIED | 0 | yes |
| Platform | stb | `2c980bb59875` | VERIFIED | 0 | yes |
| Platform | open-gpu-kernel-modules | `61dcc93722ec` | VERIFIED | 0 | yes |
| Ravencalc | openblas | `e0166008be8e` | VERIFIED | 0 | yes |
| Ravencalc | narwhals | `e34715d1e9e2` | VERIFIED | 0 | yes |
| Ravencalc | cython | `ec152091ca7c` | VERIFIED | 0 | yes |
| Ravencalc | pybind11 | `d03662f0984f` | VERIFIED | 0 | yes |
| Ravencalc | scikit-learn | `866c0f51e756` | VERIFIED | 0 | yes |
| Ravencalc | numpy | `dd88c0c19b54` | VERIFIED | 7 | yes |
| Ravencalc | scipy | `e4e854eaa8f1` | VERIFIED | 8 | yes |
| Ravencalc | mpmath | `b5c04506ef0c` | VERIFIED | 0 | yes |
| Ravencalc | sympy | `16fa855354eb` | VERIFIED | 0 | yes |
| Ravencalc | cloudpickle | `7576fff24b97` | VERIFIED | 0 | yes |
| Ravencalc | joblib | `cd9a6b05fc4f` | VERIFIED | 0 | yes |
| Ravencalc | threadpoolctl | `d5bf10bcf90d` | VERIFIED | 0 | yes |
| Remix | librespot | `d36f9f1907e8` | VERIFIED | 0 | yes |
| Streamer | hls.js | `e5ff3583965e` | VERIFIED | 0 | yes |
| Web | workerd | `925464ba9fe5` | VERIFIED | 0 | yes |
| Web | workers-sdk | `00ae21fa8375` | UNRESOLVED | 0 | **none** |

## Submodule summary

Entries: **90** · identity key `owner_source_path + submodule_path` · unknown URLs: **0**

- AT-RECORDED-COMMIT: 90

## Dependency graph

Declarations discovered from on-disk manifests: **16283**. No depth limit; nothing fetched.

| Classification | Count |
|---|---|
| PACKAGE-MANAGED | 11351 |
| DIRECT-DECLARED | 4443 |
| BUILD-FETCH | 255 |
| WORKSPACE-LOCAL | 144 |
| SUBMODULE | 90 |

| Scope | Count |
|---|---|
| UNKNOWN | 7749 |
| DEV-ONLY | 6220 |
| RUNTIME/SHIP | 1632 |
| DOC-ONLY | 358 |
| BUILD-ONLY | 300 |
| TEST-ONLY | 24 |

A lockfile establishes resolution, not directness: a `Cargo.lock` entry with no
source URL is `WORKSPACE-LOCAL`, never `DIRECT-DECLARED`.


## Vendored register

Entries **406** across **247** logical packages; **45** appear in more than one place.

| Scope | Count |
|---|---|
| UNKNOWN | 347 |
| PRIVATE-VENDORED | 31 |
| TEST-ONLY | 26 |
| DOC-ONLY | 2 |

| Most-duplicated | Copies |
|---|---|
| sub | 23 |
| cmmod | 15 |
| nlohmann | 14 |
| foo | 14 |
| gtest | 10 |
| a | 9 |
| b | 8 |
| sub2 | 7 |

All decisions are `UNRESOLVED`. A test-only vendored library must not be pushed
through the same release path as a runtime-linked one — hence the scope column.


## Provider graph

OE-Core recipes inspected **2760**, providers indexed **2823**, collisions **104**
(of which **58** are direct-acquisition versus an OE-Core recipe).

| | |
|---|---|
| OE-Core recipes inspected | 2760 |
| Providers indexed | 2823 |
| Collisions | 104 |
| Direct-acquisition vs OE-Core | **58** |

| Logical dependency | Direct | OE-Core recipe |
|---|---|---|
| packaging | Common/packaging | python3-packaging 26.3 |
| pybind11 | Ravencalc/pybind11 | python3-pybind11 3.0.4 |
| gstreamer | Live/gstreamer | gstreamer1.0 1.28.7 |
| ninja | Build/ninja | ninja 1.13.2 |
| annotated-doc | API/annotated-doc | python3-annotated-doc 0.0.5 |
| annotated-types | API/annotated-types | python3-annotated-types 0.8.0 |
| anyio | API/anyio | python3-anyio 4.14.2 |
| attrs | CLI/attrs | python3-attrs 26.1.0 |
| autoconf | Build/autoconf | autoconf 2.73 |
| automake | Build/automake | automake 1.19 |
| certifi | API/certifi | python3-certifi 2026.7.22 |
| cffi | CLI/cffi | python3-cffi 2.1.1 |
| click | API/click | python3-click 8.5.0 |
| cloudpickle | Ravencalc/cloudpickle | python3-cloudpickle 3.1.2 |
| cryptography | CLI/cryptography | python3-cryptography UNKNOWN |
| cython | Ravencalc/cython | python3-cython 3.2.9 |
| fastapi | API/fastapi | python3-fastapi 0.141.1 |
| filelock | Common/filelock | python3-filelock 3.32.4 |
| fsspec | Common/fsspec | python3-fsspec 2026.7.0 |
| glfw | Platform/glfw | glfw 3.3.8 |
| h11 | API/h11 | python3-h11 0.16.0 |
| httpcore | API/httpcore | python3-httpcore 1.0.9 |
| httpx | API/httpx | python3-httpx 0.28.1 |
| httpx2 | CLI/httpx2 | python3-httpx2 2.12.0 |
| idna | API/idna | python3-idna 3.19 |
| jinja2 | Common/jinja2 | python3-jinja2 3.1.6 |
| joblib | Ravencalc/joblib | python3-joblib 1.5.3 |
| jsonschema | CLI/jsonschema | python3-jsonschema 4.26.0 |
| jsonschema-specifications | CLI/jsonschema-specifications | python3-jsonschema-specifications 2025.9.1 |
| libtool | Build/libtool | libtool 2.6.2 |
| m4 | Build/m4 | m4 1.4.21 |
| markdown-it-py | Common/markdown-it-py | python3-markdown-it-py 4.2.0 |
| markupsafe | Common/markupsafe | python3-markupsafe 3.0.3 |
| mdurl | Common/mdurl | python3-mdurl 0.1.2 |
| mpmath | Ravencalc/mpmath | python3-mpmath 1.4.1 |
| networkx | Common/networkx | python3-networkx 3.6.1 |
| numpy | Ravencalc/numpy | python3-numpy 2.5.3 |
| psutil | Common/psutil | python3-psutil 7.2.2 |
| pycparser | CLI/pycparser | python3-pycparser 3.0 |
| pydantic | API/pydantic | python3-pydantic 2.13.4 |
| pygments | Common/pygments | python3-pygments 2.21.0 |
| pyjwt | CLI/pyjwt | python3-pyjwt 2.13.0 |
| python-multipart | CLI/python-multipart | python3-python-multipart 0.0.32 |
| pyyaml | Common/pyyaml | python3-pyyaml 6.0.3 |
| referencing | CLI/referencing | python3-referencing 0.37.0 |
| regex | Common/regex | python3-regex 2026.8.31 |
| rich | Common/rich | python3-rich 15.0.0 |
| rpds-py | CLI/rpds-py | python3-rpds-py 2026.6.3 |
| setuptools | Common/setuptools | python3-setuptools 84.0.0 |
| shellingham | Common/shellingham | python3-shellingham 1.5.4 |
| sniffio | API/sniffio | python3-sniffio 1.3.1 |
| starlette | API/starlette | python3-starlette 1.6.0 |
| sympy | Ravencalc/sympy | python3-sympy 1.14.0 |
| tqdm | Common/tqdm | python3-tqdm 4.69.1 |
| typer | Common/typer | python3-typer 0.27.2 |
| typing-extensions | API/typing-extensions | python3-typing-extensions 4.16.0 |
| typing-inspection | API/typing-inspection | python3-typing-inspection 0.4.4 |
| uvicorn | API/uvicorn | python3-uvicorn 0.49.0 |

Provider **existence** is recorded; `selected_provider` stays `UNRESOLVED`.
The scanner exposes choices and does not make architecture decisions.


## Source collisions

Provider kinds indexed: DIRECT-ACQUISITION, OE-CORE-RECIPE, SUBMODULE, VENDORED

| | |
|---|---|
| Logical sources indexed | 395 |
| With more than one provider | **137** |
| INTRA-COMPONENT-DUPLICATE | 116 |
| CROSS-COMPONENT-DUPLICATE | 7 |
| CROSS-RUNTIME-DUPLICATE | 14 |
| DIRECT-VERSUS-OE-CORE | 56 |
| Vendor entries reclassified as SUBMODULE | 66 |
| Duplicate top-level upstream URLs | 0 (invariant) |

| Cross-runtime source | Runtimes | Copies | Kinds |
|---|---|---|---|
| nlohmann | Common, LLM, Platform | 15 | SUBMODULE, VENDORED |
| doctest | Common, Platform | 4 | VENDORED |
| fifo-map | Common, Platform | 4 | VENDORED |
| fuzzer | Common, Platform | 4 | VENDORED |
| hedley | Common, Platform | 4 | VENDORED |
| imapdl | Common, Platform | 4 | VENDORED |
| cpp-httplib | Common, LLM | 3 | SUBMODULE, VENDORED |
| json | Common, Platform | 3 | DIRECT-ACQUISITION, SUBMODULE |
| stb | LLM, Platform | 3 | DIRECT-ACQUISITION, VENDORED |
| tomli | Build, Common | 3 | OE-CORE-RECIPE, VENDORED |
| pocketfft | Common, Ravencalc | 2 | SUBMODULE |
| progressbar | Build, Common | 2 | VENDORED |

A git submodule is a real source copy with its own upstream identity, so
`SUBMODULE` is indexed as a provider kind alongside the others. **Detection only** —
no copy is collapsed, deleted or rewritten; every entry is `UNRESOLVED`.


## Licence inventory

Licence-bearing files: **574**

- NESTED/DEPENDENCY: 454
- TOP-LEVEL: 120

**LICENSE expression and LIC_FILES_CHKSUM coverage are separate concepts.**
This inventory is drift evidence, not a licensing conclusion.


## Artifact capabilities

What each source **natively declares**. No SyMoNeuRaL decision is recorded.

| Capability | Components |
|---|---|
| PYTHON-PACKAGE | 78 |
| PYTHON-EXTENSION | 31 |
| EXECUTABLE | 18 |
| NODE-BUNDLE | 16 |
| RUST-RLIB | 15 |
| RUST-CDYLIB | 11 |
| STATIC-LIBRARY|SHARED-LIBRARY | 11 |
| UNKNOWN | 10 |
| SHARED-LIBRARY | 7 |

## Unresolved decisions

| Category | Identifier | State | Blocks |
|---|---|---|---|
| ARCHITECTURE | FreeToken/torch | OPEN-OWNED-BY-PHASE-19 | Adaptive-Fabric build design |
| BUILD-DESIGN | nvidia-userspace-driver-provider | OPEN | Platform: complete fresh-machine GPU deployment from estate artifacts |
| BUILD-DESIGN | nvidia-gsp-firmware-provider | OPEN | Platform: loading the estate-built nvidia.ko on Blackwell/Ada/Ampere hardware |

### Rulings recorded (not open, still release-relevant)

| Category | Identifier | State | Blocks |
|---|---|---|---|
| VERSION-CONFLICT | sympy-mpmath-constraint | RESOLVED-A | Ravencalc runtime closure PASS (sympy) |
| VERIFICATION | offline-compile | RESOLVED-SCOPED | release build claim |
| LICENCE-POSTURE | kawpowminer-gpl-distribution | DEFERRED | Crypto: Phase 17b GPU miner (kawpowminer 1.2.4) - not P7 |

Derived from the scanner records at render time:

- licence files unresolved: **574**
- provider collisions unresolved: **97**
- vendored decisions unresolved: **406**
- vendor entries reclassified as submodule: **66**

Curated counts as recorded in `unresolved.json` (hand-maintained; may lag the derived figures above):

- artifact decisions pending: **41**
- licence files unresolved: **429**
- provider collisions unresolved: **30**
- source collision decisions unresolved: **73**
- vendor entries reclassified as submodule: **64**
- vendored decisions unresolved: **366**

## Exceptions

| ID | Component | Result | Classification |
|---|---|---|---|
| EXC-001 | symoneural-openblas | SUCCESS rc=0, 984 tasks, 0 errors | EXPLORATORY, OUTSIDE ACQUISITION GATE |
| EXC-002 | symoneural-openblas | SUCCESS rc=0, 773 tasks after adding cross-compile options | EXPLORATORY, OUTSIDE ACQUISITION GATE |

Recorded as history. Neither build is authoritative for release.


## Generated to-do tasks

Open decisions only; ruled items are listed above under *Rulings recorded*.

1. **[ARCHITECTURE] FreeToken/torch** — FreeToken requires torch>=2.11,<2.12; Common holds PyTorch 2.14.0, outside that range.

2. **[BUILD-DESIGN] nvidia-userspace-driver-provider** — No estate provider for the NVIDIA driver userspace ABI (libcuda.so.1, libnvidia-ml.so.1, libnvidia-gpucomp, libnvidia-nvvm, libnvidia-ptxjitcompiler, nvidia-modprobe) at 615.71.09. The Debian profile consumes the host's NVIDIA Debian 13 packages (615.71.09-2; the P7 S2 boundary). The estate profile has none, so a fresh estate machine cannot run CUDA even with the estate-built kernel modules and kernel.

3. **[BUILD-DESIGN] nvidia-gsp-firmware-provider** — No estate provider for the GSP firmware the open kernel modules request at load (nvidia/615.71.09/gsp_tu10x.bin, gsp_ga10x.bin, ucodes_*.bin; modinfo firmware:). Debian profile: firmware-nvidia-gsp 615.71.09-2 from NVIDIA's Debian 13 index (sha256 2f72dd12294aba56...). Estate profile: oe-core linux-firmware ships nouveau-era NVIDIA firmware, not 615.71.09 GSP.

4. **[VERIFICATION] offline-compile** (RESOLVED-SCOPED) — No component demonstrated to compile with no network after bitbake -c fetch. Enumeration is not proof.

5. **[LICENCE-POSTURE] kawpowminer-gpl-distribution** (DEFERRED) — kawpowminer is GPL-3.0 (ethminer lineage). acquisition/pending-acquisitions.json has recorded it since 2026-09-13 with the note that the INCOMPATIBLE_LICENSE posture must be decided before acquisition. P7 C8 confirmed the CUDA authority (13.4.1, sm_120) would serve it; the product/distribution question is separate from P7.

