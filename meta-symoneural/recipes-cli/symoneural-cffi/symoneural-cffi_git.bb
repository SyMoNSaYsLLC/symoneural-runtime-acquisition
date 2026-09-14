# cffi for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (cryptography cffi>=2.0.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag v2.1.1 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/ffi/source/cffi"

SUMMARY = "cffi for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/python-cffi/cffi"
LICENSE = "MIT-0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=c0158ab9b75875f3bb7fea081d388818"

SRC_URI = "git://github.com/python-cffi/cffi;protocol=https;nobranch=1;branch=main"
PV = "2.1.1"
SRCREV = "fd33e7700f0ebafe6f30bd5053f13327221b77a2"

inherit python_setuptools_build_meta pkgconfig
DEPENDS += "libffi"
RDEPENDS:${PN} += "symoneural-pycparser python3-ctypes python3-io python3-shell"
