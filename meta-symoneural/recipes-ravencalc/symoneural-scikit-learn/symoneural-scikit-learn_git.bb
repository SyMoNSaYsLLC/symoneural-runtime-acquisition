# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/ml/source/scikit-learn"

LICENSE = "BSD-3-Clause"
# LIC_FILES_CHKSUM restored to recipetool's full file list.
# Rationale: over-declaring makes bitbake detect licence drift across ALL
# licence-bearing files; under-declaring hides it. Curating this down to one
# canonical file dropped OpenBLAS from 8 files to 1, losing coverage of the
# vendored LAPACK, LAPACKE, ReLAPACK and netlib BLAS reference licences.
LIC_FILES_CHKSUM = "file://COPYING;md5=bdb6f7facb161e909d9554c4dba7e3d5 \
                    file://build_tools/wheels/LICENSE_linux.txt;md5=74fe73a2347614be92ca02e88ccb635e \
                    file://build_tools/wheels/LICENSE_macos.txt;md5=0de7c72eb7424592824af78da6be6820 \
                    file://build_tools/wheels/LICENSE_windows.txt;md5=802ab916560bd734a79d42a2976716f8 \
                    file://build_tools/wheels/check_license.py;md5=261ab1f970bbe479cbdba4db014638d7 \
                    file://sklearn/externals/array_api_compat/LICENSE;md5=3d4ab4243dc36b64cb5d45edfcff7242 \
                    file://sklearn/externals/array_api_extra/LICENSE;md5=88200d470f94211ec903b46e40b5c09b \
                    file://sklearn/svm/src/liblinear/COPYRIGHT;md5=4baf47a10698d8d50aa7907b77be55e9"

SRC_URI = "git://github.com/scikit-learn/scikit-learn;protocol=https;branch=1.9.X"

# Modify these as desired
PV = "1.9.1"
SRCREV = "866c0f51e7560ef0303cbcc5f159df5382ea9e3f"

# recipetool emitted empty do_configure/do_compile/do_install stubs ALONGSIDE
# a real build-class inherit. A recipe-level function OVERRIDES the inherited
# one, so the stubs silently won: this recipe installed nothing (or ran bare
# `make`) despite inheriting a working class. Stubs removed so the inherited
# class actually runs.
inherit pkgconfig python_mesonpy






# --- SYMONEURAL BUILD DEPS ---------------------------------------------------
# D2: scikit-learn builds against the numpy and scipy SyMoNeuRaL ships, not
# OE-Core's python3-numpy.
DEPENDS += "python3-cython-native symoneural-numpy-native symoneural-numpy symoneural-scipy python3"
