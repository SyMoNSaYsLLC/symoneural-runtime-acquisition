# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "GPL-2.0-or-later AND LGPL-2.1-or-later"
# LIC_FILES_CHKSUM restored to recipetool's full file list.
# Rationale: over-declaring makes bitbake detect licence drift across ALL
# licence-bearing files; under-declaring hides it. Curating this down to one
# canonical file dropped OpenBLAS from 8 files to 1, losing coverage of the
# vendored LAPACK, LAPACKE, ReLAPACK and netlib BLAS reference licences.
LIC_FILES_CHKSUM = "file://gl-mod/bootstrap/LICENSE;md5=d65cd57ee96e03049d1c1cf9b4bf8f88 \
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

