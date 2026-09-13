# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/web/source/fastapi"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=95792ff3fe8e11aa49ceb247e66e4810"

SRC_URI = "git://github.com/fastapi/fastapi;protocol=https;branch=master"

# Modify these as desired
PV = "1.0+git"
SRCREV = "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f"

# NOTE: no Makefile found, unable to determine what needs to be done





# fastapi uses the pdm backend. recipetool emitted empty stubs and NO inherit at
# all, so nothing built and nothing installed - yet the task reported success.
# A recipe with stubs and no build class fails silently, which is worse than
# failing loudly.
inherit python_pep517 python_setuptools_build_meta
PEP517_BUILD_API = "pdm.backend"
DEPENDS += "python3-pdm-backend-native"
