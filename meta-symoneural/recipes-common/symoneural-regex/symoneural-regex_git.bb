# regex for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (transformers regex>=2025.10.22). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag 2026.9.10 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/text/source/regex"

SUMMARY = "regex for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/mrabarnett/mrab-regex"
LICENSE = "Apache-2.0 AND CNRI-Python"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=7b5751ddd6b643203c31ff873051d069"

SRC_URI = "git://github.com/mrabarnett/mrab-regex;protocol=https;nobranch=1;branch=main"
PV = "2026.9.10"
SRCREV = "7dd71c15c4fb5c94206bed1763abd4c2bd2f1b33"

# Derived from CPython's re module, hence the CNRI-Python term alongside Apache-2.0.
inherit python_setuptools_build_meta
