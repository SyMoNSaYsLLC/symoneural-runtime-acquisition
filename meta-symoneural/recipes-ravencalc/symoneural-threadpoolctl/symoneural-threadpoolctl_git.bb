# threadpoolctl - a RUNTIME dependency of the scikit-learn wheel (scikit-learn threadpoolctl>=3.5.0). Acquired
# 2026-09-13 under "own what you ship"; licence read from the tree at the pin.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/util/source/threadpoolctl"

SUMMARY = "threadpoolctl for the SyMoNeuRaL Ravencalc runtime"
HOMEPAGE = "https://github.com/joblib/threadpoolctl"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=8f2439cfddfbeebdb5cac3ae4ae80eaf"

SRC_URI = "git://github.com/joblib/threadpoolctl;protocol=https;nobranch=1;branch=main"
PV = "3.6.0"
SRCREV = "d5bf10bcf90d9a8a315fe9496fb1bc97007d2fea"

inherit python_flit_core
