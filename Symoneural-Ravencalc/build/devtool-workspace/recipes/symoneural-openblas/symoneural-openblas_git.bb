# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "BSD-3-Clause"
# LIC_FILES_CHKSUM restored to recipetool's full file list.
# Rationale: over-declaring makes bitbake detect licence drift across ALL
# licence-bearing files; under-declaring hides it. Curating this down to one
# canonical file dropped OpenBLAS from 8 files to 1, losing coverage of the
# vendored LAPACK, LAPACKE, ReLAPACK and netlib BLAS reference licences.
LIC_FILES_CHKSUM = "file://GotoBLAS_00License.txt;md5=f5be3760860238b7f064d27c77f66e74 \
                    file://LICENSE;md5=5adf4792c949a00013ce25d476a2abc0 \
                    file://ctest/LICENSE;md5=6571445bebffcbf3dc11671e0044a0f9 \
                    file://lapack-netlib/LAPACKE/LICENSE;md5=262be6117ed87ae106825097c1c3733f \
                    file://lapack-netlib/LICENSE;md5=d0e7a458f9fcbf0a3ba97cef3128b85d \
                    file://reference/LICENSE;md5=6571445bebffcbf3dc11671e0044a0f9 \
                    file://relapack/LICENSE;md5=65ab012e987dc0a47926be2d2bc711ba \
                    file://test/LICENSE;md5=6571445bebffcbf3dc11671e0044a0f9"

SRC_URI = "git://github.com/OpenMathLib/OpenBLAS;protocol=https;branch=develop"

# Modify these as desired
PV = "0.3.34"
SRCREV = "e0166008be8e466242aa76b2ff75ce3f0fbf574a"

S = "${WORKDIR}/git"

inherit cmake

# Specify any options you want to pass to cmake using EXTRA_OECMAKE:
# Cross-compile requirements, verified against this build configuration:
#   TARGET=CORE2   OpenBLAS refuses to configure when cross compiling without an
#                  explicit TARGET (cmake/system.cmake:44). CORE2 matches
#                  TUNE_FEATURES="m64 core2".
#   NOFORTRAN=1    The OE cross toolchain is built with LANGUAGES="c,c++" and
#                  FORTRAN="" - there is no Fortran compiler to use.
#   C_LAPACK=1     Keeps LAPACK by building it from the C translations instead of
#                  the Fortran sources, which NOFORTRAN would otherwise drop.
EXTRA_OECMAKE = "-DTARGET=CORE2 -DNOFORTRAN=1 -DC_LAPACK=1 -DBUILD_SHARED_LIBS=ON"
