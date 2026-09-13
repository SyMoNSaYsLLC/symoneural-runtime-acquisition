# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Build/src/autotools/source/m4"

LICENSE = "GPL-3.0-or-later"
# LIC_FILES_CHKSUM restored to recipetool's full file list.
# Rationale: over-declaring makes bitbake detect licence drift across ALL
# licence-bearing files; under-declaring hides it. Curating this down to one
# canonical file dropped OpenBLAS from 8 files to 1, losing coverage of the
# vendored LAPACK, LAPACKE, ReLAPACK and netlib BLAS reference licences.
LIC_FILES_CHKSUM = "file://COPYING;md5=1ebbd3e34237af26da5dc08a4e440464 \
                    file://examples/COPYING;md5=005f2e201a0526c1d1d79dd6303ecf23 \
                    file://gl-mod/bootstrap/LICENSE;md5=d5688448fc38a9cce6ad2dd20f9034a4 \
                    file://gnulib/COPYING;md5=ef5bccbf6e492f82800e68bdeab302eb \
                    file://gnulib/doc/COPYING.LESSERv2;md5=4bf661c1e3793e55c8d1051bc5e0ae21 \
                    file://gnulib/doc/COPYING.LESSERv3;md5=3000208d539ec061b899bce1d9ce9404 \
                    file://gnulib/doc/COPYINGv2;md5=570a9b3749dd0463a1778803b12a6dce \
                    file://gnulib/doc/COPYINGv3;md5=1ebbd3e34237af26da5dc08a4e440464 \
                    file://gnulib/doc/licenses-texi.texi;md5=09b614ae21015080de2b8609e6dc53ab \
                    file://gnulib/etc/license-notices/GPL;md5=1c6e075428a27f5f532f880d13f8e295 \
                    file://gnulib/etc/license-notices/GPLv2+;md5=5ce7d0334f07b226c7fc98c3ff5a856e \
                    file://gnulib/etc/license-notices/GPLv3+;md5=1c6e075428a27f5f532f880d13f8e295 \
                    file://gnulib/etc/license-notices/LGPL;md5=0ca052fc52beb0651a5c5e11438862e3 \
                    file://gnulib/etc/license-notices/LGPLv2+;md5=592cab4e58b6de14cb5c2606d066c198 \
                    file://gnulib/etc/license-notices/LGPLv3+;md5=0ca052fc52beb0651a5c5e11438862e3 \
                    file://gnulib/etc/license-notices/LGPLv3+_or_GPLv2+;md5=9ea8b24d4800023635f1175322cfcf33 \
                    file://gnulib/modules/COPYING;md5=06278c397f7effab23d4b56008d33989"

SRC_URI = "gitsm://git.savannah.gnu.org/git/m4.git;protocol=https;branch=branch-1.4"

# Modify these as desired
PV = "1.4.21"
SRCREV = "fe2f13ab9ab9b3e712c6529f0b2a49a81feb6ce2"

# NOTE: if this software is not capable of being built in a separate build directory
# from the source, you should replace autotools with autotools-brokensep in the
# inherit line
inherit gettext autotools

# Specify any options you want to pass to the configure script using EXTRA_OECONF:
EXTRA_OECONF = ""

