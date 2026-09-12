# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "GPL-2.0-only AND MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=7e4cfe1c8dee5c6fe34c79c38d7b6b52 \
                    file://LICENSE.GPL-2.0-only;md5=4ee23c52855c222cba72583d301d2338 \
                    file://LICENSE.MIT;md5=030cb33d2af49ccebca74d0588b84a21"
SRC_URI = "git://git.openembedded.org/bitbake;protocol=https;branch=2.8"

# Modify these as desired
PV = "2.8.1"
SRCREV = "0880963fea4d91a034e4a6e007d23f98658ab986"

S = "${WORKDIR}/git"

# NOTE: no Makefile found, unable to determine what needs to be done

do_configure () {
	# Specify any needed configure commands here
	:
}

do_compile () {
	# Specify compilation commands here
	:
}

do_install () {
	# Specify install commands here
	:
}

