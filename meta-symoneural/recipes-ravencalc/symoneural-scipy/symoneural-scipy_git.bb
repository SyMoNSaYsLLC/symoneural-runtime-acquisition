# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/numerics/source/scipy"

LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=6506a2e1578b1a1161d9bda0b896c647 \
                    file://LICENSES_bundled.txt;md5=fe2784111ff83b9451741c37b82985c6"
SRC_URI = "gitsm://github.com/scipy/scipy;protocol=https;branch=maintenance/1.18.x"

# Modify these as desired
PV = "1.18.1"
SRCREV = "e4e854eaa8f18d807cd3496028e257e36caa93cc"

inherit pkgconfig python_mesonpy


# WARNING: We were unable to map the following python package/module
# dependencies to the bitbake packages which include them:
#    Cython
#    numpy
#    pybind11
#    pythran

# WARNING: We were unable to map the following python package/module
# runtime dependencies to the bitbake packages which include them:
#    numpy

# --- SYMONEURAL BUILD DEPS ---------------------------------------------------
# pkgconfig is what lets meson's Cython link test find target python3 (the numpy
# pattern). NOT `inherit cython`: that class seds every .c/.cpp under ${S}, which
# under externalsrc is pristine acquired source.
#
# D2: scipy builds against symoneural-numpy, never OE-Core's python3-numpy.
# Building against a numpy we do not ship is precisely the provider collision
# the control plane exists to prevent.
DEPENDS += "python3-cython-native python3-pybind11-native symoneural-numpy-native symoneural-numpy python3"

# pythran is absent from OE-Core AND from meta-openembedded, and its chain
# (beniget, ply) is absent too. Authoring it in-stack would make the ply
# vendoring collision live. scipy exposes use-pythran as a meson option, so it
# is disabled: the cost is slower fallbacks for Pythran-accelerated kernels,
# not loss of function. BUILD-DESIGN decision, recorded.
EXTRA_OEMESON += "-Duse-pythran=false"

# pyproject-build validates [build-system] requires against the native env even
# with --no-isolation. pythran is unobtainable (absent from OE-Core and
# meta-openembedded, chain missing) and is genuinely unused because
# -Duse-pythran=false. Skipping the check is honest here: the dependency is
# declared but not exercised. numpy IS exercised and is supplied above.
PEP517_BUILD_OPTS += "--skip-dependency-check"
