# symoneural-nvidia-open-kernel — two kernel targets, one pinned NVIDIA source

Status vocabulary: PASS / FAIL / BLOCKED / NOT TESTED / NOT STARTED / DEFERRED; HOST-CONDITIONED is a
qualifier on a status, never a status. Everything below is a verified fact with its evidence or an
explicit status. Nothing is inferred from the August-era estate; that estate is NOT APPLICABLE.

Charter (Garrett, 2026-09-14, after the P7 C6 checkpoint; executed after the P7 C7 checkpoint):
build the NVIDIA open GPU kernel modules from controlled pristine upstream source for **(A)** the
Debian kernel ABI the development machine runs and **(B)** an estate-built Linux kernel, from ONE
canonical acquisition, with separate inputs, build directories, staging roots, packages and
evidence. The charter does not authorise loading the built modules, touching the host module tree,
signing keys, Secure Boot, initramfs, the bootloader, or the running driver — and none of that was
done. Live activation stays NOT TESTED / BLOCKED (section 7).

## 1. Source — canonical identity (acquired 2026-09-14)

| Item | Value | Evidence |
|---|---|---|
| Upstream | `https://github.com/NVIDIA/open-gpu-kernel-modules` | canonical remote |
| Release | `615.71.09` (`version.mk`: `NVIDIA_VERSION = 615.71.09`) | committed tree |
| Commit | `61dcc93722ecb418bb5f2e00923f05b4b8051dd1` | `git ls-remote refs/tags/615.71.09^{}` (re-checked at evidence time) |
| Tag object | `d2a24f90e843359450ab313a286f43a88d95c6ce` — annotated, SSH-signed by NVIDIA's tagger | `git cat-file -p` in the pin store |
| Tree | `9199a9f620b76343c35c207354ffcb3d1570053d` = `HEAD:Symoneural-Platform/src/kernel/source/open-gpu-kernel-modules` | `tools/ingest-tree verify open-gpu-kernel-modules` → VERIFIED (4005 files, no submodules) |
| Acquisition | records `670d01c81`; tree `1e385bf66` (`tools/ingest-and-commit`; pin store `Symoneural-Platform/src/kernel/.gitpins/open-gpu-kernel-modules.git`, local, never pushed) | git log |
| Licence | `COPYING` (md5 `1d5fa2a493e937d5a4b96e5e03b90f7c`): MIT except where noted; "when linked together to form a Linux kernel module, the resulting Linux kernel module is dual licensed as MIT/GPLv2". SPDX census of the tree: MIT 2946, Linux-OpenIB 1, Apache-2.0 WITH LLVM-exception 1. Module `license:` string: `Dual MIT/GPL`. Recipe LICENSE `MIT OR GPL-2.0-only`. | `generated/evidence/platform/NVIDIA-OPEN-KERNEL-SOURCE.txt` |
| GPU representation | `README.md` line 983: `NVIDIA GeForce RTX 5070 Ti | 2C05`; host GPU `10de:2c05` — a table row, not functional proof | committed tree |
| Reference archive | `/home/google/Desktop/open-gpu-kernel-modules-main.zip` sha256 `d92c0aa2b8645bca2becf76551a832b58988e412658a3d37d438ed6ba3406445` — supporting evidence only | re-measured |
| Debian's DKMS copy | `/usr/src/nvidia-615.71.09/kernel-open` differs from the committed `kernel-open/` only by `dkms.conf` — evidence only, never a build input | `diff -rq` |

Both recipes build from `symoneural-pristine`'s disposable export of `HEAD:<source_path>`; the
acquired tree is never written. No source patch was needed for either kernel.

## 2. Kernel-input contracts and what was actually used

### 2A. Debian profile (development machine) — HOST-CONDITIONED

