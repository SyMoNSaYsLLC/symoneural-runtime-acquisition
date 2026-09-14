# markdown-it-py for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (rich markdown-it-py>=2.2.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag v4.2.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/text/source/markdown-it-py"

SUMMARY = "markdown-it-py for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/executablebooks/markdown-it-py"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=a38a1697260a7ad7bf29f44b362db1fc"

SRC_URI = "git://github.com/executablebooks/markdown-it-py;protocol=https;nobranch=1;branch=main"
PV = "4.2.0"
SRCREV = "36c5f547144df2d01970a5792d68c71a3380b227"

inherit python_flit_core
RDEPENDS:${PN} += "symoneural-mdurl"
