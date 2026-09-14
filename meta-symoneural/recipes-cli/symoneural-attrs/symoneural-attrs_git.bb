# attrs for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (jsonschema attrs>=22.2.0; referencing attrs>=22.2.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag 26.1.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/data/source/attrs"

SUMMARY = "attrs for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/python-attrs/attrs"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=5e55731824cf9205cfabeab9a0600887"

SRC_URI = "git://github.com/python-attrs/attrs;protocol=https;nobranch=1;branch=main"
PV = "26.1.0"
SRCREV = "7bfc49e9b22d5ba25b6e429524c3d49fee27cb36"

inherit python_hatchling
DEPENDS += "python3-hatch-vcs-native python3-hatch-fancy-pypi-readme-native"
