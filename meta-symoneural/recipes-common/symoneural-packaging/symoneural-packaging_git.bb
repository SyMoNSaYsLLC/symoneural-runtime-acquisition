# packaging for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (huggingface-hub packaging>=20.9; transformers packaging>=20.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag 26.3 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/util/source/packaging"

SUMMARY = "packaging for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/pypa/packaging"
LICENSE = "Apache-2.0 OR BSD-2-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=faadaedca9251a90b205c9167578ce91 \
                    file://LICENSE.APACHE;md5=2ee41112a44fe7014dce33e26468ba93 \
                    file://LICENSE.BSD;md5=7bef9bf4a8e4263634d0597e7ba100b8"

SRC_URI = "git://github.com/pypa/packaging;protocol=https;nobranch=1;branch=main"
PV = "26.3"
SRCREV = "929fd4b1410ac7ef61ef3f45b2f5d7e87711a9b5"

inherit python_flit_core
