# SyMoNeuRaL-owned pybind11. NOT a redesign: mirrors meta-python's
# python3-pybind11_3.0.4.bb - same upstream, same SRCREV, same build classes -
# repointed at the estate's own pinned tree. LIC_FILES_CHKSUM matches
# meta-python's declaration (774f65abd8a7fe3124be2cdf766cd06f), verified against
# our acquired LICENSE.
#
# WHY OWN IT. pybind11 is header-only: its headers are compiled INTO scipy's
# _duccfft extension and ship inside our binary. That is "own what you ship", not
# "borrow what you only build with". Borrowing it also produced a live defect -
# meta-python's pybind11.pc lands only in recipe-sysroot-native, so meson fell
# through to the native config-tool, which emitted the target include path
# /usr/include/python3.14 with no sysroot prefix and tripped
# -Werror=poison-system-directories.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/devtools/source/pybind11"

SUMMARY = "Seamless operability between C++11 and Python"
HOMEPAGE = "https://github.com/pybind/pybind11"
SECTION = "devel/python"

LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=774f65abd8a7fe3124be2cdf766cd06f"

SRC_URI = "git://github.com/pybind/pybind11;protocol=https;branch=stable"
SRCREV = "d03662f0984f652b60e7ddce53d3868002275197"
PV = "3.0.4"

# ninja and cmake stay BORROWED, deliberately. Both are build-only - neither ever
# ships to a customer - so DECISIONS.md's rule applies: "borrow what you only
# build with". symoneural-ninja exists but carries no BBCLASSEXTEND, so there is
# no native variant; pointing at one was my error and bitbake caught it:
#   Nothing PROVIDES 'symoneural-ninja-native'
# Reverting is not the expedient fix, it is the correct one - this matches what
# meta-python declares, and "do not redesign" applies here too.
DEPENDS = "python3-cmake-native python3-ninja-native"

inherit cmake python_setuptools_build_meta

EXTRA_OECMAKE = "-DPYBIND11_TEST=OFF -DPYBIND11_USE_CROSSCOMPILING=ON"

# Kept verbatim from meta-python: the python_setuptools_build_meta class owns the
# task bodies, so the cmake half has to be chained on explicitly.
do_configure:append() {
    cmake_do_configure
}

do_compile:append() {
    cmake_do_compile
}

do_install:append() {
    cmake_do_install
}

BBCLASSEXTEND = "native nativesdk"
