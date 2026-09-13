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
# Four entries REMOVED, and the reason is a property of the class rather than a
# licensing judgement: scikit-learn's .gitattributes marks build_tools (and
# benchmarks, asv_benchmarks, maint_tools, .*) as EXPORT-IGNORE, so
# `git archive HEAD` correctly omits them and they can NEVER be present in the
# pristine export. Declaring them made do_unpack fail permanently:
#   LIC_FILES_CHKSUM names 4 file(s) absent from the export:
#   build_tools/wheels/LICENSE_{linux,macos,windows}.txt, check_license.py
# They are licence texts for libraries bundled into upstream's BINARY WHEELS
# (cibuildwheel tooling). SyMoNeuRaL does not build or ship those wheels, so
# they cover nothing we distribute. Removing them narrows the declaration to
# what the export actually contains - it does not discard applicable terms.
# NOTE: an export is NOT always a full copy of the worktree. mpmath has no
# export-ignore and matched exactly (248 == 248 == 248), which is what made
# "exports are complete" look like a general rule. It is not.
LIC_FILES_CHKSUM = "file://COPYING;md5=bdb6f7facb161e909d9554c4dba7e3d5 \
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
