# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "GPL-2.0-or-later"
LIC_FILES_CHKSUM = "file://COPYING;md5=751419260aa954499f7abaabaa882bbe"
SRC_URI = "git://git.savannah.gnu.org/git/automake.git;protocol=https;branch=master"

# Modify these as desired
PV = "1.19"
SRCREV = "e82d2d34d4626445565bc131f6580b59597d0c62"

S = "${WORKDIR}/git"

# NOTE: the following prog dependencies are unknown, ignoring: byacc tex lex yacc
DEPENDS = "bison-native flex-native"

# NOTE: if this software is not capable of being built in a separate build directory
# from the source, you should replace autotools with autotools-brokensep in the
# inherit line
inherit perlnative autotools

# Specify any options you want to pass to the configure script using EXTRA_OECONF:
EXTRA_OECONF = ""

