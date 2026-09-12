# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "GPL-3.0-or-later"
LIC_FILES_CHKSUM = "file://COPYINGv3;md5=1ebbd3e34237af26da5dc08a4e440464 \
                    file://COPYING.EXCEPTION;md5=eb129370fe0bb2068cc4e48ff8d31260"
SRC_URI = "git://git.savannah.gnu.org/git/autoconf.git;protocol=https;branch=master"

# Modify these as desired
PV = "2.73"
SRCREV = "44d712a26b0e14931bf2df57e2c9b80a2747dfce"

S = "${WORKDIR}/git"

# NOTE: the following prog dependencies are unknown, ignoring: emacs xemacs expr

# NOTE: if this software is not capable of being built in a separate build directory
# from the source, you should replace autotools with autotools-brokensep in the
# inherit line
inherit perlnative autotools

# Specify any options you want to pass to the configure script using EXTRA_OECONF:
EXTRA_OECONF = ""

