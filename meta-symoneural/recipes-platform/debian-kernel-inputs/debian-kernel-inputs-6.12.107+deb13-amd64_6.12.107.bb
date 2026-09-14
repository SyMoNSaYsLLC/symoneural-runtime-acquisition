# Debian 13 (trixie) kernel ABI 6.12.107+deb13-amd64: the exact header / kbuild closure an external
# module build against that kernel needs, plus the signed kernel image for the staged-install
# proof. Every input is fetched by the SHA256 the trixie/main index publishes (index sha256
# 4f2c68d67001d595fbd343f6dbad44468953a51c4d9dec3a4803249f6e295940 - Debian 13.7, InRelease
# 12 Sep 2026; re-verified against /var/lib/apt/lists on 2026-09-14), staged into the TARGET
# SYSROOT under their Debian paths so a module build sees exactly the layout the Debian kernel
# expects (relative scripts/ and tools/ symlinks into linux-kbuild), and deployed unchanged for
# the staged-install proof. NOTHING IS PACKAGED: these are Debian-provided BUILD INPUTS of the
# Debian profile (docs/platform/NVIDIA-OPEN-KERNEL.md section 2A), not SyMoNeuRaL deliverables.
#
# The kbuild helpers inside linux-kbuild (fixdep, modpost, genksyms, objtool, resolve_btfids) are
# Debian-built host executables: using them makes the module build HOST-CONDITIONED, together
# with the host gcc-14/binutils/pahole declared in the build directory's HOSTTOOLS.
SUMMARY = "Debian linux-headers / linux-kbuild / linux-image 6.12.107+deb13-amd64 (6.12.107-1) as pinned build inputs"
HOMEPAGE = "https://packages.debian.org/trixie/linux-headers-6.12.107+deb13-amd64"
LICENSE = "GPL-2.0-only"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/GPL-2.0-only;md5=801f80980d171dd6425610833a22dbe6"

DEB_KABI = "6.12.107+deb13-amd64"
DEB_KVER = "6.12.107-1"
DEB_KBUILD = "linux-kbuild-6.12.107+deb13"
DEB_COMMON = "linux-headers-6.12.107+deb13-common"
DEBIAN_POOL = "https://deb.debian.org/debian/pool/main"

SRC_URI = " \
    ${DEBIAN_POOL}/l/linux/linux-headers-${DEB_KABI}_${DEB_KVER}_amd64.deb;name=hdr;subdir=hdr \
    ${DEBIAN_POOL}/l/linux/${DEB_COMMON}_${DEB_KVER}_all.deb;name=common;subdir=common \
    ${DEBIAN_POOL}/l/linux/${DEB_KBUILD}_${DEB_KVER}_amd64.deb;name=kbuild;subdir=kbuild \
    ${DEBIAN_POOL}/l/linux-signed-amd64/linux-image-${DEB_KABI}_${DEB_KVER}_amd64.deb;name=image;subdir=image \
"
SRC_URI[hdr.sha256sum] = "0ab746a3d854ad0e666923147842d1e629cdb3e29a97b76ae25b4911285174e4"
SRC_URI[common.sha256sum] = "12dc292d7c238928fbcb7eebbe79208758fe263a4e2ea0e9b6734e6df12020a5"
SRC_URI[kbuild.sha256sum] = "0a88527eb05bca1ce75e7d39ec27539d385a24cf90b2b28917cc4903a4f710d3"
SRC_URI[image.sha256sum] = "7794643cf4560de2a7e3b069e8ca8511ad2a568d652ea285f0fe051f79bc9e99"

S = "${UNPACKDIR}"
COMPATIBLE_HOST = "x86_64.*-linux"

INHIBIT_DEFAULT_DEPS = "1"
INHIBIT_PACKAGE_STRIP = "1"
INHIBIT_SYSROOT_STRIP = "1"
INHIBIT_PACKAGE_DEBUG_SPLIT = "1"

inherit nopackages deploy

do_configure[noexec] = "1"
do_compile[noexec] = "1"

# /usr/src is not part of OE's default sysroot set; the kernel trees live there on Debian.
SYSROOT_DIRS += "${prefix}/src"

# The compiler identity the kernel .config records - the module build declares exactly this
# compiler; a changed input must fail here, plainly, not deep inside conftest.
DEB_KERNEL_CC_IDENT = "x86_64-linux-gnu-gcc-14 (Debian 14.2.0-19) 14.2.0"

do_install() {
    install -d ${D}${prefix}/src ${D}${libdir}
    cp -a ${S}/common/usr/src/${DEB_COMMON} ${D}${prefix}/src/
    cp -a ${S}/hdr/usr/src/linux-headers-${DEB_KABI} ${D}${prefix}/src/
    cp -a ${S}/kbuild/usr/lib/${DEB_KBUILD} ${D}${libdir}/

    out=${D}${prefix}/src/linux-headers-${DEB_KABI}
    grep -Fxq 'CONFIG_CC_VERSION_TEXT="${DEB_KERNEL_CC_IDENT}"' $out/.config \
        || bbfatal "linux-headers-${DEB_KABI}: .config compiler identity is not '${DEB_KERNEL_CC_IDENT}'"
    grep -Fxq 'override KERNELRELEASE = ${DEB_KABI}' $out/.kernelvariables \
        || bbfatal "linux-headers-${DEB_KABI}: .kernelvariables does not pin KERNELRELEASE ${DEB_KABI}"
    grep -Fxq '#define UTS_RELEASE "${DEB_KABI}"' $out/include/generated/utsrelease.h \
        || bbfatal "linux-headers-${DEB_KABI}: UTS_RELEASE is not ${DEB_KABI}"
    for f in Module.symvers vmlinux arch/x86/module.lds include/config/auto.conf; do
        [ -e $out/$f ] || bbfatal "linux-headers-${DEB_KABI}: $f missing (needed by modpost / BTF / module link)"
    done
    for f in scripts/basic/fixdep scripts/mod/modpost scripts/genksyms/genksyms tools/objtool/objtool tools/bpf/resolve_btfids/resolve_btfids; do
        [ -x ${D}${libdir}/${DEB_KBUILD}/$f ] || bbfatal "${DEB_KBUILD}: $f missing or not executable"
    done
    # the arch tree reaches kbuild through RELATIVE symlinks; they must resolve inside ${D} as staged
    [ -x $out/scripts/mod/modpost ] || bbfatal "linux-headers-${DEB_KABI}: scripts symlink does not resolve to ${DEB_KBUILD}"
    chown -R root:root ${D}
}

# The four debs, byte-for-byte as fetched, for the isolated staged-install proof
# (tools/nvidia-open-kernel-proof debian): the module package is installed into a disposable
# root beside linux-image's module metadata, never onto the host.
do_deploy() {
    install -d ${DEPLOYDIR}/debian-kernel-inputs
    for f in linux-headers-${DEB_KABI}_${DEB_KVER}_amd64.deb ${DEB_COMMON}_${DEB_KVER}_all.deb \
             ${DEB_KBUILD}_${DEB_KVER}_amd64.deb linux-image-${DEB_KABI}_${DEB_KVER}_amd64.deb; do
        install -m 0644 ${DL_DIR}/$f ${DEPLOYDIR}/debian-kernel-inputs/$f
    done
    ( cd ${DEPLOYDIR}/debian-kernel-inputs && sha256sum *.deb > SHA256SUMS )
}
addtask deploy after do_install
