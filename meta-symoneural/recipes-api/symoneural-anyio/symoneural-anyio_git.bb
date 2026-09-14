# anyio - a RUNTIME dependency of the API wheels (starlette <5,>=3.6.2 ...).
# Acquired 2026-09-13 under the estate rule "own what you ship": the layer copy is
# build tooling at most, never the shipped provider. Tag 4.15.1 at the pin below;
# licence read from the tree, not from a layer recipe.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/http/source/anyio"

SUMMARY = "anyio for the SyMoNeuRaL API runtime"
HOMEPAGE = "https://github.com/agronholm/anyio"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=c0a769411d2af7894099e8ff75058c9f"

SRC_URI = "git://github.com/agronholm/anyio;protocol=https;nobranch=1;branch=main"
PV = "4.15.1"
SRCREV = "ffcd1542cd6d127980205f90a0100078849dd703"

inherit python_setuptools_build_meta
DEPENDS += "python3-setuptools-scm-native"

# Runtime edges from this wheel's own Requires-Dist (target Python 3.14; no extras).
RDEPENDS:${PN} += "symoneural-idna symoneural-sniffio"
