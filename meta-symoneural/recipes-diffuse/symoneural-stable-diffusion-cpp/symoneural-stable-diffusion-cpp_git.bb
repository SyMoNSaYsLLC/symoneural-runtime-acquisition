# stable-diffusion.cpp - the Diffuse runtime's image engine (Phase 14 item 14a).
#
# Diffusion inference in C++ against a GGUF model, CUDA through the estate authority.
# Packages sd-cli, which is what the image and sigils units launch (Phase 14 item 14d:
# sd-cli --backend te=cpu --vae-tiling --diffusion-fa, 4 steps, cfg 1.0, euler).
#
# WHY THIS BUILDS ITS OWN ggml, AND WHY THAT IS NOT A SHORTCUT (Phase 14 S1).
# The pending_collisions.ggml ruling is RESOLVED-FOR-LLM: llama.cpp links the canonical
# ggml because tools/map-llama-upstreams.py proved the embedded copy byte-identical to
# ggml-org/ggml at e91ded11bdcd. sd.cpp is NOT that case, and two facts in the source
# settle it rather than a preference:
#
#   1. VERSION. The estate's symoneural-ggml is canonical ggml 0.23.0. The submodule
#      here is leejet/ggml (a personal fork of ggml-org/ggml) on branch sd.cpp at
#      e20c3a14aa70, whose CMakeLists declares GGML_VERSION 0.19.0. Different trees,
#      four minor versions apart.
#   2. ABI. CMakeLists.txt does `if (NOT SD_USE_SYSTEM_GGML) add_definitions(-DGGML_MAX_NAME=160)`.
#      Upstream ggml's default is 64. GGML_MAX_NAME sizes the `name` array inside
#      struct ggml_tensor, so a system ggml compiled at 64 and an sd.cpp compiled at 160
#      disagree on sizeof(struct ggml_tensor). That is not a link error; it is silent
#      memory corruption.
#
# So SD_USE_SYSTEM_GGML stays OFF, the vendored fork is built, and the three-way
# collision stays recorded UNRESOLVED exactly as Phase 14 S1 says. There are then two
# libggml codebases in the estate; neither is loaded into the other's process.
SUMMARY = "stable-diffusion.cpp - diffusion inference in C/C++ (Diffuse: image, sigils)"
DESCRIPTION = "Image generation from GGUF diffusion models. Provides sd-cli, the launch \
binary for the Diffuse runtime's image and sigils units, built with the estate CUDA \
authority for Blackwell sm_120."
HOMEPAGE = "https://github.com/leejet/stable-diffusion.cpp"

# MIT        stable-diffusion.cpp itself, and the vendored ggml fork
# BSD-3      thirdparty/libwebp and thirdparty/libwebm (identical licence text, same md5)
# Unlicense  thirdparty/zip.c (kuba--/zip). It carries only the warranty clause in its
#            header and ships no licence file of its own, so it has no LIC_FILES_CHKSUM
#            entry; it is declared here rather than left unstated.
# thirdparty/json.hpp (nlohmann) and thirdparty/httplib.h are both MIT, SPDX-tagged
# in-file, covered by the MIT term.
LICENSE = "BSD-3-Clause AND MIT AND Unlicense"
LIC_FILES_CHKSUM = "file://LICENSE;md5=907b35094e28d92d03f21f8883acfa3b \
                    file://ggml/LICENSE;md5=223b26b3c1143120c87e2b13111d3e99 \
                    file://thirdparty/libwebp/COPYING;md5=6e8dee932c26f2dab503abf70c96d8bb \
                    file://thirdparty/libwebm/LICENSE.TXT;md5=6e8dee932c26f2dab503abf70c96d8bb"

inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Diffuse/src/image/source/stable-diffusion.cpp"

SRC_URI = "git://github.com/leejet/stable-diffusion.cpp;protocol=https;branch=master"
SRCREV = "7f410a3793c5bba8eb198e962ce7a3d6095f9d89"

# Upstream has NO release line. Its only version-like token is the per-commit tag
# master-<N>-<sha>, where N is a monotonic commit counter; at this pin the tag is
# master-859-7f410a3. 0.0.859 orders correctly against a later snapshot and can be
# re-derived from the tag, which a bare date or SHA could not.
PV = "0.0.859"
SYMON_SD_UPSTREAM_TAG = "master-859-7f410a3"
SYMON_SD_SHORT_SHA = "7f410a3"
# the ggml SUBMODULE's own pin - a different commit, and it asks the same questions
SYMON_SD_GGML_SHORT_SHA = "e20c3a1"

inherit cmake pkgconfig

# CUDA arrives ONLY through the estate authority (P7: symoneural-cuda.bbclass ->
# cuda-toolkit-bin 13.4.1, sm_120). SD_CUDA=ON is the whole of sd.cpp's backend
# selection - CMakeLists.txt turns it into GGML_CUDA=ON for the vendored ggml.
# The CPU-only build stays selectable with PACKAGECONFIG = "".
PACKAGECONFIG ??= "cuda"
PACKAGECONFIG[cuda] = "-DSD_CUDA=ON,-DSD_CUDA=OFF,,"
inherit ${@bb.utils.contains('PACKAGECONFIG', 'cuda', 'symoneural-cuda', '', d)}

