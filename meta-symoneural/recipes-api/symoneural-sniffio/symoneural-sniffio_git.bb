# sniffio - a RUNTIME dependency of the API wheels (anyio ...).
# Acquired 2026-09-13 under the estate rule "own what you ship": the layer copy is
# build tooling at most, never the shipped provider. Tag v1.3.1 at the pin below;
# licence read from the tree, not from a layer recipe.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/http/source/sniffio"

SUMMARY = "sniffio for the SyMoNeuRaL API runtime"
HOMEPAGE = "https://github.com/python-trio/sniffio"
LICENSE = "MIT OR Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=fa7b86389e58dd4087a8d2b833e5fe96 \
                    file://LICENSE.MIT;md5=e62ba5042d5983462ad229f5aec1576c \
                    file://LICENSE.APACHE2;md5=3b83ef96387f14655fc854ddc3c6bd57"

SRC_URI = "git://github.com/python-trio/sniffio;protocol=https;nobranch=1;branch=main"
PV = "1.3.1"
SRCREV = "ae020e13b98d276a6558ffc25e82509fd4c288f0"

inherit python_setuptools_build_meta
DEPENDS += "python3-setuptools-scm-native"
