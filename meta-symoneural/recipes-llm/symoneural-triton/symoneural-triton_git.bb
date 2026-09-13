# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-LLM/src/inference/source/triton"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=048160ce07d177648e699b6f41a72b9a \
                    file://third_party/f2reduce/LICENCE.txt;md5=1077d374bd619bc68bfe2023d1fabf76"

SRC_URI = "git://github.com/triton-lang/triton;protocol=https;branch=release/3.8.x"

# Modify these as desired
PV = "1.0+git"
SRCREV = "c01b6774b1865984607d89d89d3a10833de92037"

inherit python_setuptools_build_meta


# WARNING: We were unable to map the following python package/module
# dependencies to the bitbake packages which include them:
#    cmake
#    ninja
#    pybind11
