# Pygments for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (rich pygments>=2.13.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag 2.21.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/text/source/pygments"

SUMMARY = "Pygments for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/pygments/pygments"
LICENSE = "BSD-2-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=36a13c90514e2899f1eba7f41c3ee592"

SRC_URI = "git://github.com/pygments/pygments;protocol=https;nobranch=1;branch=main"
PV = "2.21.0"
SRCREV = "a43b45dcf081b6010c6ab4428f149f7f6d2499c4"

inherit python_hatchling