# CMAKE_CUDA_ARCHITECTURES is NOT set here: symoneural-cuda.bbclass writes it into the
# generated toolchain file from SYMON_CUDA_ARCH (120). ggml then rewrites 120 to 120a-real
# (src/ggml-cuda/CMakeLists.txt) because Blackwell's FP4 tensor-core instructions are not
# forwards compatible. Setting it twice would let the two disagree.

# --- everything below turns OFF a build-time network path or a host probe ---------
#
# GGML_CUDA_CUB_3DOT2  the ONE FetchContent in this tree: it clones nvidia/cccl v3.2.0
#                      from GitHub at configure time. CUDA 13.4 already bundles CCCL, and
#                      no bitbake task may reach the network. It is never declared with
#                      option(), so it is an undefined -> false variable and would not
#                      have fired by default; it is pinned OFF so a future default flip
#                      cannot turn a configure into a clone.
# GGML_CUDA_NCCL       defaults ON and calls find_package(NCCL). NCCL is not part of
#                      cuda-toolkit-bin, so the probe can only miss - or, worse, hit a
#                      copy on the build host outside the sysroot. One GPU: OFF.
# GGML_NATIVE          never bake the build host's CPU into a cross artefact
# GGML_CCACHE          no host ccache probing
# GGML_CPU_KLEIDIAI    Arm-only, and the CPU backend's only FetchContent
# SD_SERVER_BUILD_FRONTEND  runs `pnpm install` and `pnpm run build` in
#                      examples/server/frontend. pnpm is not in the native sysroot and
#                      examples/server/frontend/dist does not exist at this pin, so the
#                      build would take the "pnpm not found" warning branch anyway; OFF
#                      makes that a decision instead of an accident of PATH.
EXTRA_OECMAKE += "-DGGML_CUDA_CUB_3DOT2=OFF \
                  -DGGML_CUDA_NCCL=OFF \
                  -DGGML_NATIVE=OFF \
                  -DGGML_CCACHE=OFF \
                  -DGGML_CPU_KLEIDIAI=OFF \
                  -DSD_SERVER_BUILD_FRONTEND=OFF"

# x86-64-v3 is the estate's target arch (AVX2/FMA/F16C/BMI2). ggml's instruction options
# default from INS_ENB, which follows GGML_NATIVE; with NATIVE off they would fall back to
# a baseline CPU. Same set as symoneural-ggml, for the same reason.
EXTRA_OECMAKE += "-DGGML_AVX=ON -DGGML_AVX2=ON -DGGML_FMA=ON -DGGML_F16C=ON -DGGML_BMI2=ON \
                  -DGGML_OPENMP=ON"

# SD_BUILD_SHARED_LIBS=ON: sd-cli and sd-server both link `stable-diffusion`, and the
# default static build would put a second full copy of the compiled CUDA kernels inside
# each binary. Shared keeps one. It also sets CMAKE_POSITION_INDEPENDENT_CODE before
# add_subdirectory(ggml), which the static branch does not.
# SD_BUILD_SHARED_GGML_LIB stays OFF: ggml is static INSIDE libstable-diffusion.so, so the
# 0.19.0 fork never appears as a loadable libggml that could be confused with the estate's
# canonical 0.23.0.
# SD_BUILD_EXAMPLES=ON is how sd-cli exists at all; it is the deliverable.
EXTRA_OECMAKE += "-DSD_BUILD_SHARED_LIBS=ON -DSD_BUILD_SHARED_GGML_LIB=OFF -DSD_BUILD_EXAMPLES=ON"

# WebP and WebM image/video output, from the pinned submodules already in the export.
# Both default ON because the submodule CMakeLists exist; stated so the packaging below
# is not describing an accident.
EXTRA_OECMAKE += "-DSD_WEBP=ON -DSD_USE_SYSTEM_WEBP=OFF -DSD_WEBM=ON -DSD_USE_SYSTEM_WEBM=OFF"

