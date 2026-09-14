# ESTATE TARGET (B): NVIDIA open GPU kernel modules for the kernel the estate builds itself -
# virtual/kernel of the Symoneural-Platform estate build directory (linux-yocto, charter 6.18.48,
# qemux86-64), through OE's own external-module path (module.bbclass: cross toolchain, shared
# kernel work dir, kernel-module-split packaging). Nothing here reads the host kernel: SYSSRC and
# SYSOUT are the staged kernel source and build-artifact trees, KERNEL_UNAME the built kernel's
# abiversion; the resulting vermagic is the estate kernel's, not the workstation's.
#
# Build result for qemux86-64 is a build/package/staged-install result, not an RTX 5070 Ti
# hardware qualification (docs/platform/NVIDIA-OPEN-KERNEL.md section 2B, 5).
require symoneural-nvidia-open-kernel.inc

# Restated here because tools/scan-acquisition.py pairs a tree with its recipe by reading the
# .bb text (SYMON_TREE / SRCREV / PV / LICENSE), not included files. Values identical to the .inc.
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Platform/src/kernel/source/open-gpu-kernel-modules"
SRCREV = "61dcc93722ecb418bb5f2e00923f05b4b8051dd1"
PV = "615.71.09"
LICENSE = "MIT OR GPL-2.0-only"

inherit symoneural-pristine module

# NVIDIA's build writes into its own tree (kernel-open/*.o, src/*/_out/); the pristine class's
# export under ${WORKDIR} is disposable, so building in place is safe and is what the tree's
# Makefiles expect.
B = "${S}"

MODULES_MODULE_SYMVERS_LOCATION = "kernel-open"
MAKE_TARGETS = "modules"
MODULES_INSTALL_TARGET = "modules_install"

# module.bbclass hands kbuild KERNEL_SRC / KERNEL_PATH / O and the cross tools (CC=KERNEL_CC with
# OE's prefix maps, LD, AR, OBJCOPY, STRIP). NVIDIA's wrapper (kernel-open/Makefile) reads SYSSRC
# and SYSOUT instead and otherwise falls back to `uname -r` - so both are given explicitly. Its
# architecture test wants ARCH=x86_64 (module-base exports ARCH=x86 for kbuild; a command-line
# value wins and kbuild remaps x86_64 -> x86 itself). TARGET_OS/TARGET_ARCH feed utils.mk for the
# nv-kernel.o / nv-modeset-kernel.o builds (OE's exported OS=linux would otherwise drop -DNV_LINUX).
EXTRA_OEMAKE += "SYSSRC=${STAGING_KERNEL_DIR} SYSOUT=${STAGING_KERNEL_BUILDDIR} KERNEL_UNAME=${KERNEL_VERSION} \
    ARCH=x86_64 TARGET_ARCH=x86_64 TARGET_OS=Linux \
    NV_EXCLUDE_KERNEL_MODULES=${NV_EXCLUDE_KERNEL_MODULES} ${NV_BUILD_IDENTITY} NV_VERBOSE=1"

do_compile:prepend() {
    for f in .config Module.symvers include/config/kernel.release; do
        [ -e ${STAGING_KERNEL_BUILDDIR}/$f ] || bbfatal "estate kernel build artifacts lack $f: ${STAGING_KERNEL_BUILDDIR}"
    done
    [ -f ${STAGING_KERNEL_DIR}/Makefile ] || bbfatal "estate kernel source missing: ${STAGING_KERNEL_DIR}"
    [ "$(cat ${STAGING_KERNEL_BUILDDIR}/include/config/kernel.release)" = "${KERNEL_VERSION}" ] \
        || bbfatal "kernel.release '$(cat ${STAGING_KERNEL_BUILDDIR}/include/config/kernel.release)' != kernel-abiversion '${KERNEL_VERSION}'"
}

do_compile:append() {
    for m in ${NV_KERNEL_MODULES}; do
        ko=${B}/kernel-open/$m.ko
        [ -f "$ko" ] || bbfatal "$m.ko was not produced"
        grep -aFq 'vermagic=${KERNEL_VERSION} ' "$ko" || bbfatal "$m.ko vermagic is not the estate kernel's (${KERNEL_VERSION})"
        grep -aFq '${NV_MODULE_LICENSE_STRING}' "$ko" || bbfatal "$m.ko licence string changed"
    done
    [ ! -e ${B}/kernel-open/nvidia-peermem.ko ] || bbfatal "nvidia-peermem was built despite NV_EXCLUDE_KERNEL_MODULES"
}

do_install:append() {
    for m in ${NV_KERNEL_MODULES}; do
        [ -n "$(find ${D}${nonarch_base_libdir}/modules/${KERNEL_VERSION} -name "$m.ko*" -print -quit)" ] \
            || bbfatal "$m.ko not installed under ${nonarch_base_libdir}/modules/${KERNEL_VERSION}"
    done
    [ -z "$(find ${D} -name 'nvidia-peermem*' -print -quit)" ] || bbfatal "nvidia-peermem must not be installed"
}
