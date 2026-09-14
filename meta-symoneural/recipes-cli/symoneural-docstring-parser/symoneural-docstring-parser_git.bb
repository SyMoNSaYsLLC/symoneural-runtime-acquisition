# docstring-parser for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (anthropic-sdk-python docstring-parser<1,>=0.15). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag 0.18.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/text/source/docstring-parser"

SUMMARY = "docstring-parser for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/rr-/docstring_parser"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE.md;md5=4014649477385d83f428a6adae447a49"

SRC_URI = "git://github.com/rr-/docstring_parser;protocol=https;nobranch=1;branch=main"
PV = "0.18.0"
SRCREV = "87dca55a7b5bdc854ad1d190f1c461015ba5f008"

inherit python_hatchling
