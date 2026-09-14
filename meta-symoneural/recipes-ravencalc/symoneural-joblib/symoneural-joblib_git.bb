# joblib - a RUNTIME dependency of the scikit-learn wheel (scikit-learn joblib>=1.4.0). Acquired
# 2026-09-13 under "own what you ship"; licence read from the tree at the pin.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/util/source/joblib"

SUMMARY = "joblib for the SyMoNeuRaL Ravencalc runtime"
HOMEPAGE = "https://github.com/joblib/joblib"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=2e481820abf0a70a18011a30153df066"

SRC_URI = "git://github.com/joblib/joblib;protocol=https;nobranch=1;branch=main"
PV = "1.6.0"
SRCREV = "cd9a6b05fc4f2b1c8202eb62c4e863484f8cc099"

inherit python_setuptools_build_meta

# joblib 1.6.0 wheel: Requires-Dist cloudpickle>=3.0 (loky/parallel backends import it at module load)
RDEPENDS:${PN} += "symoneural-cloudpickle"
