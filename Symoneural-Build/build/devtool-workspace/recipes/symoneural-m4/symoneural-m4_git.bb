# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "GPL-3.0-or-later"
LIC_FILES_CHKSUM = "file://COPYING;md5=1ebbd3e34237af26da5dc08a4e440464"
SRC_URI = "gitsm://git.savannah.gnu.org/git/m4.git;protocol=https;branch=branch-1.4"

# Modify these as desired
PV = "1.4.21"
SRCREV = "fe2f13ab9ab9b3e712c6529f0b2a49a81feb6ce2"

S = "${WORKDIR}/git"


# NOTE: if this software is not capable of being built in a separate build directory
# from the source, you should replace autotools with autotools-brokensep in the
# inherit line
inherit gettext autotools

# Specify any options you want to pass to the configure script using EXTRA_OECONF:
EXTRA_OECONF = ""

