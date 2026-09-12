# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "GPL-2.0-or-later AND LGPL-2.1-or-later"
LIC_FILES_CHKSUM = "file://libtoolize.in;beginline=10;endline=21;md5=5062b84415ec558409a8c6419d7b28db \
                    file://libltdl/ltdl.c;beginline=9;endline=26;md5=cd68c95bddcdd34f586151895b5dc34e"
SRC_URI = "gitsm://git.savannah.gnu.org/git/libtool.git;protocol=https;branch=master"

# Modify these as desired
PV = "2.6.2"
SRCREV = "309bb53a8adfb22c6e5869cc8da049bf123e5438"

S = "${WORKDIR}/git"


# NOTE: if this software is not capable of being built in a separate build directory
# from the source, you should replace autotools with autotools-brokensep in the
# inherit line
inherit autotools

# Specify any options you want to pass to the configure script using EXTRA_OECONF:
EXTRA_OECONF = ""

