# idna - a RUNTIME dependency of the API wheels (httpx any ...).
# Acquired 2026-09-13 under the estate rule "own what you ship": the layer copy is
# build tooling at most, never the shipped provider. Tag v3.19 at the pin below;
# licence read from the tree, not from a layer recipe.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/http/source/idna"

SUMMARY = "idna for the SyMoNeuRaL API runtime"
HOMEPAGE = "https://github.com/kjd/idna"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.md;md5=9a6c29079fc90c29d80332f44d2625f2"

SRC_URI = "git://github.com/kjd/idna;protocol=https;nobranch=1;branch=main"
PV = "3.19"
SRCREV = "03a9a11dd8aecd4fea742cabe20f4d3d9ed82abb"

inherit python_flit_core
