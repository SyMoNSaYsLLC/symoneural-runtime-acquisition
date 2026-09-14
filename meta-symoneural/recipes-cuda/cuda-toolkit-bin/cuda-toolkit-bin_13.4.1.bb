# NVIDIA CUDA Toolkit 13.4.1 - the estate's ONE CUDA authority (P7; ruling
# unresolved.json:cuda-toolkit-authority). BINARY_EXTERNAL under NVIDIA's EULA: these
# are NVIDIA's own Debian 13 packages, each pinned by the SHA256 the repository index
# publishes (generated/evidence/cuda/CUDA-13.4.1-COMPONENTS.txt records index and
# hashes). No source-built claim is made for anything in this recipe.
#
# Why 13.4.1 (docs/cuda/P7-CUDA-AUTHORITY.md holds the matrix): the host driver
# 615.71.09 is the 13.4-generation driver; the pinned PyTorch 2.14 CI builds 13.4 and
# never 13.3; nvcc 13.4 verifiably accepts the estate's GCC 16.2 host compiler;
# Tune's cuda-python pin is v13.4.1; ggml-cuda is indifferent between the two.
#
# Layout: the toolkit tree is installed whole under ${prefix}/local/cuda-13.4 so
# FindCUDAToolkit and nvcc see NVIDIA's own layout; the runtime .so.* are MOVED to
# ${libdir} (the tree keeps relative symlinks to them) so consumers need no RUNPATH
# and a clean root resolves them on the default loader path. libcuda.so.1 and
# libnvidia-ml.so.1 are NOT here - they come from the host driver at run time (S2);
# only the link-time stubs ship. The Debian ld.so.conf.d drop-ins are not carried.
SUMMARY = "NVIDIA CUDA Toolkit 13.4.1 (binary, NVIDIA EULA) - the estate CUDA authority"
HOMEPAGE = "https://developer.nvidia.com/cuda-toolkit"
LICENSE = "LicenseRef-NVIDIA-CUDA-EULA"
# EULA.txt as shipped inside cuda-documentation-13-4 13.4.49-1 (the same text is
# committed at meta-symoneural/files/custom-licenses/LicenseRef-NVIDIA-CUDA-EULA)
LIC_FILES_CHKSUM = "file://usr/local/cuda-13.4/EULA.txt;md5=a3c52c1f3e8953cbfbc50639ad4b63e1"

