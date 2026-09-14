# cloudpickle - a RUNTIME dependency of joblib 1.6.0 (Requires-Dist cloudpickle>=3.0); the
# Ravencalc clean-root proof failed on `import sklearn` for want of it. Acquired 2026-09-14
# under the estate rule "own what you ship". Tag v3.1.2 at the pin below; licence from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/util/source/cloudpickle"

SUMMARY = "cloudpickle for the SyMoNeuRaL Ravencalc runtime"
HOMEPAGE = "https://github.com/cloudpipe/cloudpickle"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=b4d59aa5e2cc777722aac17841237931"

SRC_URI = "git://github.com/cloudpipe/cloudpickle;protocol=https;nobranch=1;branch=master"
PV = "3.1.2"
SRCREV = "7576fff24b9769432f76cc6d2c01282583ee87a9"

inherit python_flit_core
