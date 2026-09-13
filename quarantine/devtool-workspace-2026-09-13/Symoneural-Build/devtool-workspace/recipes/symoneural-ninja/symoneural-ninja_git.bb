# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://COPYING;md5=a81586a64ad4e476c791cda7e2f2c52e"
SRC_URI = "git://github.com/ninja-build/ninja;protocol=https;branch=release"

# Modify these as desired
PV = "1.13.2"
SRCREV = "3441b633c2fe2c494e958780ba0f4227b1327634"

S = "${WORKDIR}/git"

# NOTE: unable to map the following CMake package dependencies: GTest
# NOTE: spec file indicates the license may be "Apache 2.0"
inherit cmake

# Specify any options you want to pass to cmake using EXTRA_OECMAKE:
EXTRA_OECMAKE = ""

