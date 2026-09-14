# psutil for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels: accelerate 1.15.0 declares psutil
# (install_requires, unconditional). Acquired 2026-09-14 under the estate rule "own
# what you ship": layer copies are build tooling at most, never the shipped provider.
# The objective document had already tabled it as a pending C-extension acquisition.
# Tag release-7.2.2 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/util/source/psutil"

SUMMARY = "psutil for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/giampaolo/psutil"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=a9c72113a843d0d732a0ac1c200d81b1"

SRC_URI = "git://github.com/giampaolo/psutil;protocol=https;nobranch=1;branch=master"
PV = "7.2.2"
SRCREV = "9eea97dd6f1d16ea33f5144c8925f1ce7a0688e1"

# Mirrors oe-core python3-psutil_7.2.2.bb: the C extension (_psutil_linux,
# _psutil_posix) is cross-compiled by setuptools against the target sysconfig, and
# the bundled test suite is split out of the runtime package exactly as upstream OE
# does. The -tests package's on-target toolchain RDEPENDS (gcc, binutils, ...) are
# not mirrored: this estate proves runtimes with tools/clean-root-proof, not by
# running upstream's test suite on the target.
inherit python_setuptools_build_meta

PACKAGES =+ "${PN}-tests"
FILES:${PN}-tests += " \
    ${PYTHON_SITEPACKAGES_DIR}/psutil/test* \
    ${PYTHON_SITEPACKAGES_DIR}/psutil/__pycache__/test* \
"
RDEPENDS:${PN}-tests += "${PN}"

RDEPENDS:${PN} += " \
    python3-shell python3-threading python3-xml python3-netclient python3-ctypes \
    python3-resource \
"
