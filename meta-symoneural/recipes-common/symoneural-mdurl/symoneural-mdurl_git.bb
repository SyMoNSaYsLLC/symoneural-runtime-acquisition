# mdurl for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (markdown-it-py mdurl~=0.1). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag 0.1.2 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/text/source/mdurl"

SUMMARY = "mdurl for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/executablebooks/mdurl"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=aca1dc6b9088f1dda81c89cad2c77ad1"

SRC_URI = "git://github.com/executablebooks/mdurl;protocol=https;nobranch=1;branch=main"
PV = "0.1.2"
SRCREV = "596bf1c8752de45fa576a52c315d6d8cc5bb1a4e"

# no runtime dependencies: this terminates the transformers -> typer -> rich ->
# markdown-it-py chain.
inherit python_flit_core
