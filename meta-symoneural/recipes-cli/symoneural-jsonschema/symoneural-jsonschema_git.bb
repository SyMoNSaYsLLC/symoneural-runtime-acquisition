# jsonschema for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (mcp jsonschema>=4.20.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag v4.26.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/json/source/jsonschema"

SUMMARY = "jsonschema for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/python-jsonschema/jsonschema"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=7a60a81c146ec25599a3e1dabb8610a8"

SRC_URI = "git://github.com/python-jsonschema/jsonschema;protocol=https;nobranch=1;branch=main"
PV = "4.26.0"
SRCREV = "a7277432b0f7bcd0551f6e589d30457017125df4"

inherit python_hatchling
DEPENDS += "python3-hatch-vcs-native python3-hatch-fancy-pypi-readme-native"
RDEPENDS:${PN} += "symoneural-attrs symoneural-jsonschema-specifications symoneural-referencing symoneural-rpds-py"
