# certifi - a RUNTIME dependency of the API wheels (httpx any ...).
# Acquired 2026-09-13 under the estate rule "own what you ship": the layer copy is
# build tooling at most, never the shipped provider. Tag 2026.07.22 at the pin below;
# licence read from the tree, not from a layer recipe.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/http/source/certifi"

SUMMARY = "certifi for the SyMoNeuRaL API runtime"
HOMEPAGE = "https://github.com/certifi/python-certifi"
LICENSE = "MPL-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=11618cb6a975948679286b1211bd573c"

SRC_URI = "git://github.com/certifi/python-certifi;protocol=https;nobranch=1;branch=main"
PV = "2026.07.22"
SRCREV = "f4bc676bc101fe2235846e37044e8c693d6cbaf4"

inherit python_setuptools_build_meta
