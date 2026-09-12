# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=a6607bd72611b702183473dfb4e6198b"
SRC_URI = "git://github.com/mpmath/mpmath;protocol=https;branch=mpmath-1.4.x"

# Modify these as desired
PV = "1.4.1"
SRCREV = "c1131e2d64abcbb57728ca8a499c920c0c69e67f"

S = "${WORKDIR}/git"

inherit python_setuptools_build_meta

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

