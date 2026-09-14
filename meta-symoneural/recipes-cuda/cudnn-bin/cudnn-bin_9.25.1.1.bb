# NVIDIA cuDNN for CUDA 13 - BINARY_EXTERNAL, a provider SEPARATE from the generic
# CUDA authority (cuda-toolkit-bin). Ruling: Garrett 2026-09-14 (P7 C7): cuDNN is used
# for the final PyTorch CUDA feature set, is not source-built, does not join
# cuda-toolkit-bin, is pinned to exact packages + SHA256 from the same controlled
# NVIDIA Debian 13 repository index the toolkit uses, carries its own licence, and
# never binds to a host-installed cuDNN.
#
# Version: the pinned PyTorch tree's CI pairs CUDA 13.4 with cuDNN 9.25.0.15
# (.ci/docker/common/install_cuda.sh install_134). The index (sha256 769ece57...)
# offers 9.25.1.1 and 9.26.0.51 for cuda-13; 9.25.1.1 is the smallest on the 9.25
# line. Runtime + dev (SONAME links) + headers only: static and jit (runtime-compiled
# engines) packages are not taken - optional libraries are not enabled because they exist.
SUMMARY = "NVIDIA cuDNN 9 for CUDA 13 (binary, NVIDIA Debian 13 repository)"
HOMEPAGE = "https://developer.nvidia.com/cudnn"
# NVIDIA "LICENSE AGREEMENT FOR NVIDIA SOFTWARE DEVELOPMENT KITS" - the copyright file every
# cuDNN package carries (identical in all three, md5 6309a40f...); text committed under
# meta-symoneural/files/custom-licenses/ and shipped with the runtime package.
LICENSE = "LicenseRef-NVIDIA-cuDNN-SLA"
LIC_FILES_CHKSUM = "file://usr/share/doc/libcudnn9-cuda-13/copyright;md5=6309a40f44d0c8b8cd8950ef80691561"

NVIDIA_REPO = "https://developer.download.nvidia.com/compute/cuda/repos/debian13/x86_64"
SRC_URI = " \
    ${NVIDIA_REPO}/libcudnn9-cuda-13_9.25.1.1-1_amd64.deb;name=rt \
    ${NVIDIA_REPO}/libcudnn9-dev-cuda-13_9.25.1.1-1_amd64.deb;name=dev \
    ${NVIDIA_REPO}/libcudnn9-headers-cuda-13_9.25.1.1-1_amd64.deb;name=headers \
"
SRC_URI[rt.sha256sum] = "f25c6ee3e610680754dbe55e745580219d381813c8727e3c4e41bc8c9b043078"
SRC_URI[dev.sha256sum] = "f140d27ad2aab673bf7ef4de4fd644905bb7ccb9975a35520c8a7609b9c1fb1b"
SRC_URI[headers.sha256sum] = "093c102de6adcd46b157d0a539cdbe689b180f0064d9ea1edc91703bc64de03b"

S = "${UNPACKDIR}"
COMPATIBLE_HOST = "x86_64.*-linux"
# Prebuilt, but its NEEDED set (libz, libstdc++, libgcc_s, glibc) must resolve to
# packages: keep the default toolchain DEPENDS and add zlib so package_do_shlibs can
# see every provider and write RDEPENDS. (Inhibiting default deps left the runtime
# package with no Depends at all - the first build's file-rdeps errors.)
DEPENDS = "zlib"
INHIBIT_PACKAGE_STRIP = "1"
INHIBIT_PACKAGE_DEBUG_SPLIT = "1"
INHIBIT_SYSROOT_STRIP = "1"
do_configure[noexec] = "1"
do_compile[noexec] = "1"

# Debian multiarch layout in, OE layout out: the .so.9 chains move onto ${libdir} so
# consumers resolve them on the default loader path with no RUNPATH; headers onto
# ${includedir} (FindCUDNN looks for cudnn.h / cudnn_version.h there). The fetcher
# extracts the payload as the build user; sstate's output-hash walker needs root:root.
do_install() {
    install -d ${D}${libdir} ${D}${includedir} ${D}${datadir}/doc/${PN}
    cp -a ${S}/usr/lib/x86_64-linux-gnu/libcudnn*.so* ${D}${libdir}/
    install -m 0644 ${S}/usr/include/x86_64-linux-gnu/cudnn*.h ${D}${includedir}/
    install -m 0644 ${S}/usr/share/doc/libcudnn9-cuda-13/copyright ${D}${datadir}/doc/${PN}/LICENSE-NVIDIA-SDK
    chown -R root:root ${D}
}

PACKAGES = "${PN} ${PN}-dev"
FILES:${PN} = "${libdir}/libcudnn*.so.* ${datadir}/doc/${PN}"
FILES:${PN}-dev = "${libdir}/libcudnn*.so ${includedir}"
# vendor binaries: prebuilt, already stripped, not linked with OE's LDFLAGS; buildpaths is NOT skipped
INSANE_SKIP:${PN} = "already-stripped ldflags textrel arch"
INSANE_SKIP:${PN}-dev = "dev-so"
