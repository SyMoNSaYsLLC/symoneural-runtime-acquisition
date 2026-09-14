# P7 — the estate CUDA / toolkit authority

Recorded 2026-09-14. Ruling: `acquisition/unresolved.json` → `cuda-toolkit-authority`
(was RESOLVED-DEFAULT at 13.4.1; confirmed below from evidence, not from the default).
Implementation: `meta-symoneural/classes/symoneural-cuda.bbclass`,
`meta-symoneural/recipes-cuda/cuda-toolkit-bin/cuda-toolkit-bin_13.4.1.bb`,
`meta-symoneural/recipes-cuda/symoneural-cuda-probe/`. Component hashes:
`generated/evidence/cuda/CUDA-13.4.1-COMPONENTS.txt`.

## C0 — current CUDA state (read from disk, 2026-09-14)

| Fact | Value | Source |
| --- | --- | --- |
| GPU | NVIDIA GeForce RTX 5070 Ti, GB203, **compute capability 12.0 (sm_120)**, 16303 MiB | `nvidia-smi --query-gpu`, `lspci -nn` (10de:2c05) |
| Driver | **615.71.09**, open kernel module built 2026-09-12; user-space `libcuda.so.615.71.09`, `libnvidia-ml.so.615.71.09` | `/proc/driver/nvidia/version`, `/sys/module/nvidia/version`, `dpkg -l` |
| Host toolkits | `/usr/local/cuda → 13.4` = **13.4.1** (nvcc 13.4.59, cudart 13.4.49, nvrtc 13.4.59), installed from NVIDIA's Debian 13 repo; `/usr/local/cuda-13.3` is a **remnant with no nvcc and no version.json** (only cudart/driver-dev/culibos/nvrtc/gdb-src 13.3 packages remain) | `version.json`, `nvcc --version`, `dpkg -l`, `apt-cache policy` (13.3: not installed, candidate 13.3.1-1) |
| Host cuDNN | none installed | `ls libcudnn*` |
| Estate | no CUDA recipe, class, or package existed; ruling RESOLVED-DEFAULT 13.4.1; `cuda-python` pinned v13.4.1, `cupy` v14.2.0, `fastrlock` v0.8.3 (Tune, unacquired); `kawpowminer` 1.2.4 (Crypto, GPL posture undecided) | `unresolved.json`, `pending-acquisitions.json`, `find meta-symoneural` |

**Host CUDA is evidence, not authority.** Nothing below binds to `/usr/local/cuda-*`.

## C1 — 13.3 vs 13.4 compatibility matrix

