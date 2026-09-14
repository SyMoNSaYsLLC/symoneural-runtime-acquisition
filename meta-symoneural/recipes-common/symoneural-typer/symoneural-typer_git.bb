# typer for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (transformers typer (unconditional in the wheel METADATA)). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag 0.27.2 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/util/source/typer"

SUMMARY = "typer for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/fastapi/typer"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=173d405eb704b1499218013178722617"

SRC_URI = "git://github.com/fastapi/typer;protocol=https;nobranch=1;branch=main"
PV = "0.27.2"
SRCREV = "99eb220df7c69a0f14a0b69214042677e0760b9d"

inherit python_pdm
DEPENDS += "python3-pdm-backend-native"
# typer declares shellingham>=1.3.0, rich>=13.8.0 and annotated-doc>=0.0.2.
# annotated-doc is already SYMONEURAL-OWNED by the API runtime. colorama is
# Windows-gated and false here.
RDEPENDS:${PN} += "symoneural-shellingham symoneural-rich symoneural-annotated-doc"
