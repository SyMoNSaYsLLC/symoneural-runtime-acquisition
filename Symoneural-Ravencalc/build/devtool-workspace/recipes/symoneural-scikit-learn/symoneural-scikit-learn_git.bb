# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://COPYING;md5=bdb6f7facb161e909d9554c4dba7e3d5"
SRC_URI = "git://github.com/scikit-learn/scikit-learn;protocol=https;branch=1.9.X"

# Modify these as desired
PV = "1.9.1"
SRCREV = "866c0f51e7560ef0303cbcc5f159df5382ea9e3f"

S = "${WORKDIR}/git"


inherit python_mesonpy

# NOTE: this is a Makefile-only piece of software, so we cannot generate much of the
# recipe automatically - you will need to examine the Makefile yourself and ensure
# that the appropriate arguments are passed in.

do_configure () {
	# Specify any needed configure commands here
	:
}

do_compile () {
	# You will almost certainly need to add additional arguments here
	oe_runmake
}

do_install () {
	# NOTE: unable to determine what to put here - there is a Makefile but no
	# target named "install", so you will need to define this yourself
	:
}

