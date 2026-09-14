# jsonschema-specifications for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (jsonschema jsonschema-specifications>=2023.03.6). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag v2025.9.1 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/json/source/jsonschema-specifications"

SUMMARY = "jsonschema-specifications for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/python-jsonschema/jsonschema-specifications"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=93eb9740964b59e9ba30281255b044e2"

SRC_URI = "git://github.com/python-jsonschema/jsonschema-specifications;protocol=https;nobranch=1;branch=main"
PV = "2025.9.1"
SRCREV = "3b846010c34ce254d8ced23023451d1d64de37f5"

inherit python_hatchling
DEPENDS += "python3-hatch-vcs-native"
RDEPENDS:${PN} += "symoneural-referencing"
