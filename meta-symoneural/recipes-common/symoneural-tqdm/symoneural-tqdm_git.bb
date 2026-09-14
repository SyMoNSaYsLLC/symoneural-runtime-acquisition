# tqdm for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (huggingface-hub tqdm>=4.42.1; transformers tqdm>=4.60). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag v4.70.1 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/util/source/tqdm"

SUMMARY = "tqdm for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/tqdm/tqdm"
LICENSE = "MIT AND MPL-2.0"
LIC_FILES_CHKSUM = "file://LICENCE;md5=9a9bed097dea538bf341c8623c8f8852"

SRC_URI = "git://github.com/tqdm/tqdm;protocol=https;nobranch=1;branch=main"
PV = "4.70.1"
SRCREV = "9cf5a12b1f955468a17f0ba3c59092b23e4258ac"

inherit python_setuptools_build_meta
DEPENDS += "python3-setuptools-scm-native"
# tqdm's only declared dependency, colorama, is gated on
# platform_system == "Windows" and is false for this target, so no RDEPENDS.
