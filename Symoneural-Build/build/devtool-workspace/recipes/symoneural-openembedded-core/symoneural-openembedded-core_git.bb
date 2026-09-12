# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "MIT AND GPL-2.0-only"
LIC_FILES_CHKSUM = "file://LICENSE;md5=b97a012949927931feb7793eee5ed924 \
                    file://LICENSE.GPL-2.0-only;md5=4ee23c52855c222cba72583d301d2338 \
                    file://LICENSE.MIT;md5=030cb33d2af49ccebca74d0588b84a21"
SRC_URI = "git://git.openembedded.org/openembedded-core;protocol=https;branch=scarthgap"

# Modify these as desired
PV = "5.0.19"
SRCREV = "2814f0962f56c8d1afa4de76d2895ba9b5cb767d"

S = "${WORKDIR}/git"

