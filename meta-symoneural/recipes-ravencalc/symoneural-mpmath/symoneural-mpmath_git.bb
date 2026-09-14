# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
# Pinned to 1.3.0, not the newest release: sympy 1.14.0 declares mpmath<1.4,>=1.1.0 and the
# shipped pair must satisfy the DECLARED closure (acquisition/unresolved.json:sympy-mpmath-constraint,
# RESOLVED-A 2026-09-14). Move forward again when a sympy release lifts the bound.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/symbolic/source/mpmath"

LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=bde3c575382996b75d85702949512751"
SRC_URI = "git://github.com/mpmath/mpmath;protocol=https;branch=mpmath-1.4.x"

# Modify these as desired
PV = "1.3.0"
SRCREV = "b5c04506ef0cd4a1f1213f8389ee21c9c3551582"

# recipetool emitted empty do_configure/do_compile/do_install stubs ALONGSIDE
# a real build-class inherit. A recipe-level function OVERRIDES the inherited
# one, so the stubs silently won: this recipe installed nothing (or ran bare
# `make`) despite inheriting a working class. Stubs removed so the inherited
# class actually runs.
inherit python_setuptools_build_meta

# Build-time dependency proven by an actual build failure, not inferred:
# mpmath's PEP-517 build requires setuptools-scm; supplied by OE-Core.
DEPENDS += "python3-setuptools-scm-native"


# NOTE: no Makefile found, unable to determine what needs to be done




