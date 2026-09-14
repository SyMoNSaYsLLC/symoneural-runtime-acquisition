# setuptools for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels: torch 2.14 declares
# setuptools>=77.0.3 unconditionally (torch.utils.cpp_extension reaches
# pkg_resources/setuptools at run time). Acquired 2026-09-14 under the estate rule
# "own what you ship": the layer's python3-setuptools stays the BUILD tool for every
# wheel in the estate (python3-setuptools-native), never the shipped provider.
# Tag v84.0.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/util/source/setuptools"

SUMMARY = "setuptools for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/pypa/setuptools"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=141643e11c48898150daa83802dbc65f"

SRC_URI = "git://github.com/pypa/setuptools;protocol=https;nobranch=1;branch=main"
PV = "84.0.0"
SRCREV = "72e919a8b10aaafc041205d4e3ae0e6a2e1e5f87"

# Mirrors oe-core python3-setuptools_84.0.0.bb with one deliberate deviation: that
# recipe applies 0001-_distutils-sysconfig.py-make-it-possible-to-substite.patch so
# that a TARGET setuptools can cross-build other extensions under OE. This package
# is a runtime library for torch, is never used to build anything, and the estate
# ships pristine upstream source - no patch is carried.
inherit python_setuptools_build_meta

do_install:append() {
    rm -f ${D}${PYTHON_SITEPACKAGES_DIR}/setuptools/*.exe
}

RDEPENDS:${PN} += " \
    python3-compile python3-compression python3-ctypes python3-email python3-html \
    python3-json python3-netserver python3-numbers python3-pickle python3-pkgutil \
    python3-plistlib python3-shell python3-stringold python3-threading \
    python3-unittest python3-unixadmin python3-xml \
"
