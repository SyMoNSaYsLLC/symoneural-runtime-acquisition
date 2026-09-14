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

## C7 — PyTorch CUDA / distributed feature matrix (drafted from the pinned tree; build NOT started)

The pinned `symoneural-pytorch` is CPU-only by recorded decision (`USE_CUDA=0`,
`USE_DISTRIBUTED=0`). This is the intended CUDA variant, to be built only after C5
proves the low-level sm_120 path. Each row is a recipe decision with its evidence.

| Option | Setting | Why |
| --- | --- | --- |
| `USE_CUDA` | 1 via `symoneural-cuda` (nvcc-native, target libs, `TORCH_CUDA_ARCH_LIST=12.0`) | the authority; `cmake/public/cuda.cmake` requires ≥ 12.6; arch tables carry `12.0` |
| `TORCH_CUDA_ARCH_LIST` | `12.0` (no `+PTX` until a second GPU generation exists) | one card, one architecture; every extra arch multiplies compile time |
| `USE_CUDNN` | **decision pending — separate BINARY_EXTERNAL** (`libcudnn9-cuda-13` 9.25.1.1 / 9.26.0.51 in the same index; torch CI pairs 13.4 with cuDNN 9.25.0.15) | default ON when `USE_CUDA`; without it convolutions fall back to native kernels. Not part of the toolkit authority |
| `USE_CUSPARSELT`, `USE_CUFILE` | 0 | optional libraries torch CI adds separately; no estate consumer needs them |
| `USE_NCCL` | 0 | one GPU; NCCL is a separate binary (`libnccl2 2.31.2+cuda13.4`) with no consumer |
| `USE_DISTRIBUTED` | **1** (gloo CPU backend; NCCL off) | the accelerate ruling: `Accelerator.prepare()` needs `torch.distributed` compiled in even single-process; this is the "final PyTorch feature-set" that ruling deferred to |
| `USE_KINETO` / CUPTI | keep default (CUPTI is in the authority: `cuda-cupti-13-4`) | profiler support without a new binary |
| `USE_FLASH_ATTENTION`, `USE_MEM_EFF_ATTENTION` | default ON (cutlass 4.6.1 has SM120 gating) | compile cost is the price of the feature; revisit if the build proves prohibitive |
| Host compiler | estate cross g++ 16.2 through `CMAKE_CUDA_HOST_COMPILER` | nvcc 13.4 accepts GCC 16 (verified) |
| `MAX_JOBS` | unchanged (12) | CUDA TUs are memory-heavy; measured, not guessed, on the first build |

**accelerate** is revisited at the end of C7: with `USE_DISTRIBUTED=1` the
`model_has_dtensor` import resolves; the ruling `accelerate-torch-distributed` moves
from DEFERRED to re-tested, and only a re-run of `tools/clean-root-proof Common` with
accelerate back in the packagegroup can promote it.

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
| C7 PyTorch CUDA/distributed matrix · accelerate | NOT STARTED |
| C8 Crypto/Tune compatibility | NOT STARTED |
| C9 package / clean-install / host-leakage | PASS for the authority + probe and for the LLM consumer image (both proofs, host cache inhibited: CPU mode maps nothing from outside the root; S2 mode maps only files owned by packages at the installed driver version); PyTorch consumer pending C7 |
| C10 records / evidence / commits | IN PROGRESS — for C0–C6: `unresolved.json:cuda-toolkit-authority` resolved by evidence (repo-deb path, index sha256, proofs), `provider-decisions.json` names `cuda-toolkit` BINARY-EXTERNAL, evidence under `generated/evidence/cuda/` and `…/llm/`, logical commits; determinism / verify-acquisition / workscope PASS. C7/C8 records pending their work |
