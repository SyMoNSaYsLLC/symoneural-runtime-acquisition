# h11 - a RUNTIME dependency of the API wheels (httpcore >=0.16 ...).
# Acquired 2026-09-13 under the estate rule "own what you ship": the layer copy is
# build tooling at most, never the shipped provider. Tag v0.16.0 at the pin below;
# licence read from the tree, not from a layer recipe.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/http/source/h11"

SUMMARY = "h11 for the SyMoNeuRaL API runtime"
HOMEPAGE = "https://github.com/python-hyper/h11"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=f5501d19c3116f4aaeef89369f458693"

SRC_URI = "git://github.com/python-hyper/h11;protocol=https;nobranch=1;branch=main"
PV = "0.16.0"
SRCREV = "1c5b07581f058886c8bdd87adababd7d959dc7ca"

inherit setuptools3
