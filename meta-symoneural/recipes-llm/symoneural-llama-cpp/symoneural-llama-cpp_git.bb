# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

SUMMARY = "CPU Inference of LLaMA model in pure C/C++ (no CUDA/OpenCL)"
# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
#
# The following license files were not able to be identified and are
# represented as "Unknown" below, you will need to check them yourself:
#   cmake/license.cmake
#   vendor/hash/sha256/LICENSE
#   vendor/hash/xxhash/LICENSE
#
# NOTE: multiple licenses have been detected; they have been separated with &
# in the LICENSE value for now since it is a reasonable assumption that all
# of the licenses apply. If instead there is a choice between the multiple
# licenses then you should change the value to separate the licenses with |
# instead of &. If there is any doubt, check the accompanying documentation
# to determine which situation is applicable.
# LICENSE established from the licence text in the acquired tree. recipetool had
# emitted a non-SPDX token ('Unknown'/'Apache'), which newer OE-Core's SPDX parser
# rejects outright: do_populate_lic dies with
# "AttributeError: 'UnknownId' object has no attribute 'name'".
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-LLM/src/inference/source/llama.cpp"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=223b26b3c1143120c87e2b13111d3e99 \
                    file://cmake/license.cmake;md5=c547b83618ef0f5139afeda251ba3dad \
                    file://gguf-py/LICENSE;md5=d486bb2ba5e2a4d3c958abbcbe1b9225 \
                    file://licenses/LICENSE-jsonhpp;md5=d9545308f01613f54de6f21134ec51f3 \
                    file://tools/ui/src/lib/vendors/big-integer/LICENSE;md5=5641118d2906fdb4ba9b0c35dec565eb \
                    file://tools/ui/src/lib/vendors/decimal.js/LICENCE.md;md5=069dacc2a679616090ba5fe5d8687cac \
                    file://tools/ui/src/lib/vendors/nerdamer-prime/LICENSE;md5=cfc391c756ac9312d458ea4ce6b32c3f \
                    file://vendor/cpp-httplib/LICENSE;md5=1321bdf796c67e3a8ab8e352dd81474b \
                    file://vendor/hash/rotate-bits/LICENSE.md;md5=bcdfbfcc0d644320ff435b1acd3627e7 \
                    file://vendor/hash/sha256/LICENSE;md5=9023e9d96f2f04557d35e682b39ffd60 \
                    file://vendor/hash/xxhash/LICENSE;md5=13be6b481ff5616f77dda971191bb29b"

SRC_URI = "gitsm://github.com/ggml-org/llama.cpp;protocol=https;branch=master"

# Modify these as desired
# PV is the real upstream release tag at SRCREV, not recipetool's "1.0+git"
# placeholder. The placeholder is not merely cosmetic: it names every .ipk
# <pkg>_1.0+git-r0, and symoneural-pristine exports it as the wheel version
# via *_PRETEND_VERSION/*_BYPASS, where uv-dynamic-versioning parsed it and
# died with IndexError on int(parts[index]).
PV = "0.4.0"
SRCREV = "5266f24da75dc449bd56cbed7addb9c8e4a6a73e"

# NOTE: spec file indicates the license may be "MIT"
# recipetool inherited python_poetry_core here: llama.cpp ships a pyproject.toml
# for its helper scripts, and the detector picked that over the CMakeLists.txt that
# actually builds the project. llama.cpp is C++/cmake.
inherit cmake


# WARNING: We were unable to map the following python package/module
# runtime dependencies to the bitbake packages which include them:
#    torch

# CPU-only build. llama.cpp defaults BUILD_SHARED_LIBS off; we want the shared
# library so it can become a SyMoNeuRaL artifact. GGML_NATIVE is disabled because
# -march=native would bake the build host's CPU into a cross-compiled artifact.
EXTRA_OECMAKE += "-DBUILD_SHARED_LIBS=ON -DGGML_NATIVE=OFF -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF"
