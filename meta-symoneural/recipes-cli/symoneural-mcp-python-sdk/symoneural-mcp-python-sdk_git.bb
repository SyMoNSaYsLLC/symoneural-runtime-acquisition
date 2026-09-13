# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

SUMMARY = "Model Context Protocol SDK"
HOMEPAGE = "https://modelcontextprotocol.io"
# NOTE: License in pyproject.toml is: MIT
# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/mcp/source/python-sdk"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=7ae711d8a91d3871696f50e34ad3c2d7"

DEPENDS = "python3-hatchling-native"
SRC_URI = "git://github.com/modelcontextprotocol/python-sdk;protocol=https;branch=main"

# Modify these as desired
# PV is the real upstream release tag at SRCREV, not recipetool's "1.0+git"
# placeholder. The placeholder is not merely cosmetic: it names every .ipk
# <pkg>_1.0+git-r0, and symoneural-pristine exports it as the wheel version
# via *_PRETEND_VERSION/*_BYPASS, where uv-dynamic-versioning parsed it and
# died with IndexError on int(parts[index]).
PV = "2.2.0"
SRCREV = "9972c21aa42054fb1450c5fc614761ed11847ec6"

inherit python_hatchling


# WARNING: We were unable to map the following python package/module
# dependencies to the bitbake packages which include them:
#    uv-dynamic-versioning


# meta-python supplies python3-uv-dynamic-versioning 0.14.1, so the real backend
# is used rather than skipping the build-requires check. The version is derived
# properly instead of being faked.
# uv-dynamic-versioning drags its own closure into the NATIVE sysroot; a native
# recipe's RDEPENDS do not populate it, so the transitive deps are explicit.
DEPENDS += "python3-uv-dynamic-versioning-native python3-jinja2-native python3-tomlkit-native python3-dunamai-native"
