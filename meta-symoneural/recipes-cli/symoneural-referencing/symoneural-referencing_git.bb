# referencing for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (jsonschema referencing>=0.28.4; jsonschema-specifications referencing>=0.31.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag v0.37.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/json/source/referencing"

SUMMARY = "referencing for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/python-jsonschema/referencing"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=93eb9740964b59e9ba30281255b044e2"

SRC_URI = "git://github.com/python-jsonschema/referencing;protocol=https;nobranch=1;branch=main"
PV = "0.37.0"
SRCREV = "944ed5a20bc5125f2349156cbdc365daac0e67e6"

inherit python_hatchling
DEPENDS += "python3-hatch-vcs-native"
RDEPENDS:${PN} += "symoneural-attrs symoneural-rpds-py"