# ---- the version stamp: a git stub, not the estate's HEAD -------------------------
# CMakeLists.txt runs `git describe --tags` and `git rev-parse --short HEAD` in
# CMAKE_CURRENT_SOURCE_DIR and compiles the answers into src/version.cpp. Under
# symoneural-pristine ${S} is a `git archive` export with NO .git - but ${WORKDIR} sits
# under Symoneural-Diffuse/build/ INSIDE the estate repository, so git would walk upward
# and stamp sd-cli with the ESTATE's commit. That is the precise failure the class's own
# header warns about, and it would make the binary non-reproducible as a bonus.
# GIT_EXE is a find_program cache variable, so pointing it at a stub is enough. The stub
# answers with the PIN - the values in SRCREV and the recorded upstream tag - which is
# the truthful stamp, not "unknown" and not the estate's HEAD.
SYMON_SD_GIT_STUB = "${WORKDIR}/symoneural-sd-git"
symon_sd_write_git_stub() {
	cat > ${SYMON_SD_GIT_STUB} <<EOF
#!/bin/sh
# generated by symoneural-stable-diffusion-cpp_git.bb. CMake asks git what this tree is;
# under symoneural-pristine the export has no .git and the answer would come from the
# estate repository above it. These values ARE the pins.
#
# TWO trees ask, through the SAME GIT_EXE cache variable, from different directories:
# CMakeLists.txt from the top level and ggml/CMakeLists.txt from ggml/. They are
# different commits, so the answer depends on where the question is asked. A stub that
# answered the top-level SHA everywhere compiled GGML_COMMIT="7f410a3-dirty" into
# libggml-base - a submodule claiming its parent's commit, and a dirty flag on a tree
# that is a verified export. Observed in the first build's configure log, fixed here.
d=\$(pwd)
case "\$1" in
  describe)
    echo "${SYMON_SD_UPSTREAM_TAG}" ;;
  rev-parse)
    case "\$d" in
      */ggml) echo "${SYMON_SD_GGML_SHORT_SHA}" ;;
      *)      echo "${SYMON_SD_SHORT_SHA}" ;;
    esac ;;
  diff-index)
    # ggml appends "-dirty" when this exits non-zero. A git archive export of a
    # LISTING-VERIFIED pin is clean by construction, so 0 is the true answer.
    exit 0 ;;
  *)
    exit 1 ;;
esac
EOF
	chmod +x ${SYMON_SD_GIT_STUB}
}
do_configure[prefuncs] += "symon_sd_write_git_stub"
EXTRA_OECMAKE += "-DGIT_EXE=${SYMON_SD_GIT_STUB}"

# ---- packaging --------------------------------------------------------------------
# libstable-diffusion.so has no VERSION/SOVERSION upstream, so OE's default rules would
# file the unversioned .so into -dev and leave sd-cli in ${PN} with an unsatisfiable
# NEEDED. FILES_SOLIBSDEV="" plus the explicit FILES below put the runtime library where
# its consumers are; INSANE_SKIP dev-so acknowledges the unversioned name is upstream's.
SOLIBS = ".so"
FILES_SOLIBSDEV = ""
FILES:${PN} += "${libdir}/libstable-diffusion.so ${bindir}/sd-cli"
INSANE_SKIP:${PN} += "dev-so"
FILES:${PN}-dev += "${includedir} ${libdir}/cmake ${libdir}/pkgconfig"

# examples/CMakeLists.txt adds cli AND server unconditionally - upstream's SD_BUILD_SERVER
# option is commented out, so sd-server cannot be switched off without editing the source,
# and R1 forbids that. It is therefore built and packaged SEPARATELY, and no image
# installs it: the estate's HTTP surface is the FastAPI gateway, and a second listener
# inside a runtime image is not something to ship by accident.
PACKAGES =+ "${PN}-server"
FILES:${PN}-server = "${bindir}/sd-server"
RDEPENDS:${PN}-server += "${PN}"

# ---- the vendored ggml's dev artefacts must NOT be installed -----------------------
# ggml/CMakeLists.txt installs its CMake package config and its 19 public headers
# UNCONDITIONALLY - line 347 `install(TARGETS ggml LIBRARY PUBLIC_HEADER)` and line 416
# `install(FILES ggml-config.cmake ggml-config-version.cmake DESTINATION .../cmake/ggml)`,
# neither inside a GGML_STANDALONE guard. Verified by listing ${D} after the first
# successful build: 19 ggml*.h plus gguf.h in ${includedir}, ggml-config{,-version}.cmake
# in ${libdir}/cmake/ggml, and four libggml*.a.
#
# Those are the SAME paths symoneural-ggml-dev owns for CANONICAL ggml 0.23.0. Two
# consequences, and the second is the serious one:
#   * do_rootfs conflict if both -dev packages ever land in one image;
#   * a third consumer's find_package(ggml) could resolve to the 0.19.0 config and
#     compile against headers built for GGML_MAX_NAME=160 while linking a 0.23.0
#     libggml built at 64 - the identical sizeof(struct ggml_tensor) corruption the
#     comment at the top of this recipe exists to prevent, arriving through the INCLUDE
#     path instead of the loader.
#
# Nothing in the estate consumes this fork's ggml: it is compiled static INSIDE
# libstable-diffusion.so and has no separate consumer by design. So the honest fix is
# not to ship its development interface at all. `rm -f`, not a FILES exclusion: an
# excluded file still sits in ${D} and OE reports it as installed-but-not-shipped.
do_install:append() {
	rm -f ${D}${includedir}/ggml*.h ${D}${includedir}/gguf.h
	rm -rf ${D}${libdir}/cmake/ggml
	rm -f ${D}${libdir}/libggml*.a
	rm -f ${D}${libdir}/pkgconfig/ggml.pc
}
