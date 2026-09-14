# shellingham for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (typer shellingham>=1.3.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag 1.5.4 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/util/source/shellingham"

SUMMARY = "shellingham for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/sarugaku/shellingham"
LICENSE = "ISC"
LIC_FILES_CHKSUM = "file://LICENSE;md5=78e1c0248051c32a38a7f820c30bd7a5"

SRC_URI = "git://github.com/sarugaku/shellingham;protocol=https;nobranch=1;branch=main"
PV = "1.5.4"
SRCREV = "cba059e7f29f731c2fdf9c8c3ea7921182b7d6c3"

# shellingham declares NO build-backend (requires = setuptools, wheel), so PEP 517
# falls back to setuptools.build_meta:__legacy__ and pyproject-build checks for
# wheel - the same gap that stopped pycparser in the CLI closure. wheel is build
# tooling and never ships, so the OE-Core copy is the correct provider.
inherit python_setuptools_build_meta
DEPENDS += "python3-wheel-native"
