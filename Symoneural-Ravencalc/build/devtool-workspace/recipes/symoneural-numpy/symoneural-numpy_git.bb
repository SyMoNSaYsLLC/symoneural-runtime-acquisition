# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=26080bf81b2662c7119d3ef28ae197fd"
SRC_URI = "gitsm://github.com/numpy/numpy;protocol=https;branch=maintenance/2.5.x"

# Modify these as desired
PV = "2.5.3"
SRCREV = "dd88c0c19b54ad9ed3533224221285bf0873249a"

S = "${WORKDIR}/git"

inherit python_mesonpy

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

