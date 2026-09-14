# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
#
# The following license files were not able to be identified and are
# represented as "Unknown" below, you will need to check them yourself:
#   LICENSE.md
# LICENSE established from the licence text in the acquired tree. recipetool had
# emitted a non-SPDX token ('Unknown'/'Apache'), which newer OE-Core's SPDX parser
# rejects outright: do_populate_lic dies with
# "AttributeError: 'UnknownId' object has no attribute 'name'".
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/web/source/starlette"

LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.md;md5=11e8c8dbfd5fa373c703de492140ff7a"

SRC_URI = "git://github.com/encode/starlette;protocol=https;branch=main"

# Modify these as desired
# PV is the real upstream release tag at SRCREV, not recipetool's "1.0+git"
# placeholder. The placeholder is not merely cosmetic: it names every .ipk
# <pkg>_1.0+git-r0, and symoneural-pristine exports it as the wheel version
# via *_PRETEND_VERSION/*_BYPASS, where uv-dynamic-versioning parsed it and
# died with IndexError on int(parts[index]).
PV = "1.6.0"
SRCREV = "4f250d6b814587e20c5365f0a5f0c4d42bcb929f"

# recipetool emitted empty do_configure/do_compile/do_install stubs ALONGSIDE
# a real build-class inherit. A recipe-level function OVERRIDES the inherited
# one, so the stubs silently won: this recipe installed nothing (or ran bare
# `make`) despite inheriting a working class. Stubs removed so the inherited
# class actually runs.
inherit python_hatchling

# NOTE: no Makefile found, unable to determine what needs to be done
# Runtime edges to the acquired Tier-B distributions (wheel METADATA, target 3.14, no extras).
RDEPENDS:${PN} += "symoneural-anyio"
