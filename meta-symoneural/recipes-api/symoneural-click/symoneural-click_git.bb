# click - a RUNTIME dependency of the API wheels (uvicorn >=7.0 ...).
# Acquired 2026-09-13 under the estate rule "own what you ship": the layer copy is
# build tooling at most, never the shipped provider. Tag 8.5.0 at the pin below;
# licence read from the tree, not from a layer recipe.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/web/source/click"

SUMMARY = "click for the SyMoNeuRaL API runtime"
HOMEPAGE = "https://github.com/pallets/click"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=1fa98232fd645608937a0fdc82e999b8"

SRC_URI = "git://github.com/pallets/click;protocol=https;nobranch=1;branch=main"
PV = "8.5.0"
SRCREV = "8b19813f2bfca99f1018a587a8cf54fc959f2e5d"

inherit python_flit_core
