# Shared by the two symoneural-nvidia-open-kernel* recipes: ONE pinned NVIDIA source tree, TWO
# kernel targets (docs/platform/NVIDIA-OPEN-KERNEL.md). Each target has its own recipe, build
# directory, kernel inputs, staging root and package identity; only the source and these
# shared facts are common.
SUMMARY = "NVIDIA open GPU kernel modules ${PV} - source-built from the pinned tree, UNSIGNED"
DESCRIPTION = "nvidia, nvidia-uvm, nvidia-modeset and nvidia-drm built from NVIDIA's \
open-gpu-kernel-modules release ${PV}. KERNEL MODULES ONLY: the NVIDIA driver userspace \
(libcuda.so.1, libnvidia-ml.so.1, libnvidia-gpucomp, libnvidia-nvvm, libnvidia-ptxjitcompiler, \
nvidia-modprobe) and the GSP firmware the modules request (nvidia/${PV}/gsp_*.bin, ucodes_*.bin) \
are NOT part of these packages and remain separately provided dependencies."
HOMEPAGE = "https://github.com/NVIDIA/open-gpu-kernel-modules"
SECTION = "kernel"

# COPYING, read from the acquired tree: files are MIT "except where noted otherwise" (SPDX census
# of the tree at this pin: MIT 2900, Linux-OpenIB 1, Apache-2.0 WITH LLVM-exception 1); "when
# linked together to form a Linux kernel module, the resulting Linux kernel module is dual
# licensed as MIT/GPLv2" - the modules' license string is "Dual MIT/GPL".
LICENSE = "MIT OR GPL-2.0-only"
LIC_FILES_CHKSUM = "file://COPYING;md5=1d5fa2a493e937d5a4b96e5e03b90f7c"

# SOURCES-100 pin: acquisition/source-lock.json component open-gpu-kernel-modules (runtime
# Platform), upstream annotated tag 615.71.09 = d2a24f90e843359450ab313a286f43a88d95c6ce.
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Platform/src/kernel/source/open-gpu-kernel-modules"
SRCREV = "61dcc93722ecb418bb5f2e00923f05b4b8051dd1"
PV = "615.71.09"

# Module scope (docs/platform/NVIDIA-OPEN-KERNEL.md section 3). nvidia-peermem needs the
# out-of-tree InfiniBand peer-memory API (MLNX OFED) and has no estate consumer: excluded, never
# built. The tree has no nvidia-vgpu-vfio directory.
NV_KERNEL_MODULES = "nvidia nvidia-uvm nvidia-modeset nvidia-drm"
NV_EXCLUDE_KERNEL_MODULES = "nvidia-peermem"

# Reproducible build identity: utils.mk defaults NV_BUILD_USER/NV_BUILD_HOST to `whoami` and
# `hostname` and embeds "(user@host)" in the nv-kernel.o build string. Fixed values, not the
# workstation's.
NV_BUILD_IDENTITY = "NV_BUILD_USER=symoneural NV_BUILD_HOST=symoneural"

# The string the modules must carry; asserted after every build.
NV_MODULE_LICENSE_STRING = "license=Dual MIT/GPL"

COMPATIBLE_HOST = "x86_64.*-linux"
