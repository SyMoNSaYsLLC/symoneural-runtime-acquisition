# python-multipart for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (mcp python-multipart>=0.0.9). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag 0.0.32 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/http/source/python-multipart"

SUMMARY = "python-multipart for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/Kludex/python-multipart"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=3b83ef96387f14655fc854ddc3c6bd57"

SRC_URI = "git://github.com/Kludex/python-multipart;protocol=https;nobranch=1;branch=main"
PV = "0.0.32"
SRCREV = "238ead62a0bb6f6cdfe122708faa13812f59f9a6"

inherit python_hatchling
