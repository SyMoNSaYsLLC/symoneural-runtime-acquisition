# DEBIAN TARGET (A): NVIDIA open GPU kernel modules for the development machine's kernel ABI
# 6.12.107+deb13-amd64 (Debian 13, an EXTERNAL kernel in this profile), built from the same
# pinned tree as the estate target, against the pinned Debian kernel inputs staged by
# debian-kernel-inputs-6.12.107+deb13-amd64 (SYSSRC = common tree, SYSOUT = arch tree) with the
# compiler identity the kernel .config records (x86_64-linux-gnu-gcc-14, Debian 14.2.0-19), taken
# from the host through the build directory's HOSTTOOLS. HOST-CONDITIONED: the toolchain and
# Debian's prebuilt kbuild helpers come from the host at the index-recorded versions, so BUILD and
# PACKAGE can PASS while REPRODUCIBILITY stays NOT TESTED.
#
# The package is a .deb (package_deb) whose name carries the kernel ABI, installs under its own
# path (updates/symoneural), Depends on exactly this kernel and on the GSP firmware package of the
# same driver generation, and Conflicts with NVIDIA's DKMS packages that ship same-named modules.
# UNSIGNED: Secure Boot is on and the host's modules are MOK-signed; no key is read, made or used
# here. It is never installed on the host by this work (docs/platform/NVIDIA-OPEN-KERNEL.md).
require symoneural-nvidia-open-kernel.inc
SUMMARY = "NVIDIA open GPU kernel modules ${PV} for Debian ${DEB_KABI} (source-built, unsigned, HOST-CONDITIONED)"

inherit symoneural-pristine
B = "${S}"

DEB_KABI = "6.12.107+deb13-amd64"
DEB_KVER = "6.12.107-1"
# NVIDIA's Debian 13 repository version of the userspace/firmware stack this module set belongs to
# (index sha256 769ece572c8ac8998c02859ae4fb2f1e0b9c2762639fe8ea493c1741aadd70ca).
NV_DEB_STACK = "615.71.09-2"
# Debian 13 is merged-/usr and linux-image records its module tree under /usr/lib/modules.
DEB_MODDIR = "/usr/lib/modules/${DEB_KABI}/updates/symoneural"

DEPENDS = "debian-kernel-inputs-${DEB_KABI}"
INHIBIT_DEFAULT_DEPS = "1"

NV_SYSSRC = "${STAGING_DIR_TARGET}${prefix}/src/linux-headers-6.12.107+deb13-common"
NV_SYSOUT = "${STAGING_DIR_TARGET}${prefix}/src/linux-headers-${DEB_KABI}"
NV_HOST_PREFIX = "x86_64-linux-gnu-"
NV_HOST_CC = "${NV_HOST_PREFIX}gcc-14"
NV_HOST_CC_IDENT = "x86_64-linux-gnu-gcc-14 (Debian 14.2.0-19) 14.2.0"

# package.bbclass strips and splits debug info with STRIP/OBJCOPY: the same declared Debian
# binutils, never the estate cross tools (which this recipe does not depend on).
STRIP = "${NV_HOST_PREFIX}strip"
OBJCOPY = "${NV_HOST_PREFIX}objcopy"
PACKAGE_DEBUG_SPLIT_STYLE = "debug-without-src"