| Item | Value | Evidence |
|---|---|---|
| Target | Debian 13.7 amd64, ABI `6.12.107+deb13-amd64` (the running kernel; `/proc/version`) | host |
| Kernel inputs (recipe `debian-kernel-inputs-6.12.107+deb13-amd64`, fetched by SHA256, staged into the recipe sysroot under their Debian paths, deployed unchanged for the proof) | `linux-headers-6.12.107+deb13-amd64` 6.12.107-1 `0ab746a3d854ad0e666923147842d1e629cdb3e29a97b76ae25b4911285174e4`; `linux-headers-6.12.107+deb13-common` `12dc292d7c238928fbcb7eebbe79208758fe263a4e2ea0e9b6734e6df12020a5`; `linux-kbuild-6.12.107+deb13` `0a88527eb05bca1ce75e7d39ec27539d385a24cf90b2b28917cc4903a4f710d3`; `linux-image-6.12.107+deb13-amd64` (signed) `7794643cf4560de2a7e3b069e8ca8511ad2a568d652ea285f0fe051f79bc9e99` — re-verified 2026-09-14 against the local trixie/main index (sha256 `4f2c68d67001d595fbd343f6dbad44468953a51c4d9dec3a4803249f6e295940`, InRelease 12 Sep 2026) | index; `tmp/deploy/images/qemux86-64/debian-kernel-inputs/SHA256SUMS` |
| Compiler identity | `CONFIG_CC_VERSION_TEXT="x86_64-linux-gnu-gcc-14 (Debian 14.2.0-19) 14.2.0"`; the module build asserts the declared `x86_64-linux-gnu-gcc-14 --version` equals it | recipe; `log.do_compile` |
| Host tools admitted | `HOSTTOOLS += x86_64-linux-gnu-{gcc-14,ld,ld.bfd,ar,nm,objcopy,objdump,strip,readelf} pahole` (installed gcc-14 14.2.0-19, binutils 2.44-3, dwarves 1.30-1 = index versions) plus Debian's prebuilt kbuild helpers from `linux-kbuild` (fixdep, modpost, genksyms, objtool, resolve_btfids) | `meta-symoneural/conf/templates/platform-debian-6.12.107-deb13-amd64/local.conf.sample` |
| Wrapper inputs | `SYSSRC=<sysroot>/usr/src/linux-headers-6.12.107+deb13-common SYSOUT=<sysroot>/usr/src/linux-headers-6.12.107+deb13-amd64 KERNEL_UNAME=6.12.107+deb13-amd64 ARCH=x86_64 TARGET_ARCH=x86_64 TARGET_OS=Linux CC=… CROSS_COMPILE=x86_64-linux-gnu- … KCFLAGS/EXTRA_CFLAGS=<OE prefix maps>`; Debian's `.kernelvariables` additionally overrides `KERNELRELEASE`/`CROSS_COMPILE` inside kbuild | `log.do_compile` line 2 (quoted in `NVIDIA-OPEN-KERNEL-DEBIAN-BUILD.txt`) |
| Kernel facts that gated the build | `MODVERSIONS=y MODULE_SIG=y MODULE_SIG_ALL=y DEBUG_INFO_BTF_MODULES=y DRM=m`; the arch headers ship a BTF-only `vmlinux` (5.87 MB) so module BTF was generated (4 `pahole --btf_base vmlinux` runs); the signed `linux-image` ships an 83-byte placeholder `System.map` ("the real System.map is in the -dbg package") — the proof therefore uses `Module.symvers` as the symbol/CRC oracle | inputs recipe assertions; proof section 6 |
| Build directory | `Symoneural-Platform/build/debian-6.12.107-deb13-amd64` (no `+`: OE's sanity checker rejects it in TMPDIR paths; first launch failed on exactly that), `PACKAGE_CLASSES = package_deb`, from the layer template | template; `conf/templateconf.cfg` |

### 2B. Estate profile — estate cross toolchain

| Item | Value | Evidence |
|---|---|---|
| Machine / kernel | `qemux86-64` (x86-64-v3), `linux-yocto` **6.18.48** — recipe `linux-yocto_6.18.bb` (oe-core `fe7a24bc67`), `SRCREV_machine ad9d5e451874e64e4e51093f3c9c6ca4426d3b0a` (v6.18/standard/base), `SRCREV_meta c8484925c85ec1e6510c75d9e1b36e01d6e2e904` (yocto-6.18); kernel package version `6.18.48+git0+c8484925c8_ad9d5e4518-r0` carries both | build log; feed |
| Selection discrepancy, resolved explicitly | the pinned metadata holds 6.18.48 and 7.2.4; with no preference BitBake picks 7.2.4 (Ravencalc's sstate holds such a build). The Platform estate template pins `PREFERRED_VERSION_linux-yocto = "6.18%"` per the charter; the built ABI was read back from `kernel-abiversion`: **`6.18.48-yocto-standard`** | `platform-estate/local.conf.sample`; `kernel-build-artifacts/kernel-abiversion` |
| Kernel sources | the estate's own git mirrors (`Symoneural-Ravencalc/downloads/git2/…linux-yocto.git`, `…yocto-kernel-cache`) cloned locally into `Symoneural-Platform/downloads/git2/` before the build; both SRCREVs were present, no network fetch was needed | evidence file |
| Toolchain | estate cross toolchain from the shared sstate: `CONFIG_CC_VERSION_TEXT="x86_64-oe-linux-gcc (GCC) 16.2.0"`; modules compiled by `x86_64-oe-linux-gcc` (1488 invocations, 0 host gcc) via module.bbclass's `KERNEL_CC` (carries OE's prefix maps) | `log.do_compile` |
| Kernel facts | `MODULES=y MODULE_UNLOAD=y DRM=y DRM_KMS_HELPER=y DRM_TTM_HELPER=y DRM_DISPLAY_HELPER=m VIDEO=y PREEMPT=y SMP=y`; **not set**: `MODVERSIONS` (vermagic-only ABI — CRC checks NOT APPLICABLE), `MODULE_SIG`, `MODULE_COMPRESS_*`, `DEBUG_INFO_BTF` | `kernel-build-artifacts/.config` |
| Wrapper inputs | `SYSSRC=…/work-shared/qemux86-64/kernel-source SYSOUT=…/work-shared/qemux86-64/kernel-build-artifacts KERNEL_UNAME=6.18.48-yocto-standard ARCH=x86_64 TARGET_ARCH=x86_64 TARGET_OS=Linux NV_EXCLUDE_KERNEL_MODULES=nvidia-peermem NV_BUILD_USER=symoneural NV_BUILD_HOST=symoneural` on top of module.bbclass's `KERNEL_SRC/KERNEL_PATH/O/CC/LD/AR/OBJCOPY/STRIP` | `log.do_compile` line 2 |
| Build directory | `Symoneural-Platform/build/devtool-master`, package_ipk, from the layer template | template |

## 3. Module scope (both profiles, as built)

| Module | Decision | Result |
|---|---|---|
| `nvidia`, `nvidia-uvm` | build | built for both targets |
| `nvidia-modeset`, `nvidia-drm` | build where the kernel has `CONFIG_DRM` (Debian `=m`, estate `=y`) | built for both targets |
| `nvidia-peermem` | **exclude** (`NV_EXCLUDE_KERNEL_MODULES`; needs the out-of-tree InfiniBand peer-memory API, no estate consumer) | absent from both builds and packages (asserted) |
| `nvidia-vgpu-vfio` | not in the tree | — |

## 4. Dependency boundary — the CURRENT platform view

The P7 C4–C7 proofs stopped the graph at "external NVIDIA driver". That boundary was sufficient for
the runtime proofs and those proofs remain valid: they proved estate-built CUDA userspace against
the HOST's driver stack (Debian DKMS-built modules, NVIDIA's Debian 13 userspace and firmware). They
did not prove an estate-built kernel driver, and nothing below rewrites them. The stack, node by node,
with today's provider:

