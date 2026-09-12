# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "BSD-3-Clause AND MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=ea48085d7dff75b49271b25447e8cdca"
SRC_URI = "git://github.com/sympy/sympy;protocol=https;branch=master"

# Modify these as desired
PV = "1.14.0"
SRCREV = "16fa855354eb7bcabd3fe10993841e03b1382692"

S = "${WORKDIR}/git"

inherit setuptools3

# The following configs & dependencies are from setuptools extras_require.
# These dependencies are optional, hence can be controlled via PACKAGECONFIG.
# The upstream names may not correspond exactly to bitbake package names.
# The configs are might not correct, since PACKAGECONFIG does not support expressions as may used in requires.txt - they are just replaced by text.
#
# Uncomment this line to enable all the optional features.
#PACKAGECONFIG ?= "dev"
PACKAGECONFIG[dev] = ",,,python3-hypothesis python3-pytest"

# WARNING: the following rdepends are from setuptools install_requires. These
# upstream names may not correspond exactly to bitbake package names.
RDEPENDS:${PN} += "python3-mpmath"

# WARNING: the following rdepends are determined through basic analysis of the
# python sources, and might not be 100% accurate.
RDEPENDS:${PN} += "python3-core"