| Discriminator | CUDA 13.3 | CUDA 13.4.1 | Verdict |
| --- | --- | --- | --- |
| Driver generation (615.71.09) | 13.3 shipped with driver 610.57.04 (the stale `not_acquired` row records exactly that pairing) | 615.71.09 is the 13.4-generation driver; 13.4.1 user-space runs on it today (`nvidia-smi` answers) | **13.4** — provable now; 13.3 not empirically provable without its toolkit |
| Blackwell sm_120 | supported (13.0+) — inferred | `nvcc --list-gpu-arch` lists `compute_120`, `compute_121` — verified | tie (13.4 verified) |
| Pinned PyTorch 2.14 (`5266f24d` era tree) | never appears in `.ci`/`.github` | minimum CUDA 12.6; `install_134` in `.ci/docker/common/install_cuda.sh`; periodic job `linux-jammy-cuda13.4-py3.10-gcc11`; `12.0`/`12.0a` in every arch table; cutlass 4.6.1 gates `CUTLASS_ARCH_MMA_SM120` natively | **13.4** — upstream-exercised at the pin |
| Host compiler: estate GCC **16.2** (the only GCC in oe-core) | bound **unverifiable offline** (cuda-crt-13-3 not on host; torch's table for 13.0 says `< 16`) | `crt/host_config.h`: `#if __GNUC__ > 16 … unsupported` → **GCC 16 accepted**, no `-allow-unsupported-compiler` needed | **13.4** — verified; 13.3 would be a risk carried on faith |
| Pinned llama.cpp/ggml (`e91ded11`) | `ggml-cuda/CMakeLists.txt`: ≥ 12.8 → `120a-real`; ≥ 13 drops 50/61/70 virtuals | same | tie |
| Tune pins | `cuda-python` v13.4.1 tracks CUDA 13.4 → mismatch | matches | **13.4** |
| Triton 3.8.0 (REFERENCE_ONLY, not built) | bundles `ptxas-blackwell 13.3.33`, `cupti-blackwell 13.3.35` (its own binaries, independent of the system toolkit) | — | 13.3-side datum, **non-binding** |
| Crypto kawpowminer 1.2.4 | 2021-era CMake/CUDA; risk with any 13.x; GPL-3.0 posture undecided (Phase 20e) | same | not a discriminator |
| Reproducible provider path | in the local NVIDIA Debian 13 index with SHA256s (13.3.1-1) | in the same index (13.4.1-1); the runfile the old ruling assumed did not exist at torch's pin date (`install_134` says so) — the repo `.deb`s are the reproducible artefacts | tie on availability |

## C2 — decision

**CUDA 13.4.1.** Four verified discriminators (driver generation, pinned-torch CI,
GCC 16 host-compiler support, cuda-python pin) against one non-binding datum
(Triton's bundled 13.3 ptxas, reference-only). Not chosen for being newer; 13.3 not
rejected for being historical — rejected because the estate cannot verify its
host-compiler bound and no pinned consumer exercises it.

## C3 — provider / acquisition policy

- **One authority.** `symoneural-cuda.bbclass` is the only way a recipe reaches
  CUDA: `DEPENDS cuda-toolkit-bin cuda-toolkit-bin-native`; nvcc from the native
  sysroot; headers/libraries from the target sysroot; host compiler = the estate's
  cross g++; `CMAKE_CUDA_ARCHITECTURES=120`. No consumer names a host path.
- **BINARY_EXTERNAL.** 33 NVIDIA Debian 13 packages (2.13 GB), each pinned by the
  SHA256 the repository index publishes; index identity recorded. No source-built
  claim. Licence `LicenseRef-NVIDIA-CUDA-EULA`; the EULA text is checked against the
  copy inside `cuda-documentation-13-4` (md5 `a3c52c1f…`) and committed at
  `meta-symoneural/files/custom-licenses/`.
- **S2 driver posture.** `libcuda.so.1` and `libnvidia-ml.so.1` are host-driver
  provided at run time and are `PRIVATE_LIBS`; only link-time stubs ship. The driver
  is an external proprietary condition and is reported as such.
- **Layout.** The toolkit tree stays whole under `/usr/local/cuda-13.4` (NVIDIA's own
  layout, what `FindCUDAToolkit` expects); runtime `.so.*` are moved onto `${libdir}`
  with relative links back, so consumers carry no RUNPATH and a clean root resolves
  them on the default loader path. Debian's `ld.so.conf.d` drop-ins are not carried.
- **QA.** Vendor-binary skips are named per package (`already-stripped ldflags textrel
  arch file-rdeps`, plus dev-only `dev-so staticdev dev-elf libdir`); **buildpaths is
  not skipped**.
- **Not in the authority:** cuDNN, NCCL, cuSPARSELt, NVSHMEM (available in the same
  index — cuDNN 9.25.1.1/9.26.0.51, NCCL 2.31.2+cuda13.4). They are separate
  BINARY_EXTERNAL decisions for C7; the toolkit recipe does not pull them.

## C6 — the LLM CUDA consumer against the authority (2026-09-14)

**Result: PASS at the backend level; GPU inference on a real model stays BLOCKED on
external model availability (the P9 exception, unchanged).**

What was built. `symoneural-ggml` gained `PACKAGECONFIG[cuda]` (`-DGGML_CUDA=ON`,
`GGML_CUDA_CUB_3DOT2=OFF`) and inherits `symoneural-cuda` — nothing in the recipe names
a toolkit path, a version or an architecture; all of that is the class. The first build
of it exposed a shape problem, fixed before anything was accepted:

- **Static backend registration made the whole stack driver-dependent.** With the CUDA
  backend compiled into the registry, `libggml.so.0` NEEDs `libggml-cuda.so.0`, which
  NEEDs `libcuda.so.1`. Under the target loader with the host's `ld.so.cache`
  inhibited, `symoneural-llm-util` exited 127 before `main`: not "no GPU", but no
  libsymoneural-llm at all on a machine without the driver. The earlier CPU-mode proof
  had hidden this by letting the target loader fall through to the host cache
  (`/lib/x86_64-linux-gnu/libcuda.so.1`), which was a harness gap as well.
- **Fix: backends are dlopen'ed modules** (`GGML_BACKEND_DL=ON`,
  `GGML_BACKEND_DIR=/usr/lib/ggml`), the mechanism upstream ships its own binaries
  with. `libggml.so.0` NEEDs no backend. `libggml-cpu.so` lives in `symoneural-ggml`;
  `libggml-cuda.so` is its own package `symoneural-ggml-cuda`, so the S2 boundary and
  the `cuda-toolkit-bin` dependency stop at one package and the CPU composition is the
  same image minus that package. The packagegroup names it explicitly (the image sets
  `NO_RECOMMENDATIONS`; the manifest is the install record).
- **libsymoneural-llm 1.1.1** loads the modules once per process from the directory
  next to itself (`dladdr` → `<dir>/ggml`) before anything asks the registry. llama's
  own `ggml_backend_load_all` (compiled-in dir, executable dir, **cwd**) runs only when
  nothing is registered yet, so it never runs while the packages are intact. A module
  whose dependencies are missing simply fails to dlopen. `capabilities` now says
  `gpu:CUDA` / `cpu` / `backend:none` for what this process can see. ABI 1.1 unchanged
  (`abi_version` 65793 = 1.1.1).

Evidence (all from packages, through the target loader, `env -i`, host cache inhibited):

| Item | Value |
|---|---|
| build | `symoneural-image-llm`: 4802 tasks, 0 ERROR; 3 pre-existing WARNINGs (CLOSED licence on symoneural-api, shared sstate dir), none QA |
| image | `symoneural-image-llm-qemux86-64.rootfs-20260914133906.tar.gz`, 1,258,934,760 B, sha256 `55fd6fb3203da786483a2d3f5b70dc03385efab4a3ccf016882c85a6445d554e`, 42 packages (`+symoneural-ggml-cuda`) |
| symoneural-ggml | 612,010 B: `libggml.so.0.23.0` 42,992 B, `libggml-base.so.0.23.0` 649,512 B, `ggml/libggml-cpu.so` 838,152 B |
| symoneural-ggml-cuda | 40,316,162 B: `ggml/libggml-cuda.so` 63,468,088 B, 143 sm_120 SASS; NEEDED `libggml-base.so.0 libcudart.so.13 libcublas.so.13 libcuda.so.1 libstdc++.so.6 libm.so.6 libgcc_s.so.1 libc.so.6`; RDEPENDS `cuda-toolkit-bin (>= 13.4.1)` |
| class S2 QA (`symon_cuda_qa_s2`) | "22 NEEDED entries resolved by providers; host-driver libraries used: libcuda.so.1" — `libcuda.so.1` is the only NEEDED without a package provider, in the one module allowed to have it |
| linkage audit | PASS — `libsymoneural-llm.so.1` NEEDED `libggml.so.0 libggml-base.so.0 libllama.so.0 libc.so.6`; no driver library anywhere in the chain except the cuda module (`generated/evidence/llm/NATIVE-LINKAGE.json`) |
| proof, CPU mode | **PASS** — modules present `libggml-cpu.so libggml-cuda.so`; `libggml.so.0 NEEDs no backend`; only `libggml-cpu.so` loaded; `capabilities … cpu`; **no file mapped from outside the root**; chat unit PASS (`generated/evidence/llm/LLM-CLEAN-ROOT-PROOF.txt`) |
| proof, S2 mode | **PASS** — same image; both modules loaded; `gpu:CUDA` (driver 615.71.09); host files mapped: `libcuda.so.1`, `libnvidia-gpucomp`, `libnvidia-nvvm70`, `libnvidia-ptxjitcompiler`, each owned by a package at 615.71.09; chat unit PASS; `/v1/capabilities` → `gpu:CUDA` (`generated/evidence/cuda/LLM-CLEAN-ROOT-PROOF-S2.txt`) |
| probe proof re-run | PASS under the same inhibited-cache rule (`generated/evidence/cuda/CUDA-CLEAN-ROOT-PROOF.txt`) |
| GPU inference | **BLOCKED** — `gpu_layers > 0` on a real model needs weights the estate does not hold; `sym_llm_runtime_open` refuses `gpu_layers != 0` when no GPU backend is loaded (`EBACKEND`), which is now a runtime fact, not a build fact |

Not done here, recorded: the API registry's chat row still says `symoneural-llama-cpp`
"via llama-server" (integration work, not P7); a CPU-only image composition is
possible (packagegroup without `symoneural-ggml-cuda`, ggml `PACKAGECONFIG = ""`) but
was not built — the P9 CPU checkpoint image remains the CPU evidence.

## C7 — PyTorch CUDA / distributed feature set (built and proven 2026-09-14)

**Result: PASS.** `symoneural-pytorch` 2.14.0 (pin `2b3ec34829036a65cd9d1398ea72a0167dc37470`) is
built through the authority with the feature set Garrett decided, packages QA-clean, and its
CUDA path runs on the RTX 5070 Ti from the Common image in the clean-root proof. Accelerate's
`prepare()` path, the reason it was DEFERRED, passes on this torch in both proof modes.

Decision (Garrett): `USE_CUDA=1` for sm_120; cuDNN as a **separate** BINARY_EXTERNAL provider;
`USE_DISTRIBUTED=1` with Gloo; every optional NVIDIA library off unless a real consumer needs it.

| Knob | Value | Note |
|---|---|---|
| CUDA | `USE_CUDA=1`, `TORCH_CUDA_ARCH_LIST=12.0` (class `SYMON_CUDA_ARCH_DOTTED`) | torch emits sm_120 plus arch-specific `sm_120a`/`sm_121a` objects for a few kernels: `libtorch_cuda.so` holds 419 sm_120 + 1 sm_121a |
| cuDNN | `USE_CUDNN=1`, `USE_STATIC_CUDNN=0`, `cudnn-bin` 9.25.1.1 | torch CI pairs CUDA 13.4 with cuDNN 9.25.0.15 (`install_cuda.sh install_134`); the index offers 9.25.1.1 and 9.26.0.51; 9.25.1.1 is the smallest on that line. Three debs (runtime 432 MB, dev, headers) by index SHA256; NVIDIA SDK licence agreement (md5 `6309a40f…`) committed as `LicenseRef-NVIDIA-cuDNN-SLA`; NEEDED only libz + toolchain, no S2 library |
| Distributed | `USE_DISTRIBUTED=1`, `USE_GLOO=1`; `USE_TENSORPIPE=0 USE_MPI=0 USE_UCC=0` | c10d + Gloo is what accelerate imports; RPC transport is not a consumer need |
| Optional NVIDIA libs | `USE_NCCL=0 USE_CUSPARSELT=0 USE_CUDSS=0 USE_CUFILE=0 USE_NVSHMEM=0 USE_MAGMA=0` | one-GPU estate; none acquired |
| Profiler | `USE_KINETO=1`, `USE_CUPTI_SO=1` | CUPTI from `cuda-toolkit-bin` (`libcupti.so.13`); configure: "Using Kineto with CUPTI support" |
| Attention | flash / mem-efficient ON (torch defaults) | torch's own kernels, not NVIDIA libraries |
| Build type | Release, `MAX_JOBS=12` | compile 10:26→11:45 first pass; accepted build finished 14:08 |

How CUDA reaches torch's PEP 517 build (`scikit_build_core.build`; no cmake class):
`cmake/EnvVarForwarding.cmake` forwards every `USE_*`/`BUILD_*`/`CMAKE_*` environment variable
as a forced cache variable and passes `CUDNN_ROOT/CUDNN_INCLUDE_DIR/CUDNN_LIBRARY`,
`TORCH_CUDA_ARCH_LIST`, `CUDACXX`, `CUDAHOSTCXX` through by name, so the matrix is exports.
The class supplies `CUDACXX`, `CUDAHOSTCXX` (the sysroot/tune/LDFLAGS wrapper, now written by a
`do_configure` prefunc), `CUDAFLAGS`, `CUDA_HOME`, and — for torch's vendored legacy FindCUDA,
which never derives `CUDA_TOOLKIT_TARGET_DIR` from a pre-set root when cross-compiling for
x86_64 — its documented inputs `CUDA_PATH` and `CUDA_NVCC_EXECUTABLE`; `SYMON_CUDA_CMAKE_ARGS`
adds the explicit compiler/host-compiler/root defines to `CMAKE_ARGS`.

| Evidence | Value |
|---|---|
| configure | `log.do_compile.1037712`: `CUDA nvcc is: <native sysroot>/usr/local/cuda-13.4/bin/nvcc`; `Found CUDNN: <target sysroot>/usr/lib/libcudnn.so`; `Using Kineto with CUPTI support`; summary block in `generated/evidence/cuda/TORCH-CUDA-CONFIGURE.txt` |
| package | `symoneural-pytorch_2.14.0-r0_x86-64-v3.ipk` 208,784,028 B sha256 `8c010d753e4c4209c2962ba19c02abb0f27e5b4fe36bec3e4a47fe08d39134de`; Depends `cuda-toolkit-bin (>= 13.4.1), cudnn-bin (>= 9.25.1.1), …` (`generated/evidence/cuda/TORCH-CUDA-PACKAGE.txt`) |
| QA | `do_package_qa` PASS (`log.do_package_qa.1409652`) with the fail-closed S2 check: "98 NEEDED entries resolved by providers; host-driver libraries used: libcuda.so.1"; buildpaths and rpaths NOT skipped |
| libraries | every `torch/lib/*.so`: RPATH `$ORIGIN`, 0 build-path strings; `libtorch_cuda.so` NEEDED `libcudart.so.13 libcusparse.so.12 libcufft.so.12 libcurand.so.10 libcublas.so.13 libcublasLt.so.13 libcudnn.so.9 libnvrtc.so.13 …` — no direct `libcuda.so.1` |
| image | `symoneural-image-common-qemux86-64.rootfs-20260914203500.tar.gz` 2,057,617,376 B sha256 `464dab39b9b19a7fc1a352cabeb041ba8d16fb25acf28bf9d2e134070e4e2266`, 131 packages incl. `cuda-toolkit-bin`, `cudnn-bin`, `symoneural-accelerate`, `symoneural-psutil` (`generated/evidence/common/COMMON-IMAGE-C7.txt`) |
| proof, CPU mode | **PASS** — build facts (`torch.version.cuda` 13.4, cuDNN 92501, gloo available, NCCL absent), `torch.cuda.is_available()` False, `Accelerator(cpu).prepare()` + one SGD epoch changed the weights; **no file mapped from outside the root** (`generated/evidence/common/COMMON-CLEAN-ROOT-PROOF.txt`) |
| proof, S2 mode | **PASS** — `NVIDIA GeForce RTX 5070 Ti cc 12.0: is_available True, matmul on device == CPU reference, cuDNN 92501 conv2d == CPU reference, runtime 13.4`; `Accelerator(cuda).prepare()` + one SGD epoch; host files mapped: `libcuda.so.1`, `libnvidia-ml.so.1`, `libnvidia-gpucomp`, `libnvidia-nvvm70`, `libnvidia-ptxjitcompiler` — all owned by packages at 615.71.09 (`generated/evidence/cuda/COMMON-CLEAN-ROOT-PROOF-S2.txt`) |
| closure | `check-python-runtime-closures.py --runtime Common`: 66 direct requirements PASS (direct wheels only; not an image consumer proof) |
| provenance (build side) | accepted build's CMake cache and `torch_cuda` link line: C/C++ compiler `recipe-sysroot-native/usr/bin/x86_64-oe-linux/x86_64-oe-linux-g++`, nvcc `recipe-sysroot-native/usr/local/cuda-13.4/bin/nvcc`, host compiler = the class wrapper (cross g++ `--sysroot=<recipe-sysroot> -m64 -march=x86-64-v3 …`), toolkit root/include and cudart/cublas/cufft/curand/cusparse from `recipe-sysroot/usr/local/cuda-13.4`, cuDNN from `recipe-sysroot/usr/lib/libcudnn.so`; `libcudart.so`/`libnvrtc.so`/`libcupti.so` link inputs came from the NATIVE sysroot's copy of the same debs (byte-identical to the target copies: sha256 `a77eeb711d35…`, `4eef3c9523c2…`). No `/usr/local/cuda-*`, `/usr/lib/x86_64-linux-gnu` or `/usr/include` host path appears in the cache or the 33 toolkit references of the configure log. The host does hold CUDA 13.4 and 13.3 toolkits at `/usr/local/cuda-*`; they were not inputs |
| provenance (run side) | the proof body prints and asserts its own inputs: interpreter and `torch/__init__.py` under the root; `libpython3.14.so.1.0`, `libtorch_cuda.so`, `libtorch_cpu.so`, `libc10_cuda.so`, `libcudart.so.13.4.49`, `libcudnn.so.9.25.1`, `libcublas.so.13.7.0.27` mapped from the root (`/proc/self/maps`); `PATH` confined to the root; `shutil.which("nvidia-smi")` → not found; in S2 mode `libcuda.so.615.71.09` from the host — the declared exception. Per-process loader traces: the body process maps 104 root libraries + the 5 driver files (S2) or 0 host files (CPU); the one spawned child goes through the wrapper's host `/bin/sh` then the target loader. Host has no torch and runs Python 3.13; the image runs 3.14 |
| negative control | CPU mode asserts `torch.cuda.is_available()` is False with the driver directory absent from the loader path (no host change of any kind); S2 mode is **estate-built userspace tested against an identified external host driver** (615.71.09, packages `libcuda1`, `libnvidia-ml1`, `libnvidia-gpucomp`, `libnvidia-nvvm704`, `libnvidia-ptxjitcompiler1` at 615.71.09-2) |
| artifacts | `generated/evidence/cuda/CUDA-SHA256SUMS` (24 rows: C6 + C7 packages, images, manifests, transcripts) |
| REPRODUCIBILITY | **NOT TESTED** — same build directory and shared sstate; no differing-root build |
| INTEGRATION | **NOT TESTED** |

Accelerate: `unresolved.json:accelerate-torch-distributed` RESOLVED BY EVIDENCE;
`component-state.json` accelerate DEFERRED → TARGET; back in `packagegroup-symoneural-common`.
Boundary note found by the proof: `accelerate.utils.environment.get_gpu_info()` shells out to
`nvidia-smi` (driver userspace, not shipped in the image); the `Accelerator` path proven here
does not call it. The proof harness now confines `PATH` to the root, because with `PATH`
unset Python's `shutil.which` fell back to the host's `/usr/bin` and ran the host `nvidia-smi`.

## C8 — Crypto / Tune compatibility (confirmed from records; nothing pulled forward)

| Consumer | Pin | Against 13.4.1 | Status |
| --- | --- | --- | --- |
| Tune `cuda-python` | v13.4.1 (`0770ab6c`) | version tracks CUDA 13.4 exactly; needs the authority's headers/runtime | COMPATIBLE — acquisition still pending (licence to characterise from the tree) |
| Tune `cupy` | v14.2.0 (`dc1552a3`) | CuPy 14 publishes CUDA 13 builds; needs estate nvcc + NumPy + fastrlock | COMPATIBLE BY UPSTREAM RELEASE LINE — tree not on disk; characterise at acquisition |
| Tune `fastrlock` | v0.8.3 | Cython, CUDA-independent | NOT AFFECTED |
| Tune `nvidia-ml-py` | sdist, pin/hash pending | needs host `libnvidia-ml.so.1` (S2), toolkit-independent | NOT AFFECTED by the version choice |
| Crypto `kawpowminer` | 1.2.4 (`8bd0d598`) | 2021-era CUDA code; a 13.x-generic port risk, not a 13.3-vs-13.4 one; **GPL-3.0 posture undecided (Phase 20e)** | BLOCKED on the licensing decision — a business decision, not made here |
| Adaptive-Fabric `FreeToken`/`flashlib` | held by `unresolved.json:FreeToken/torch` | torch `>=2.11,<2.12` vs estate 2.14 — unrelated to CUDA version | BLOCKED by its own ruling |

## What the first builds taught (fixed, each in the recipe or class)

1. `-dev` doubled as a shared-library provider through the SONAME links left in the
   toolkit tree, and the payload came out owned by uid 1000 (the fetcher's
   `--no-same-owner`), which breaks the sstate output hash. The whole `.so.N` chain now
   moves onto `${libdir}`, the tree keeps relative links, `-dev` is excluded from
   provider scanning (`EXCLUDE_PACKAGES_FROM_SHLIBS`), and `${D}` is `chown -R root:root`.
2. OE stages only `SYSROOT_DIRS`; the toolkit lives under `/usr/local`, so both
   variants add it (`SYSROOT_DIRS`, `SYSROOT_DIRS_NATIVE`).
3. `EXTRA_OECMAKE` cannot carry a multi-token `CMAKE_CUDA_FLAGS`; the CUDA variables
   go into OE's generated toolchain file.
4. `-Xcompiler` flags reach g++ only when compiling; nvcc's final link ran the cross
   g++ without `--sysroot` (`cannot find Scrt1.o … -lc`). nvcc now drives a generated
   wrapper that prepends sysroot, tune and OE `LDFLAGS` on every call — which is also
   what gives CUDA-linked executables GNU_HASH/RELRO for the `ldflags` QA.
5. `SKIP_FILEDEPS` on the runtime package removed the `FILERPROVIDES` that consumers'
   `file-rdeps` QA consults; it now applies to `-dev` only.
6. `file-rdeps` honours only its hardcoded ignores, RPROVIDES and `INSANE_SKIP` — not
   `PRIVATE_LIBS` — and `libcuda.so.1` has no package provider by design (S2). The class
   therefore skips `file-rdeps` for the consumer package and replaces it with
   `symon_cuda_qa_s2`, which walks every ELF in every package and fails on any NEEDED
   that is neither the S2 pair (`libcuda.so.1 libnvidia-ml.so.1`) nor a shlibs provider.
7. `ld` follows transitive DT_NEEDED when linking an executable, so anything linked
   against a CUDA-linked library needs `libcuda.so` at link time. `cuda-toolkit-bin`
   stages NVIDIA's link-time stubs into the *target sysroot only*
   (`SYSROOT_PREPROCESS_FUNCS`); they are never packaged, and the proofs confirm the
   runtime `libcuda.so.1` comes from the driver.
8. A statically registered GPU backend turns "GPU optional" into "driver required to
   load" for the whole stack. ggml backends are dlopen'ed modules (C6); and the
   clean-root harnesses now pass `--inhibit-cache` to the target loader in every mode,
   so the host's `ld.so.cache` can no longer quietly satisfy a NEEDED.

9. torch does `string(APPEND CMAKE_CUDA_FLAGS …)` on the NORMAL variable before it enables the
   CUDA language, which shadows the cache entry CMake seeds from `CUDAFLAGS`: the first C7 build
   compiled every kernel without prefix maps (524 `__FILE__` strings in `libtorch_cuda.so`).
   torch's own channel for extra nvcc flags is `TORCH_NVCC_FLAGS`; the recipe exports the class's
   host flags through it. Control: ggml's CUDA module, built through the same class, had 0.
10. Gloo configures before torch appends `TORCH_NVCC_FLAGS` and snapshots the flags without the
   maps (four Gloo paths left in `libtorch_cuda.so`). A recipe-generated
   `CMAKE_PROJECT_gloo_INCLUDE` hook appends the flags inside Gloo's project scope (Codex, 2026-09-14).
11. torch sets `CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE` unconditionally, so every CUDA-linked
   library is installed with RPATH `$ORIGIN:<sysroot dirs>`. The recipe rewrites it to `$ORIGIN`
   with chrpath after the wheel install and re-checks the DYNAMIC TAGS (not chrpath's text, whose
   echoed filename contains the build path and made the first re-check a false failure).
12. torch's vendored legacy `FindCUDA` never derives `CUDA_TOOLKIT_TARGET_DIR` from a pre-set root
   when cross-compiling for x86_64, and its cache-reset logic discards pre-set target vars on a
   fresh configure; its documented inputs `CUDA_PATH` and `CUDA_NVCC_EXECUTABLE` (now exported by
   the class) make the include/library probes deterministic and keep the fallback off host paths.
13. `symon_cuda_qa_s2` discarded a nonzero `readelf` status and counted unique driver names
   instead of entries; a failed inspection is now fatal and the provider-resolved count subtracts
   every S2 entry (Codex's reproduction and tests, `tools/test-estate-operators.py::CudaBoundaryQa`).

Running the proofs: the Claude Code sandbox hides `/dev/nvidia*`, so
`tools/cuda-clean-root-proof` and `SYM_CUDA_S2=1 tools/llm-clean-root-proof` must run
outside it (`cudaGetDeviceCount: no CUDA-capable device is detected` otherwise); the
CPU-mode LLM proof does not touch the device.

## Status (updated as C4–C10 land)

| Row | Status |
| --- | --- |
| C0 recover · C1 matrix · C2 decision · C3 policy | DONE (this document) |
| C4 one recipe/sysroot authority | **PASS** — `cuda-toolkit-bin` 13.4.1 (runtime 1.10 GB) + `-dev` (1.26 GB) + native variant; `do_package_qa` 0 ERROR / 0 issues (buildpaths not skipped); 33 debs fetched by the SHA256s the index publishes |
| C5 sm_120 low-level compile + run | **PASS** — `symoneural-cuda-probe`: nvcc-native, cross g++ 16.2 host compiler, `--generate-code=arch=compute_120,code=[compute_120,sm_120]`; binary NEEDED `libcudart.so.13 libstdc++ libgcc_s libc`, no RUNPATH, GNU_HASH, 0 build-path bytes; run from packages through the target loader: **RTX 5070 Ti cc 12.0, runtime 13040 == driver 13040, saxpy n=1048576 max_abs_err 0**. Host files mapped: `libcuda.so.1` + three driver helpers, all owned by packages at 615.71.09 (S2). `generated/evidence/cuda/CUDA-CLEAN-ROOT-PROOF.txt` |
| C6 LLM CUDA consumer | **PASS** at the backend level — ggml CUDA backend as a dlopen'ed module (`symoneural-ggml-cuda`), 143 sm_120 SASS, S2 QA clean; libsymoneural-llm 1.1.1 reports `gpu:CUDA` with the driver and `cpu` without it from the same image; GPU inference on a real model BLOCKED on external weights (see C6) |
| C7 PyTorch CUDA/distributed matrix · accelerate | **PASS** — feature set built through the authority + `cudnn-bin`; QA clean with fail-closed S2 check; Common image proven in CPU and S2 modes; `Accelerator.prepare()` PASS on GPU and CPU → ruling RESOLVED BY EVIDENCE (see C7) |
| C8 Crypto/Tune compatibility | recorded — cuda-python 13.4.1 and cupy compatible by release line; **kawpowminer DEFERRED by Garrett's ruling to P11 / Phase 20e** (GPL-3.0 product/distribution ruling required; `unresolved.json:kawpowminer-gpl-distribution`); nothing pulled forward |
| C9 package / clean-install / host-leakage | PASS for the authority + probe, the LLM image and the Common image (all proofs run with the host loader cache inhibited and `PATH` confined to the root; CPU modes map nothing from outside the root; S2 modes map only files owned by packages at the installed driver version) |
| C10 records / evidence / commits | records for C0–C7 in place (`cuda-toolkit-authority` RESOLVED, `cuda-toolkit` BINARY-EXTERNAL, `accelerate-torch-distributed` RESOLVED BY EVIDENCE, `kawpowminer-gpl-distribution` DEFERRED); `generated/evidence/cuda/CUDA-SHA256SUMS`; logical commits local — push only on Garrett's authorization |

## Addendum (2026-09-14, after C7): the NVIDIA driver stack is three layers, not one

P7 named the whole NVIDIA driver an "external proprietary condition" (the S2 boundary). That was the
correct statement for the runtime proofs and their meaning is preserved: every C4–C7 GPU proof ran
estate-built CUDA userspace against the HOST's driver stack (Debian DKMS-built modules, NVIDIA's
Debian 13 userspace 615.71.09-2, NVIDIA's GSP firmware) and identified those host files by package.
The follow-on Platform work (docs/platform/NVIDIA-OPEN-KERNEL.md) splits that condition:

| Layer | Now |
|---|---|
| Kernel-module implementation | pinned open source (`open-gpu-kernel-modules` 615.71.09, dual MIT/GPL-2.0), **estate-built** for the Debian 6.12.107+deb13-amd64 ABI and for the estate linux-yocto 6.18.48 kernel; packaged and proven in staged roots; NOT loaded anywhere |
| NVIDIA driver userspace (`libcuda.so.1`, `libnvidia-ml.so.1`, helpers) | external/binary dependency — host packages in the Debian profile; no estate provider (OPEN decision `nvidia-userspace-driver-provider`) |
| GSP firmware (`nvidia/615.71.09/gsp_*.bin`) | external/binary dependency — `firmware-nvidia-gsp` 615.71.09-2 in the Debian profile; no estate provider (OPEN decision `nvidia-gsp-firmware-provider`) |

The S2 check in `symoneural-cuda.bbclass` is unchanged: `libcuda.so.1` and `libnvidia-ml.so.1` are
still resolved by the driver at run time and never by an estate package. Nothing in C6/C7 evidence
is rewritten by this addendum; the P9 history is untouched.
