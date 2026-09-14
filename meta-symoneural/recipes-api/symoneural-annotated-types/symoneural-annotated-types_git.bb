# annotated-types - a RUNTIME dependency of the API wheels (pydantic >=0.6.0 ...).
# Acquired 2026-09-13 under the estate rule "own what you ship": the layer copy is
# build tooling at most, never the shipped provider. Tag v0.8.0 at the pin below;
# licence read from the tree, not from a layer recipe.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/model/source/annotated-types"

SUMMARY = "annotated-types for the SyMoNeuRaL API runtime"
HOMEPAGE = "https://github.com/annotated-types/annotated-types"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=c6afb13fdc220497ee5cded1e717ed67"

SRC_URI = "git://github.com/annotated-types/annotated-types;protocol=https;nobranch=1;branch=main"
PV = "0.8.0"
SRCREV = "9eb96680138269811a39d838d720abc3dce33954"

inherit python_hatchling


# Runtime edges from this wheel's own Requires-Dist (target Python 3.14; no extras).
RDEPENDS:${PN} += "symoneural-typing-extensions"