NVIDIA_REPO = "https://developer.download.nvidia.com/compute/cuda/repos/debian13/x86_64"
SRC_URI = " \
    ${NVIDIA_REPO}/cuda-nvcc-13-4_13.4.59-1_amd64.deb;name=cuda_nvcc \
    ${NVIDIA_REPO}/cuda-crt-13-4_13.4.59-1_amd64.deb;name=cuda_crt \
    ${NVIDIA_REPO}/libnvvm-13-4_13.4.59-1_amd64.deb;name=libnvvm \
    ${NVIDIA_REPO}/libnvptxcompiler-13-4_13.4.59-1_amd64.deb;name=libnvptxcompiler \
    ${NVIDIA_REPO}/cuda-cuobjdump-13-4_13.4.49-1_amd64.deb;name=cuda_cuobjdump \
    ${NVIDIA_REPO}/cuda-cuxxfilt-13-4_13.4.49-1_amd64.deb;name=cuda_cuxxfilt \
    ${NVIDIA_REPO}/cuda-nvprune-13-4_13.4.49-1_amd64.deb;name=cuda_nvprune \
    ${NVIDIA_REPO}/cuda-cudart-13-4_13.4.49-1_amd64.deb;name=cuda_cudart \
    ${NVIDIA_REPO}/cuda-cudart-dev-13-4_13.4.49-1_amd64.deb;name=cuda_cudart_dev \
    ${NVIDIA_REPO}/cuda-driver-dev-13-4_13.4.49-1_amd64.deb;name=cuda_driver_dev \
    ${NVIDIA_REPO}/cuda-culibos-dev-13-4_13.4.49-1_amd64.deb;name=cuda_culibos_dev \
    ${NVIDIA_REPO}/cccl-13-4_13.3.4.2.1-1_amd64.deb;name=cccl \
    ${NVIDIA_REPO}/cuda-nvrtc-13-4_13.4.59-1_amd64.deb;name=cuda_nvrtc \
    ${NVIDIA_REPO}/cuda-nvrtc-dev-13-4_13.4.59-1_amd64.deb;name=cuda_nvrtc_dev \
    ${NVIDIA_REPO}/libcublas-13-4_13.7.0.27-1_amd64.deb;name=libcublas \
    ${NVIDIA_REPO}/libcublas-dev-13-4_13.7.0.27-1_amd64.deb;name=libcublas_dev \
    ${NVIDIA_REPO}/libcufft-13-4_12.4.0.34-1_amd64.deb;name=libcufft \
    ${NVIDIA_REPO}/libcufft-dev-13-4_12.4.0.34-1_amd64.deb;name=libcufft_dev \
    ${NVIDIA_REPO}/libcurand-13-4_10.4.4.49-1_amd64.deb;name=libcurand \
    ${NVIDIA_REPO}/libcurand-dev-13-4_10.4.4.49-1_amd64.deb;name=libcurand_dev \
    ${NVIDIA_REPO}/libcusolver-13-4_12.3.2.15-1_amd64.deb;name=libcusolver \
    ${NVIDIA_REPO}/libcusolver-dev-13-4_12.3.2.15-1_amd64.deb;name=libcusolver_dev \
    ${NVIDIA_REPO}/libcusparse-13-4_12.8.6.49-1_amd64.deb;name=libcusparse \
    ${NVIDIA_REPO}/libcusparse-dev-13-4_12.8.6.49-1_amd64.deb;name=libcusparse_dev \
    ${NVIDIA_REPO}/libnvjitlink-13-4_13.4.52-1_amd64.deb;name=libnvjitlink \
    ${NVIDIA_REPO}/libnvjitlink-dev-13-4_13.4.52-1_amd64.deb;name=libnvjitlink_dev \
    ${NVIDIA_REPO}/cuda-nvtx-13-4_13.4.49-1_amd64.deb;name=cuda_nvtx \
    ${NVIDIA_REPO}/cuda-profiler-api-13-4_13.4.49-1_amd64.deb;name=cuda_profiler_api \
    ${NVIDIA_REPO}/cuda-nvml-dev-13-4_13.4.61-1_amd64.deb;name=cuda_nvml_dev \
    ${NVIDIA_REPO}/cuda-cupti-13-4_13.4.58-1_amd64.deb;name=cuda_cupti \
    ${NVIDIA_REPO}/cuda-cupti-dev-13-4_13.4.58-1_amd64.deb;name=cuda_cupti_dev \
    ${NVIDIA_REPO}/cuda-toolkit-13-4_13.4.1-1_amd64.deb;name=cuda_toolkit \
    ${NVIDIA_REPO}/cuda-documentation-13-4_13.4.49-1_amd64.deb;name=cuda_documentation \
"
SRC_URI[cuda_nvcc.sha256sum] = "785ef7d36e816e1c900151a12ea89e2cee46341763451f9a2fb4f88b8a4cb408"
SRC_URI[cuda_crt.sha256sum] = "b592c1d3ebde89c1532724fecafe864137785c205ef5856cbe21297f8ef02e26"
SRC_URI[libnvvm.sha256sum] = "ba6776060918182fcf32a52f1ac38207e2b0f475c22c4f88a1d8d38e783107f7"
SRC_URI[libnvptxcompiler.sha256sum] = "0ff6cf73cb15adc9909d853878e9aec04bf17904be6d707782de09a2c64286c7"
SRC_URI[cuda_cuobjdump.sha256sum] = "eba85253516218bab686119badde05d2b901d183c4eaae884dbef2b6f3e68f6e"
SRC_URI[cuda_cuxxfilt.sha256sum] = "8576f7e4ab50f0e428ce41a9d33d4b4116f1cfb3d3977c0ca4ab9323e5a61d9e"
SRC_URI[cuda_nvprune.sha256sum] = "53a30da7484e62941fb6d0cdb31d8dd367a02ba3ed0240d749d23917de0977cc"
SRC_URI[cuda_cudart.sha256sum] = "36a28d919e012ad4a2e3e34199bae057be958241e86e9b14e751aadc190bfbd2"
SRC_URI[cuda_cudart_dev.sha256sum] = "74af55d4183173ed16e9a8e6d8a0949cdef3058466e184a5271b38e31d52aca5"
SRC_URI[cuda_driver_dev.sha256sum] = "7714a88bc872271858da9d84d3fafbad5624de767e0b1e89b7b036b37c365a7f"
SRC_URI[cuda_culibos_dev.sha256sum] = "4df11d998e1178185c72cd9e4e4f6274157bd54641b3b858091f2264962e9970"
SRC_URI[cccl.sha256sum] = "a0910963b40ae631aa7f8199b7877c6ce54e95a2b7c252a37d9122dd629baee1"
SRC_URI[cuda_nvrtc.sha256sum] = "aeb9962c55e09a2555d7bbfd96fbe1edbb2789d29760ada66c56a4685d233f23"
SRC_URI[cuda_nvrtc_dev.sha256sum] = "d35ebc6f38a603c8c7888eca7650794ecc732465b6c808d1a432e42580a679b4"
SRC_URI[libcublas.sha256sum] = "a4abaccf6e3e84ce59a548cdaf1c6eca8bf32f089bd88f83b61bd0fbbfd52b70"
SRC_URI[libcublas_dev.sha256sum] = "3608619f7623ccd173a1ba8eee44835a5fd271de8ce81a93b022d8ee79a37133"
SRC_URI[libcufft.sha256sum] = "871832cd9811badcbbc7fd9327fc320e1285ccd30226232d581548c60bba1573"
SRC_URI[libcufft_dev.sha256sum] = "2ec43f8c580ce5291e9a70a53dc3257a99a2002d5e5f4e4d3044fd1508761878"
SRC_URI[libcurand.sha256sum] = "a51e236ccf5ec056c91a19431044d01bc12be59a88bf2f330e795cdcb80e0d67"
SRC_URI[libcurand_dev.sha256sum] = "20bcd990e0e7a1ff4667ba506483a09b5376613088aefb772c5bca0eb046234d"
SRC_URI[libcusolver.sha256sum] = "5a5bb997df7ee660bf91eb58ab08a884be79e489578c2623d2b1a32b7c5813c8"
SRC_URI[libcusolver_dev.sha256sum] = "fd631986323029892449ce5aed30fac4006b31d42f73f1051b50c3f1a2c6d1ba"
SRC_URI[libcusparse.sha256sum] = "33afebd5257fc6f680aa79f7c79cd2da6f9bcc45c9f5403191def34420cb37d6"
SRC_URI[libcusparse_dev.sha256sum] = "09a281df1cf6eb41440fc16e838bc78d6b6e3d07d6b69f7874a1ecf45617f205"
SRC_URI[libnvjitlink.sha256sum] = "0ce03afa84876aa193465c60f7e38e55350c4cf55d0d016e17c383adf5d162a6"
SRC_URI[libnvjitlink_dev.sha256sum] = "ac7f1e11d4c6bb4f8d8fbdd808a091f6d272bd96f6f4bcea12ae2d44405a2c38"
SRC_URI[cuda_nvtx.sha256sum] = "a34be1fa3d1bbb64d74b184bf97219474a5511752fd555a7c88dd1c1dd3c8929"
SRC_URI[cuda_profiler_api.sha256sum] = "95a9ec122d0d675bc7b14ab31e20992692c109c773b685f92a92fab5b2126011"
SRC_URI[cuda_nvml_dev.sha256sum] = "f059669c1cccc8ae9b796053958bd9aa85138f7a2a9ad5a911e858bb14f487b3"
SRC_URI[cuda_cupti.sha256sum] = "555949ebdb216c0de4caf367c131d8b1b3357cdf05a130a17a5718e843515727"
SRC_URI[cuda_cupti_dev.sha256sum] = "03ed500926ebcb7a9fbe39a3cbb8bf699470335e656a48d0015461f1bff978ce"
SRC_URI[cuda_toolkit.sha256sum] = "d22afceef650970cbfb5f3f996c51c9b55ebf4c0568d1a3d78334fca38900ecb"
SRC_URI[cuda_documentation.sha256sum] = "c6639fa4e3bd76d375b3baf150b7faad4c2ec4de51a21ee815987eac7e626da9"

