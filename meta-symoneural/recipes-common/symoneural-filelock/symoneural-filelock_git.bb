# filelock for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (huggingface-hub filelock>=3.10.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag 3.32.6 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/util/source/filelock"

SUMMARY = "filelock for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/tox-dev/filelock"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=2c6acbdf7bb74caa37512c3a5ca6857b"

SRC_URI = "git://github.com/tox-dev/filelock;protocol=https;nobranch=1;branch=main"
PV = "3.32.6"
SRCREV = "4efd93e0482e8095a0b6949fb337206e7f67495d"

# LICENSE says MIT; pending-acquisitions had expected Unlicense, which is the
# pre-relicensing value. The tree wins.
inherit python_hatchling
DEPENDS += "python3-hatch-vcs-native"
