# narwhals - a RUNTIME dependency of the scikit-learn wheel (scikit-learn narwhals>=2.0.1). Acquired
# 2026-09-13 under "own what you ship"; licence read from the tree at the pin.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/dataframe/source/narwhals"

SUMMARY = "narwhals for the SyMoNeuRaL Ravencalc runtime"
HOMEPAGE = "https://github.com/narwhals-dev/narwhals"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE.md;md5=635dc68cb70b18de784113020c6d814e"

SRC_URI = "git://github.com/narwhals-dev/narwhals;protocol=https;nobranch=1;branch=main"
PV = "2.26.0"
SRCREV = "e34715d1e9e2bd6f5306662e8ad495eaf0c1325a"

inherit python_uv_build
