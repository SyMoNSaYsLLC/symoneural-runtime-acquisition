# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=6506a2e1578b1a1161d9bda0b896c647 \
                    file://LICENSES_bundled.txt;md5=fe2784111ff83b9451741c37b82985c6"
SRC_URI = "gitsm://github.com/scipy/scipy;protocol=https;branch=maintenance/1.18.x"

# Modify these as desired
PV = "1.18.1"
SRCREV = "e4e854eaa8f18d807cd3496028e257e36caa93cc"

S = "${WORKDIR}/git"

inherit python_mesonpy


# WARNING: We were unable to map the following python package/module
# dependencies to the bitbake packages which include them:
#    Cython
#    numpy
#    pybind11
#    pythran

# WARNING: We were unable to map the following python package/module
# runtime dependencies to the bitbake packages which include them:
#    numpy