| Layer | Debian profile (development machine) | Estate profile (qemux86-64 baseline) |
|---|---|---|
| SyMoNeuRaL CUDA consumers | `symoneural-pytorch`, `symoneural-ggml-cuda` + `libsymoneural-llm`, `symoneural-accelerate` — built, proven (C6, C7) | same packages |
| CUDA 13.4.1 / cuDNN 9.25.1.1 userspace | `cuda-toolkit-bin`, `cudnn-bin` — BINARY-EXTERNAL, pinned, built | same |
| NVIDIA driver userspace ABI (`libcuda.so.1`, `libnvidia-ml.so.1`, gpucomp, nvvm, ptxjitcompiler, nvidia-modprobe) | **EXTERNAL**: host packages 615.71.09-2 from NVIDIA's Debian 13 index (`libcuda1` `75643aab…`, `libnvidia-ml1` `737b4ee1…`); the P7 S2 boundary, identified by dpkg in every S2 proof | **NO PROVIDER — deployment BLOCKED** (`unresolved.json:nvidia-userspace-driver-provider`) |
| **NVIDIA open kernel modules 615.71.09** | **this work**: `symoneural-nvidia-open-kernel-6.12.107+deb13-amd64` (.deb) — BUILD/PACKAGE/STAGED INSTALL PASS (HOST-CONDITIONED) | **this work**: `kernel-module-nvidia{,-uvm,-modeset,-drm}-6.18.48-yocto-standard` + `symoneural-nvidia-open-kernel` (ipk) — PASS |
| NVIDIA GSP firmware (`nvidia/615.71.09/gsp_*.bin`, `ucodes_*.bin`, requested by `nvidia.ko`: `modinfo -F firmware`) | **EXTERNAL**: `firmware-nvidia-gsp` 615.71.09-2 (`2f72dd12…`); the .deb Depends on it | **NO PROVIDER — deployment BLOCKED** (`unresolved.json:nvidia-gsp-firmware-provider`; oe-core `linux-firmware` carries nouveau-era NVIDIA firmware, not 615.71.09 GSP) |
| Target kernel | Debian `linux-image-6.12.107+deb13-amd64` 6.12.107-1 — EXTERNAL, pinned inputs; the .deb Depends on exactly this version | `linux-yocto` 6.18.48 — **estate-built** this run (`kernel-6.18.48-yocto-standard` ipk sha256 `ae60b691fc4cfa5d49b5d90440cee9556d25c03dd1455e1dabffa1804c066de9`) |
| GPU | RTX 5070 Ti `10de:2c05` cc 12.0 — serves the C6/C7 proofs through the HOST stack only | not present in the QEMU baseline |

