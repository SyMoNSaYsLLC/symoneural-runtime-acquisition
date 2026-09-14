# typing-inspection - a RUNTIME dependency of the API wheels (fastapi >=0.4.2 ...).
# Acquired 2026-09-13 under the estate rule "own what you ship": the layer copy is
# build tooling at most, never the shipped provider. Tag v0.4.4 at the pin below;
# licence read from the tree, not from a layer recipe.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/model/source/typing-inspection"

SUMMARY = "typing-inspection for the SyMoNeuRaL API runtime"
HOMEPAGE = "https://github.com/pydantic/typing-inspection"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=dfe2d84c58973d6a532c4e7638dbb3d8"

SRC_URI = "git://github.com/pydantic/typing-inspection;protocol=https;nobranch=1;branch=main"
PV = "0.4.4"
SRCREV = "83d4dbb74fc367db4403c76be8c0f83cd4b63fbe"

inherit python_hatchling


# Runtime edges from this wheel's own Requires-Dist (target Python 3.14; no extras).
RDEPENDS:${PN} += "symoneural-typing-extensions"
