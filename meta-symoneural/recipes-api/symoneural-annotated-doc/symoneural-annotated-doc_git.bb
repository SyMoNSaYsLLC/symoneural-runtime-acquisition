# annotated-doc - a RUNTIME dependency of the API wheels (fastapi >=0.0.2 ...).
# Acquired 2026-09-13 under the estate rule "own what you ship": the layer copy is
# build tooling at most, never the shipped provider. Tag 0.0.5 at the pin below;
# licence read from the tree, not from a layer recipe.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/model/source/annotated-doc"

SUMMARY = "annotated-doc for the SyMoNeuRaL API runtime"
HOMEPAGE = "https://github.com/fastapi/annotated-doc"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=e36e91f278975b8bb76a769f32582892"

SRC_URI = "git://github.com/fastapi/annotated-doc;protocol=https;nobranch=1;branch=main"
PV = "0.0.5"
SRCREV = "ef48d6ad51d226f772fd9c5284f55199afe4007c"

inherit python_pdm
