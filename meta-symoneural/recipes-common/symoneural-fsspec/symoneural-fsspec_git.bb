# fsspec for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (huggingface-hub fsspec>=2023.5.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag 2026.7.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/util/source/fsspec"

SUMMARY = "fsspec for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/fsspec/filesystem_spec"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=b38a11bf4dcdfc66307f8515ce1fbaa6"

SRC_URI = "git://github.com/fsspec/filesystem_spec;protocol=https;nobranch=1;branch=main"
PV = "2026.7.0"
SRCREV = "9e22b60ea6e96fbe8635e88cc71909bdd2850e60"

inherit python_hatchling
DEPENDS += "python3-hatch-vcs-native"
