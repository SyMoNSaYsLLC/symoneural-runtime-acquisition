# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/symbolic/source/sympy"

LICENSE = "BSD-3-Clause AND MIT"
# LIC_FILES_CHKSUM restored to recipetool's full file list.
# Rationale: over-declaring makes bitbake detect licence drift across ALL
# licence-bearing files; under-declaring hides it. Curating this down to one
# canonical file dropped OpenBLAS from 8 files to 1, losing coverage of the
# vendored LAPACK, LAPACKE, ReLAPACK and netlib BLAS reference licences.
LIC_FILES_CHKSUM = "file://LICENSE;md5=ea48085d7dff75b49271b25447e8cdca \
                    file://data/TeXmacs/LICENSE;md5=d6236a858ffac8a4743506872d5c1039 \
                    file://sympy/parsing/latex/LICENSE.txt;md5=b70381bd640070cb20be9d6f93f47036"

SRC_URI = "git://github.com/sympy/sympy;protocol=https;branch=master"

# Modify these as desired
PV = "1.14.0"
SRCREV = "16fa855354eb7bcabd3fe10993841e03b1382692"

inherit setuptools3

# The following configs & dependencies are from setuptools extras_require.
# These dependencies are optional, hence can be controlled via PACKAGECONFIG.
# The upstream names may not correspond exactly to bitbake package names.
# The configs are might not correct, since PACKAGECONFIG does not support expressions as may used in requires.txt - they are just replaced by text.
#
# Uncomment this line to enable all the optional features.
#PACKAGECONFIG ?= "dev"
PACKAGECONFIG[dev] = ",,,python3-hypothesis python3-pytest"

# WARNING: the following rdepends are from setuptools install_requires. These
# upstream names may not correspond exactly to bitbake package names.
# recipetool mapped the upstream dependency "mpmath" to OE's python3-* naming.
# No python3-mpmath exists in this estate; SyMoNeuRaL supplies it as
# symoneural-mpmath (Ravencalc/src/symbolic/source/mpmath).
RDEPENDS:${PN} += "symoneural-mpmath"

# WARNING: the following rdepends are determined through basic analysis of the
# python sources, and might not be 100% accurate.
RDEPENDS:${PN} += "python3-core"