S = "${UNPACKDIR}"
CUDA_TREE = "usr/local/cuda-13.4"

# OE stages only SYSROOT_DIRS into a consumer's sysroots (/usr/lib, /usr/include, ...);
# the toolkit tree lives under /usr/local, so it must be named for both variants -
# nvcc/nvvm in the native sysroot, headers/static libs/cmake in the target sysroot.
SYSROOT_DIRS += "${prefix}/local"
SYSROOT_DIRS_NATIVE += "${prefix}/local"

# NVIDIA's binaries are consumed as shipped: not stripped, not debug-split, not re-linked
INHIBIT_PACKAGE_STRIP = "1"
INHIBIT_PACKAGE_DEBUG_SPLIT = "1"
INHIBIT_SYSROOT_STRIP = "1"
INHIBIT_DEFAULT_DEPS = "1"

do_configure[noexec] = "1"
do_compile[noexec] = "1"

do_install() {
    install -d ${D}${prefix}/local ${D}${libdir}
    cp -a ${S}/${CUDA_TREE} ${D}${prefix}/local/
    ln -sf cuda-13.4 ${D}${prefix}/local/cuda
    # Every shared-object name (real file, SONAME link, unversioned link) moves onto the
    # default loader path; the tree keeps a relative link for each so NVIDIA's own layout
    # still resolves for FindCUDAToolkit and nvcc. The tree's lib dir ends up holding only
    # links, static archives and the link-time stubs.
    tree=${D}${prefix}/local/cuda-13.4/targets/x86_64-linux/lib
    for f in $tree/*.so*; do
        case "$f" in *.a) continue ;; esac
        [ -e "$f" ] || [ -L "$f" ] || continue
        n=$(basename "$f")
        if [ -L "$f" ]; then
            t=$(readlink "$f"); rm "$f"; ln -s "$t" ${D}${libdir}/$n
        else
            mv "$f" ${D}${libdir}/$n
        fi
        ln -s ../../../../../lib/$n "$f"
    done
    # the payload was extracted as the build user; packaged files are root's
    chown -R root:root ${D}
}

PACKAGES = "${PN} ${PN}-dev"
FILES:${PN} = "${libdir}/*.so.* ${prefix}/local/cuda-13.4/version.json ${prefix}/local/cuda-13.4/EULA.txt"
FILES:${PN}-dev = "${prefix}/local/cuda-13.4 ${prefix}/local/cuda ${libdir}/*.so"
RDEPENDS:${PN}-dev = "${PN}"

# QA on vendor binaries, each skip named: they are not built here, so the checks
# that describe how WE build do not apply. buildpaths is NOT skipped.
INSANE_SKIP:${PN} = "already-stripped ldflags textrel arch file-rdeps"
INSANE_SKIP:${PN}-dev = "already-stripped ldflags textrel arch file-rdeps dev-so staticdev dev-elf libdir"
# file provides ARE generated for the runtime package: consumers' file-rdeps QA
# resolves libcudart.so.13 & co. through them. -dev is excluded from providers, so
# its 2 GB of files are not scanned.
SKIP_FILEDEPS:${PN}-dev = "1"
# libcuda.so.1 / libnvidia-ml.so.1 are host-driver-provided; nothing in the feed
# provides them and nothing should. -dev is never a shared-library PROVIDER: it holds
# only links, static archives, the compiler and the link-time libcuda stub, and that
# stub must not make a consumer RDEPEND on -dev for a library the driver supplies.
PRIVATE_LIBS:${PN} = "libcuda.so.1 libnvidia-ml.so.1"
EXCLUDE_PACKAGES_FROM_SHLIBS = "${PN}-dev"

BBCLASSEXTEND = "native"