do_compile() {
    unset CFLAGS CPPFLAGS CXXFLAGS LDFLAGS
    # OE exports its cross toolchain names (CC=x86_64-oe-linux-gcc ...). This profile builds with the
    # Debian kernel's own compiler identity and nothing else: drop the exports so every tool used is
    # one named on the command line below.
    unset CC CXX CPP LD CCLD AR AS NM RANLIB STRIP OBJCOPY OBJDUMP READELF \
          BUILD_CC BUILD_CXX BUILD_CPP BUILD_LD BUILD_AR BUILD_NM BUILD_STRIP BUILD_RANLIB BUILD_OBJCOPY BUILD_OBJDUMP BUILD_READELF

    [ -f "${NV_SYSSRC}/Makefile" ] || bbfatal "Debian common kernel tree missing from the sysroot: ${NV_SYSSRC}"
    for f in .config .kernelvariables Module.symvers vmlinux arch/x86/module.lds include/generated/utsrelease.h include/config/auto.conf; do
        [ -e "${NV_SYSOUT}/$f" ] || bbfatal "Debian kernel output tree lacks $f: ${NV_SYSOUT}"
    done
    grep -Fxq 'CONFIG_CC_VERSION_TEXT="${NV_HOST_CC_IDENT}"' ${NV_SYSOUT}/.config \
        || bbfatal "kernel .config compiler identity is not '${NV_HOST_CC_IDENT}'"
    grep -Fxq '#define UTS_RELEASE "${DEB_KABI}"' ${NV_SYSOUT}/include/generated/utsrelease.h \
        || bbfatal "UTS_RELEASE is not ${DEB_KABI}"
    have=$(${NV_HOST_CC} --version | head -1)
    [ "$have" = "${NV_HOST_CC_IDENT}" ] || bbfatal "declared host compiler is not '${NV_HOST_CC_IDENT}': '$have'"

    # SYSSRC/SYSOUT/KERNEL_UNAME explicit: NVIDIA's wrapper never reaches its `uname -r` /
    # /lib/modules fallback. ARCH=x86_64 for NVIDIA's own test (kbuild remaps; Debian's
    # .kernelvariables also overrides ARCH=x86, KERNELRELEASE=${DEB_KABI}, CROSS_COMPILE=x86_64-linux-gnu-).
    # KCFLAGS reaches kbuild's KBUILD_CFLAGS; EXTRA_CFLAGS reaches utils.mk (nv-kernel.o, nv-modeset-kernel.o)
    # and kbuild's ccflags-y: OE's prefix maps so no build, sysroot or work path is embedded.
    oe_runmake -C ${S} \
        SYSSRC=${NV_SYSSRC} SYSOUT=${NV_SYSOUT} KERNEL_UNAME=${DEB_KABI} \
        ARCH=x86_64 TARGET_ARCH=x86_64 TARGET_OS=Linux \
        CC=${NV_HOST_CC} HOSTCC=${NV_HOST_CC} CROSS_COMPILE=${NV_HOST_PREFIX} \
        LD=${NV_HOST_PREFIX}ld AR=${NV_HOST_PREFIX}ar NM=${NV_HOST_PREFIX}nm \
        OBJCOPY=${NV_HOST_PREFIX}objcopy OBJDUMP=${NV_HOST_PREFIX}objdump \
        STRIP=${NV_HOST_PREFIX}strip READELF=${NV_HOST_PREFIX}readelf \
        NV_EXCLUDE_KERNEL_MODULES=${NV_EXCLUDE_KERNEL_MODULES} ${NV_BUILD_IDENTITY} NV_VERBOSE=1 \
        KCFLAGS="${DEBUG_PREFIX_MAP}" EXTRA_CFLAGS="${DEBUG_PREFIX_MAP}" \
        modules

    for m in ${NV_KERNEL_MODULES}; do
        ko=${B}/kernel-open/$m.ko
        [ -f "$ko" ] || bbfatal "$m.ko was not produced"
        grep -aFq 'vermagic=${DEB_KABI} SMP preempt mod_unload modversions' "$ko" \
            || bbfatal "$m.ko vermagic is not the Debian ABI ${DEB_KABI}"
        grep -aFq '${NV_MODULE_LICENSE_STRING}' "$ko" || bbfatal "$m.ko licence string changed"
    done
    [ ! -e ${B}/kernel-open/nvidia-peermem.ko ] || bbfatal "nvidia-peermem was built despite NV_EXCLUDE_KERNEL_MODULES"
}

do_install() {
    install -d ${D}${DEB_MODDIR}
    for m in ${NV_KERNEL_MODULES}; do
        install -m 0644 ${B}/kernel-open/$m.ko ${D}${DEB_MODDIR}/
    done
    install -Dm 0644 ${B}/kernel-open/Module.symvers ${D}${includedir}/${BPN}/Module.symvers
    sed -i 's:${B}/::g' ${D}${includedir}/${BPN}/Module.symvers
}

PACKAGES = "${PN}-dbg ${PN}-dev ${PN}"
PKG:${PN} = "symoneural-nvidia-open-kernel-${DEB_KABI}"
PKG:${PN}-dev = "symoneural-nvidia-open-kernel-${DEB_KABI}-dev"
PKG:${PN}-dbg = "symoneural-nvidia-open-kernel-${DEB_KABI}-dbg"
FILES:${PN} = "${DEB_MODDIR}"
FILES:${PN}-dev = "${includedir}"

# Debian-side coupling: exactly this kernel ABI/version, and the GSP firmware the modules request at
# load (modinfo firmware: nvidia/615.71.09/gsp_*.bin) from the same driver generation. Both are
# Debian/NVIDIA packages, not estate recipes, so they are written as the .deb's own Depends field
# (package_deb's PACKAGE_ADD_METADATA_DEB) rather than as RDEPENDS: BitBake's run queue requires an
# in-build provider for every RDEPENDS name ("Nothing RPROVIDES 'firmware-nvidia-gsp'", first build).
# The package has no OE runtime dependencies of its own (a .ko has no NEEDED entries).
PACKAGE_ADD_METADATA_DEB:${PN} = "Depends: linux-image-${DEB_KABI} (= ${DEB_KVER}), firmware-nvidia-gsp (= ${NV_DEB_STACK})"
# NVIDIA's DKMS packages install same-named modules under updates/dkms of the same kernel;
# co-installation would leave depmod to pick one. Declared, never exercised on the host.
RCONFLICTS:${PN} = "nvidia-kernel-open-dkms nvidia-kernel-dkms nvidia-kernel-${PV}"

pkg_postinst:${PN}() {
    # Debian convention for module packages: refresh the module index on the target only.
    [ -n "$D" ] || depmod -a ${DEB_KABI}
}
pkg_postrm:${PN}() {
    [ -n "$D" ] || depmod -a ${DEB_KABI}
}
