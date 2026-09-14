# PyJWT for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (mcp pyjwt[crypto]>=2.10.1). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag 2.14.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/auth/source/pyjwt"

SUMMARY = "PyJWT for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/jpadilla/pyjwt"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=e4b56d2c9973d8cf54655555be06e551"

SRC_URI = "git://github.com/jpadilla/pyjwt;protocol=https;nobranch=1;branch=main"
PV = "2.14.0"
SRCREV = "c6fe464b356ff4b1ebc9ba62172d331a40aa27df"

inherit python_setuptools_build_meta
# mcp selects pyjwt[crypto]; the extra's requirement (cryptography>=3.4.0) is therefore
# RUNTIME REQUIRED on this estate and is carried here, where the wheel declares it.
RDEPENDS:${PN} += "symoneural-cryptography"
