# libggml from the CANONICAL ggml tree (reconstruction v1.1, LLM L1/L2).
#
# llama.cpp embeds a copy of ggml under ggml/ and records the commit it was
# synced from in scripts/sync-ggml.last. Our llama.cpp pin (b10809, SRCREV
# 5266f24da75d) records e91ded11bdcd78c42f9c8d3978ff6686eb4c1226, and
# tools/map-llama-upstreams.py proves the canonical tree at that commit is
# byte-identical to the embedded copy (IDENTICAL). So the estate builds ggml
# ONCE, from its canonical upstream, and llama.cpp links it with
# LLAMA_USE_SYSTEM_GGML=ON instead of compiling a second copy.
#
# Provider ruling: acquisition/provider-decisions.json pending_collisions.ggml
# = RESOLVED-FOR-LLM (libggml from the canonical tree; whisper.cpp and
# stable-diffusion.cpp re-check the pairing when Diffuse is acquired).
SUMMARY = "ggml tensor library (canonical upstream, shared by llama.cpp)"
HOMEPAGE = "https://github.com/ggml-org/ggml"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=223b26b3c1143120c87e2b13111d3e99"

inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-LLM/src/inference/source/ggml"

SRC_URI = "git://github.com/ggml-org/ggml;protocol=https;branch=master"
# v0.23.0 is the release tag at the sync commit (git describe --tags --exact-match)
PV = "0.23.0"
SRCREV = "e91ded11bdcd78c42f9c8d3978ff6686eb4c1226"

inherit cmake pkgconfig

# CUDA arrives ONLY through the estate authority (P7: symoneural-cuda.bbclass ->
# cuda-toolkit-bin 13.4.1, sm_120). The CPU-only build stays selectable
# (PACKAGECONFIG = "") and is what the accepted P9 CPU/native checkpoint proved.
# GGML_CUDA_CUB_3DOT2 stays OFF: it is a FetchContent download, and CUDA 13.4's own
# cccl (CUB 3.3) already satisfies ggml.
PACKAGECONFIG ??= "cuda"
PACKAGECONFIG[cuda] = "-DGGML_CUDA=ON -DGGML_CUDA_CUB_3DOT2=OFF,-DGGML_CUDA=OFF,,"
inherit ${@bb.utils.contains('PACKAGECONFIG', 'cuda', 'symoneural-cuda', '', d)}

# Backends are dlopen'ed MODULES (GGML_BACKEND_DL), not DT_NEEDED libraries. With a
# statically registered CUDA backend libggml.so.0 NEEDs libggml-cuda.so.0, which NEEDs
# libcuda.so.1, and the whole native LLM stack refuses to load on a machine without
# the driver (P7 C6: rc=127 under the target loader with the host cache inhibited).
# As modules under ${libdir}/ggml the CPU backend always loads, the CUDA backend loads
# when the driver's libcuda.so.1 is present, and libsymoneural-llm reports which did.
# GGML_BACKEND_DIR is the install destination and ggml's compiled-in default search
# directory; libsymoneural-llm loads from <its own directory>/ggml first, so ggml's
# executable-directory and cwd fallbacks never run while the packages are intact.
EXTRA_OECMAKE += "-DGGML_BACKEND_DL=ON -DGGML_BACKEND_DIR=${libdir}/ggml"

# Library-only, CPU backend, no build-time network:
#  GGML_NATIVE=OFF        never bake the build host's CPU into a cross artefact
#  GGML_CCACHE=OFF        no host ccache probing
#  GGML_CPU_KLEIDIAI=OFF  the only FetchContent in the CPU backend (Arm-only anyway)
#  GGML_OPENMP_FETCH=OFF  the only file(DOWNLOAD) in src/CMakeLists.txt
#  GGML_OPENMP=ON         libgomp from the toolchain sysroot
#  tests/examples OFF     GGML_STANDALONE defaults them ON; we ship the library
EXTRA_OECMAKE += "-DBUILD_SHARED_LIBS=ON \
                  -DGGML_NATIVE=OFF \
                  -DGGML_CCACHE=OFF \
                  -DGGML_CPU_KLEIDIAI=OFF \
                  -DGGML_OPENMP=ON \
                  -DGGML_OPENMP_FETCH=OFF \
                  -DGGML_BUILD_TESTS=OFF \
                  -DGGML_BUILD_EXAMPLES=OFF"

# x86-64-v3 is the estate's target arch (AVX2/FMA/F16C/BMI2); ggml's
# option defaults follow GGML_NATIVE and would otherwise pick a baseline CPU.
EXTRA_OECMAKE += "-DGGML_AVX=ON -DGGML_AVX2=ON -DGGML_FMA=ON -DGGML_F16C=ON -DGGML_BMI2=ON"

# The CUDA backend module is its own package: the S2 boundary (libcuda.so.1 from the
# host driver) and the cuda-toolkit-bin dependency stop at symoneural-ggml-cuda, and
# the CPU composition is the same image minus that one package. libcuda.so.1 has no
# package provider, so the generic file-rdeps check cannot pass; the class's
# symon_cuda_qa_s2 is the check that stays on (it fails on any other unresolved NEEDED).
PACKAGES =+ "${PN}-cuda"
FILES:${PN}-cuda = "${libdir}/ggml/libggml-cuda*"
RDEPENDS:${PN}-cuda += "${PN}"
INSANE_SKIP:${PN}-cuda += "file-rdeps"
PRIVATE_LIBS:${PN}-cuda += "${SYMON_CUDA_S2_LIBS}"
FILES:${PN} += "${libdir}/libggml*.so ${libdir}/libggml*.so.* ${libdir}/ggml/libggml-cpu*"
FILES:${PN}-dev += "${libdir}/cmake ${libdir}/pkgconfig ${includedir}"
