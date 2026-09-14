# typing-extensions - a RUNTIME dependency of the API wheels (fastapi >=4.8.0 ...).
# Acquired 2026-09-13 under the estate rule "own what you ship": the layer copy is
# build tooling at most, never the shipped provider. Tag 4.16.0 at the pin below;
# licence read from the tree, not from a layer recipe.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/model/source/typing-extensions"

SUMMARY = "typing-extensions for the SyMoNeuRaL API runtime"
HOMEPAGE = "https://github.com/python/typing_extensions"
LICENSE = "PSF-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=fcf6b249c2641540219a727f35d8d2c2"

SRC_URI = "git://github.com/python/typing_extensions;protocol=https;nobranch=1;branch=main"
PV = "4.16.0"
SRCREV = "f29cd28d8ed7642cafb1d18daf5aa41be6a5c0aa"

inherit python_flit_core
