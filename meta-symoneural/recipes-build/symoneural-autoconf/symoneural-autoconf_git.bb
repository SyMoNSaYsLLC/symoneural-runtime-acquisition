# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Build/src/autotools/source/autoconf"

LICENSE = "GPL-3.0-or-later"
# LIC_FILES_CHKSUM restored to recipetool's full file list.
# Rationale: over-declaring makes bitbake detect licence drift across ALL
# licence-bearing files; under-declaring hides it. Curating this down to one
# canonical file dropped OpenBLAS from 8 files to 1, losing coverage of the
# vendored LAPACK, LAPACKE, ReLAPACK and netlib BLAS reference licences.
LIC_FILES_CHKSUM = "file://COPYING;md5=570a9b3749dd0463a1778803b12a6dce \
                    file://COPYING.EXCEPTION;md5=eb129370fe0bb2068cc4e48ff8d31260 \
                    file://COPYINGv3;md5=1ebbd3e34237af26da5dc08a4e440464"

SRC_URI = "git://git.savannah.gnu.org/git/autoconf.git;protocol=https;branch=master"

# Modify these as desired
PV = "2.73"
SRCREV = "44d712a26b0e14931bf2df57e2c9b80a2747dfce"

# NOTE: the following prog dependencies are unknown, ignoring: emacs xemacs expr

# NOTE: if this software is not capable of being built in a separate build directory
# from the source, you should replace autotools with autotools-brokensep in the
# inherit line
inherit perlnative autotools

# Specify any options you want to pass to the configure script using EXTRA_OECONF:
EXTRA_OECONF = ""

