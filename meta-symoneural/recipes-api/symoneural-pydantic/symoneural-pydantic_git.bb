# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/model/source/pydantic"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=09280955509d1c4ca14bae02f21d49a6 \
                    file://pydantic-core/LICENSE;md5=ab599c188b4a314d2856b3a55030c75c"

SRC_URI = "git://github.com/pydantic/pydantic;protocol=https;branch=v2.13-fixes"

# Modify these as desired
PV = "1.0+git"
SRCREV = "001dea020e0809844e5b17666432c9135a976f46"

# NOTE: the following library dependencies are unknown, ignoring: h
#       (this is based on recipes that have previously been built and packaged)

# recipetool emitted empty do_configure/do_compile/do_install stubs ALONGSIDE
# a real build-class inherit. A recipe-level function OVERRIDES the inherited
# one, so the stubs silently won: this recipe installed nothing (or ran bare
# `make`) despite inheriting a working class. Stubs removed so the inherited
# class actually runs.
inherit python_hatchling




# recipetool guessed `oe_runmake install` for a hatchling/maturin package and
# that guess overrode the inherited class. Removed; python_hatchling installs.


# PEP-517 build backend needs hatch-fancy-pypi-readme importable by nativepython3.
# Proven by build failure, not inferred.
DEPENDS += "python3-hatch-fancy-pypi-readme-native"
