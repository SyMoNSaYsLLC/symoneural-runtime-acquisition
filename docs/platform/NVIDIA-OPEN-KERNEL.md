# symoneural-nvidia-open-kernel — two kernel targets, one pinned NVIDIA source

Status vocabulary: PASS / FAIL / BLOCKED / NOT TESTED / NOT STARTED / HOST-CONDITIONED.
Everything below is either a verified fact (with its evidence) or an explicit status.
Nothing in this file is inferred from the August-era estate; that estate is NOT APPLICABLE.

Charter (Garrett, 2026-09-14, after the P7 C6 checkpoint): build the NVIDIA open GPU
kernel modules from controlled pristine upstream source for **(A)** the Debian kernel
ABI the development machine runs and **(B)** an estate-built Linux kernel, from one
canonical acquisition, with separate inputs, build directories, staging roots, packages
and evidence. This does not authorise loading the built modules, touching the host
module tree, signing keys, Secure Boot, initramfs, the bootloader, or the running driver.

## 1. Source — canonical identity (verified 2026-09-14)

| Item | Value | Evidence |
|---|---|---|
| Upstream | `https://github.com/NVIDIA/open-gpu-kernel-modules` | canonical remote |
| Release | `615.71.09` (`version.mk`: `NVIDIA_VERSION = 615.71.09`) | archive read |
| Commit | `61dcc93722ecb418bb5f2e00923f05b4b8051dd1` | `git ls-remote` `refs/tags/615.71.09^{}`; also today's `refs/heads/main` |
| Tag object | `d2a24f90e843359450ab313a286f43a88d95c6ce` (annotated `refs/tags/615.71.09`) | `git ls-remote` |
| Reference archive | `/home/google/Desktop/open-gpu-kernel-modules-main.zip`, 29,807,536 B, sha256 `d92c0aa2b8645bca2becf76551a832b58988e412658a3d37d438ed6ba3406445` | re-measured; GitHub's zip comment = the commit above |
| Licence | `COPYING`: MIT except where noted; "kernel module is dual licensed as MIT/GPLv2" (module `license:` strings read `Dual MIT/GPL`) | archive read; `modinfo` of the Debian-built module |
| GPU representation | `README.md` supported-GPU table: `NVIDIA GeForce RTX 5070 Ti | 2C05`; host device `10de:2c05` | archive read; a table row is not functional proof |
| Build mechanics | top `Makefile`: `modules` → `make -C src/nvidia` (nv-kernel.o, `$(CC)`) + `make -C src/nvidia-modeset` → symlinked as `*.o_binary` → `make -C kernel-open modules`; `kernel-open/Makefile` reads `SYSSRC`/`SYSOUT`, falls back to `uname -r` when they are absent, passes `CC LD OBJDUMP ARCH NV_KERNEL_MODULES NV_EXCLUDE_KERNEL_MODULES KBUILD_OUTPUT`; `conftest.sh <CC> <ARCH> <SOURCES> <OUTPUT>` | archive read |
| Modules in the tree | `nvidia nvidia-uvm nvidia-modeset nvidia-drm nvidia-peermem` (no vgpu-vfio directory) | archive listing |
| Debian's DKMS copy | `/usr/src/nvidia-615.71.09/kernel-open` is byte-identical to upstream's (only Debian's `dkms.conf` differs) → no Debian patch is needed for a 6.12 build | `diff -rq` |

Acquisition (SOURCES-100 S2, `tools/ingest-and-commit`): **NOT STARTED** — deferred until
the live P7 C7 cooker is quiescent (acquisition records are build inputs).

## 2. Kernel-input contracts

### 2A. Debian profile (development machine)

| Item | Value | Evidence |
|---|---|---|
| Target / arch | Debian 13 (trixie) `amd64`, ABI `6.12.107+deb13-amd64` — the running kernel, rechecked (`uname -r`); machine unchanged | `/proc/version` |
| Kernel provider | Debian (external in this profile) — `linux-image-6.12.107+deb13-amd64` 6.12.107-1 (signed, `pool/main/l/linux-signed-amd64`), index sha256 `7794643cf4560de2…` | trixie/main index |
| Kernel compiler | `x86_64-linux-gnu-gcc-14 (Debian 14.2.0-19) 14.2.0`, GNU ld 2.44 (`CONFIG_CC_VERSION_TEXT`) | `.config`, `/proc/version` |
| Header / build-tool closure to stage | `linux-headers-6.12.107+deb13-amd64` 6.12.107-1 sha256 `0ab746a3d854ad0e…`; `linux-headers-6.12.107+deb13-common` 6.12.107-1 `12dc292d7c238928…`; `linux-kbuild-6.12.107+deb13` 6.12.107-1 `0a88527eb05bca1c…` (all `deb.debian.org/debian trixie/main`, index 56,620,099 B sha256 `4f2c68d67001d595…`) | index |
| Toolchain identities (index) | `gcc-14` 14.2.0-19 `21500408b5019d8d…`, `cpp-14` 14.2.0-19, `binutils` 2.44-3 `6bc08c02539ba53b…`, `make` 4.4.1-2, `libelf1t64` 0.192-4; host has the same versions installed | index; `dpkg -l` |
| Layout facts | arch headers dir: `.config`, `.kernelvariables`, `Module.symvers` (26,734 symbols), `include/config`, `include/generated` (`UTS_RELEASE "6.12.107+deb13-amd64"`), `arch/x86/include/generated`; `scripts`/`tools` are RELATIVE symlinks into `linux-kbuild-6.12.107+deb13`; the arch `Makefile` is a redirector with an ABSOLUTE include of the common tree — bypassed by giving NVIDIA `SYSSRC=<common>` and `SYSOUT=<arch>` | on-disk copy of the same packages |
| Config facts that gate the build | `CONFIG_MODVERSIONS=y` (CRCs must match `Module.symvers`), `CONFIG_MODULE_SIG=y`, `CONFIG_MODULE_SIG_ALL=y`, `CONFIG_DEBUG_INFO_BTF_MODULES=y` (pahole on host: `/usr/bin/pahole`), `CONFIG_DRM=m`, `CONFIG_INFINIBAND=m`, `CONFIG_MITIGATION_RETPOLINE=y` | `.config` |
| vermagic to match | `6.12.107+deb13-amd64 SMP preempt mod_unload modversions` | `modinfo` of the Debian-built modules |
| Signing state | Secure Boot enabled; lockdown `none`; the Debian DKMS modules are PKCS#7-signed against 2 enrolled MOK certificates; **no key of any kind is read, generated or used by this work** | `efivars`, `/sys/kernel/security/lockdown`, `mokutil` count |
| Coexistence | Debian DKMS ships `nvidia.ko.xz nvidia-uvm.ko.xz nvidia-modeset.ko.xz nvidia-drm.ko.xz nvidia-peermem.ko.xz` under `/lib/modules/6.12.107+deb13-amd64/updates/dkms/`; `nvidia-kernel-open-dkms` Provides `nvidia-kernel-615.71.09`; our package must not claim that path or Provides, must declare the module-name collision, and is never installed on the host | `dpkg -L`, index |

Isolation plan: the three kernel debs are fetched by SHA256 through the BitBake fetcher
and extracted into a disposable root; NVIDIA's wrapper receives `SYSSRC`, `SYSOUT`,
`KERNEL_UNAME`, `ARCH=x86_64`, `CC`, `LD` explicitly (no `uname -r` fallback can
fire). Compiler, binutils and make come from the host at the index-recorded versions,
declared through `HOSTTOOLS` — the proof is therefore **HOST-CONDITIONED** on the
toolchain until a full pinned toolchain root exists (named remaining work).

### 2B. Estate profile

| Item | Value | Evidence |
|---|---|---|
| Machine / distro / arch | `qemux86-64` (DEFAULTTUNE `x86-64-v3`, `PREFERRED_PROVIDER_virtual/kernel ??= "linux-yocto"`), nodistro; x86-64 | `conf/machine/qemux86-64.conf`, build `local.conf` |
| Kernel provider candidates in the pinned OE stack | `linux-yocto` 6.18.48 (`v6.18/standard/base`, `SRCREV_machine:qemux86-64 ad9d5e451874e64e4e51093f3c9c6ca4426d3b0a`, `SRCREV_meta c8484925c85ec1e6510c75d9e1b36e01d6e2e904`) and 7.2.4 (`881860c6…`/`ad69d353…`) | oe-core recipes |
| Selection | **6.18.48** — nearer the Debian 6.12 ABI NVIDIA 615 is proven on (README: "4.15 or newer"), the older of the two pinned lines; 7.2 recorded as available, not chosen because newer | this document |
| Kernel release string (expected) | `6.18.48-yocto-standard` (`LINUX_VERSION_EXTENSION ??= "-yocto-${LINUX_KERNEL_TYPE}"`) — to be read from `kernel-abiversion` after the build, never assumed | `linux-yocto.inc` |
| External-module inputs OE provides | `virtual/kernel:do_shared_workdir` → `STAGING_KERNEL_BUILDDIR` (`.config`, `Module.symvers`, `include/generated`, `scripts/module.lds`), `STAGING_KERNEL_DIR` (source), `make-mod-scripts` (kbuild helpers), `kernel-devsrc` | `kernel.bbclass`, `module.bbclass` |
| Toolchain | estate cross toolchain (`KERNEL_CC`/`KERNEL_LD`/`KERNEL_AR`/`KERNEL_OBJCOPY`, GCC 16.2) | module.bbclass |
| Module packaging | `kernel-module-split`: one package per `.ko`, suffix `-${KERNEL_VERSION}`, `PACKAGE_ARCH = ${MACHINE_ARCH}`, RDEPENDS on the kernel's module base — ipk | classes |
| Boot / qualification | a QEMU build-test baseline only; **no** production-machine boot, **no** RTX 5070 Ti qualification | charter |

Isolation plan: a new platform runtime `Symoneural-Platform` with its own build
directory; `module.bbclass` for the recipe with `do_compile` driving NVIDIA's own
wrapper (`SYSSRC=${STAGING_KERNEL_DIR} SYSOUT=${STAGING_KERNEL_BUILDDIR}`), because the
class's `KERNEL_SRC` alone does not reach NVIDIA's Makefile.

## 3. Module scope (both profiles)

| Module | Decision | Reason |
|---|---|---|
| `nvidia`, `nvidia-uvm` | build | core + CUDA UVM: the requirement |
| `nvidia-modeset`, `nvidia-drm` | build where the target kernel has `CONFIG_DRM` (Debian: `=m`; estate: read from the built `.config`), else document | display/KMS path the Debian host actually uses (both loaded) |
| `nvidia-peermem` | **exclude** | needs the out-of-tree InfiniBand peer-memory API (MLNX OFED); no estate consumer |
| `nvidia-vgpu-vfio` | not in the tree | — |

## 4. Dependency boundary (recorded, not provided by this component)

| Component | Debian profile identity (NVIDIA debian13 index, sha256 `769ece572c8ac899…`) | Estate profile |
|---|---|---|
| Open kernel modules | this work | this work |
| Target kernel | Debian `linux-image-6.12.107+deb13-amd64` 6.12.107-1 | `linux-yocto` 6.18.48 (estate-built) |
| Driver userspace (`libcuda.so.1`, `libnvidia-ml.so.1`, …) | `libcuda1` 615.71.09-2 sha256 `75643aab978f99c5…`, `libnvidia-ml1` 615.71.09-2 `737b4ee1b3eb66c6…`, `nvidia-driver` 615.71.09-2 `fb02bb1e9f336b59…`, helpers `libnvidia-gpucomp`/`libnvidia-nvvm704`/`libnvidia-ptxjitcompiler1` 615.71.09-2 — the S2 boundary of P7 | **no estate provider — deployment BLOCKER** |
| GSP firmware (`nvidia/615.71.09/gsp_*.bin`, `ucodes_*.bin`) | `firmware-nvidia-gsp` 615.71.09-2 sha256 `2f72dd12294aba56…` (75,697,546 B) | **no estate provider — deployment BLOCKER** (oe-core `linux-firmware` ships nouveau-era NVIDIA firmware, not 615.71.09 GSP) |
| CUDA userspace consumers | `cuda-toolkit-bin` 13.4.1, `symoneural-ggml-cuda`, `symoneural-pytorch` (P7) | same |

The `.ko` packages do **not** provide `libcuda.so.1` or `libnvidia-ml.so.1`; nothing may
resolve those userspace NEEDED entries with a kernel-module package.

## 5. Two-target matrix

| Stage | A. Debian 6.12.107+deb13-amd64 | B. Estate linux-yocto 6.18.48 qemux86-64 |
|---|---|---|
| SOURCE | verified identity (§1); acquisition NOT STARTED | same acquisition |
| KERNEL INPUTS | identified and pinned (§2A); staging NOT STARTED | selected (§2B); kernel build NOT STARTED |
| KERNEL BUILD | not applicable (Debian-provided) | NOT STARTED |
| MODULE BUILD | NOT STARTED | NOT STARTED |
| ABI | NOT TESTED | NOT TESTED |
| PACKAGE / QA | NOT STARTED (`.deb`) | NOT STARTED (`.ipk`) |
| STAGED INSTALL | NOT STARTED | NOT STARTED |
| NEGATIVE CHECKS | NOT TESTED | NOT TESTED |
| REPRODUCIBILITY | expected HOST-CONDITIONED (toolchain from host) | NOT TESTED |
| SIGNING | BLOCKED for live use: Secure Boot on, MOK-signed policy; artifacts will be UNSIGNED and labelled so; no keys touched | not applicable to a QEMU baseline; unsigned |
| BOOTED / MODULE LOADED | NOT TESTED (not authorised) | NOT TESTED |
| GPU CONSUMER | NOT TESTED (the host's Debian DKMS modules serve P7's proofs; equal version strings prove nothing about these artifacts) | NOT TESTED |
| Userspace / firmware / integration blockers | recorded in §4 | recorded in §4 |
