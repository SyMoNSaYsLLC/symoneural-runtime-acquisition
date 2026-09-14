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
# nobranch: the pin is a TAG (1.3.0), not a branch head. The recipe previously
# named branch=mpmath-1.4.x, which stopped being true the moment the pin moved
# back to 1.3.0. symoneural-pristine strips git:// from SRC_URI at parse time so
# nothing is fetched, but this line is the provenance record and must not lie.
SRC_URI = "git://github.com/mpmath/mpmath;protocol=https;nobranch=1;branch=master"

# Modify these as desired
PV = "1.3.0"
SRCREV = "b5c04506ef0cd4a1f1213f8389ee21c9c3551582"

# recipetool emitted empty do_configure/do_compile/do_install stubs ALONGSIDE
# a real build-class inherit. A recipe-level function OVERRIDES the inherited
# one, so the stubs silently won: this recipe installed nothing (or ran bare
# `make`) despite inheriting a working class. Stubs removed so the inherited
# class actually runs.
inherit python_setuptools_build_meta

# setuptools-scm was a dependency OF THE 1.4.1 PIN, whose pyproject.toml used it;
# the comment recording that build failure was true then and is not true now.
# At 1.3.0 the tree references setuptools_scm nowhere
# (`grep -rniE "setuptools[_-]scm"` over the tree: no match), setup.py is a bare
# `setuptools.setup()`, and setup.cfg reads the version with
# `version = attr: mpmath.__version__`, declaring only `setup_requires = setuptools>=36.7.0`.
# There is also no pyproject.toml, so pypa/build uses the PEP 517 fallback backend
# setuptools.build_meta:__legacy__. DEPENDS on setuptools-scm-native would stage a
# build tool this tree never invokes.


# NOTE: no Makefile found, unable to determine what needs to be done




