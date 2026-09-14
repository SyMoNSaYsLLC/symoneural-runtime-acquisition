# rich for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (typer rich>=13.8.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag v15.0.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/text/source/rich"

SUMMARY = "rich for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/Textualize/rich"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=b5f0b94fbc94f5ad9ae4efcf8a778303"

SRC_URI = "git://github.com/Textualize/rich;protocol=https;nobranch=1;branch=main"
PV = "15.0.0"
SRCREV = "6ac483cbea39cab124dfd3483bba70ffafb71050"

# ipywidgets is optional=true and belongs to rich's jupyter extra, so the Jupyter
# stack is deliberately NOT in this closure.
inherit python_poetry_core
RDEPENDS:${PN} += "symoneural-pygments symoneural-markdown-it-py"