The `.ko` packages do **not** provide `libcuda.so.1` or `libnvidia-ml.so.1` and nothing may resolve
those NEEDED entries with a kernel-module package (`symoneural-cuda.bbclass` S2 check unchanged).
Open kernel modules do not make the NVIDIA driver stack open: two proprietary layers remain external.
Complete fresh-machine GPU deployment from estate artifacts is therefore **BLOCKED** on the two
provider decisions above, even with both module packages built.

## 5. Two-target matrix (verified 2026-09-14; commands and outputs in generated/evidence/platform/)

| Stage | A. Debian 6.12.107+deb13-amd64 | B. Estate linux-yocto 6.18.48 qemux86-64 |
|---|---|---|
| SOURCE | PASS — one pinned acquisition, VERIFIED from HEAD (`NVIDIA-OPEN-KERNEL-SOURCE.txt`) | same acquisition |
| KERNEL INPUTS | PASS — four Debian debs by sha256, staged and asserted (`debian-kernel-inputs` recipe) | PASS — estate kernel built this run; `kernel-abiversion` 6.18.48-yocto-standard |
| KERNEL BUILD | not applicable (Debian-provided) | PASS — `linux-yocto-6.18.48+git-r0`, 1072 tasks |
| MODULE BUILD | PASS (HOST-CONDITIONED on Debian gcc-14 14.2.0-19 / binutils 2.44-3 / pahole 1.30 and Debian's prebuilt kbuild helpers) — 830 tasks; 1685 gcc-14 invocations, 0 estate gcc; 248 conftest probes; 202 kbuild compiles; MODPOST; BTF generated | PASS — 1488 `x86_64-oe-linux-gcc` invocations, 0 host gcc, 0 `uname -r`, 0 host header refs; 248 conftest probes; 202 compiles |
| ABI | PASS — vermagic `6.12.107+deb13-amd64 SMP preempt mod_unload modversions`; all imported symbol CRCs resolve against the kernel's `Module.symvers` or the sibling modules (459/327/103/272 imports); `srcversion` of all four modules IDENTICAL to the host's DKMS-built modules; `depmod -e -E` clean | PASS — vermagic `6.18.48-yocto-standard SMP preempt mod_unload`; MODVERSIONS NOT APPLICABLE (kernel config); `depmod -e -E` clean |
| PACKAGE / QA | PASS — `symoneural-nvidia-open-kernel-6.12.107+deb13-amd64_615.71.09-r0_amd64.deb` 9,388,388 B sha256 `c1f6abc07885ebfb9a20abed3ed0bb49a36be6eddcf3761b2e7e6d9a1d62ffec` (+ -dev, -dbg); `do_package_qa` 0 issues; no INSANE_SKIP; Depends `linux-image-… (= 6.12.107-1), firmware-nvidia-gsp (= 615.71.09-2)`; Conflicts with NVIDIA's DKMS packages; installs under `/usr/lib/modules/…/updates/symoneural/` only | PASS — `kernel-module-nvidia-6.18.48-yocto-standard_615.71.09-r0_qemux86_64.ipk` 11,644,856 B sha256 `5bddaec11f661be759e7e0c7212a790cf832b91913354d45e1706a992949a5d5` + uvm/modeset/drm + meta/dev/dbg; `do_package_qa` 0 issues; no INSANE_SKIP; each module package Depends on `kernel-6.18.48-yocto-standard` and its in-tree helper modules; `Source: symoneural-nvidia-open-kernel_615.71.09.bb` |
| STAGED INSTALL | PASS — disposable root, `dpkg --unpack` under an unprivileged user namespace beside the extracted linux-image metadata; `depmod -b <root>`; 113 checks, 0 failures (`NVIDIA-OPEN-KERNEL-DEBIAN-PROOF.txt`) | PASS — disposable root, the estate's `opkg` installing from an indexed copy of the feed, 15-package closure resolved by opkg; `depmod -b <root>`; 115 checks, 0 failures (`NVIDIA-OPEN-KERNEL-ESTATE-PROOF.txt`) |
| NEGATIVE / LEAKAGE | PASS — wrong `SYSSRC` fails naming the path (no `uname -r` rescue); no TMPDIR, home, hostname or login string in any shipped module or its debug info; no DKMS path, userspace library or firmware in the package; host module tree byte-identical before/after | PASS — no TMPDIR, home, hostname, login, host header or host kernel string in any module; no DKMS path, userspace library or firmware in the root |
| REPRODUCIBILITY | NOT TESTED (and HOST-CONDITIONED until a pinned toolchain root exists) | NOT TESTED (no differing-root comparison) |
| SIGNING | BLOCKED for live use — Secure Boot on, MOK-signed policy; artifacts UNSIGNED and labelled; no key read, made or used | not applicable to the QEMU baseline; unsigned |
| BOOT / MODULE LOAD | NOT TESTED (not authorised) | NOT TESTED |
| GPU CONSUMER | NOT TESTED — the host's Debian DKMS modules serve P7's proofs; equal `srcversion`/vermagic prove same inputs, not that these files were loaded | NOT TESTED (no GPU in the baseline) |
| Userspace / firmware providers | EXTERNAL (host) | BLOCKED (section 4) |

## 6. Artifacts and evidence

- `generated/evidence/platform/NVIDIA-OPEN-KERNEL-SOURCE.txt` — source identity and verification.
- `generated/evidence/platform/NVIDIA-OPEN-KERNEL-DEBIAN-BUILD.txt` — inputs, toolchain identities, make invocation, QA, package identities and control, module facts vs the host reference.
- `generated/evidence/platform/NVIDIA-OPEN-KERNEL-DEBIAN-PROOF.txt` — staged-install transcript (`tools/nvidia-open-kernel-proof debian`).
- `generated/evidence/platform/NVIDIA-OPEN-KERNEL-ESTATE-BUILD.txt` — kernel identity and config facts, make invocation, QA, package identities, module facts.
- `generated/evidence/platform/NVIDIA-OPEN-KERNEL-ESTATE-PROOF.txt` — staged-install transcript (`tools/nvidia-open-kernel-proof estate`).
- `generated/evidence/platform/SHA256SUMS` — every artifact and transcript above (`sha256sum -c` from the repository root).
- Recipes: `meta-symoneural/recipes-platform/debian-kernel-inputs/`, `meta-symoneural/recipes-platform/symoneural-nvidia-open-kernel/` (`.inc` + two `.bb`). Build templates: `meta-symoneural/conf/templates/platform-*/`. Launcher: `tools/symonbake <Runtime> [--build-dir <name>] …`.
- Records: `component-state.json` (TARGET), `provider-decisions.json` (`nvidia-open-kernel-modules`: SYMONEURAL-OWNED), `unresolved.json` (two OPEN deployment blockers), `source-lock.json` (recipe fields refreshed).

## 7. Remaining blockers and what this does not claim

1. **NVIDIA driver userspace provider for the estate profile** — OPEN (`unresolved.json`). Without it the estate-built kernel + modules cannot run CUDA on any machine.
2. **GSP firmware provider for the estate profile** — OPEN. `nvidia.ko` requests `nvidia/615.71.09/{gsp_tu10x,gsp_ga10x,ucodes_tu10x,ucodes_ga10x}.bin` at load.
3. **Signing / live activation on the development machine** — BLOCKED by policy; a separate gate. The .deb is never installed on the host by this work; a runbook for any future activation must be written to the Desktop stakeholder folder first.
4. **Reproducibility** — NOT TESTED for both targets; the Debian target additionally depends on host toolchain identity.
5. **Hardware qualification** — the qemux86-64 result is a build/package result, not RTX 5070 Ti compatibility.
6. **Adjacent, not started**: AWCC (pending row, GPL-3.0 ruling), kawpowminer (DEFERRED P11), acpi_call module.
