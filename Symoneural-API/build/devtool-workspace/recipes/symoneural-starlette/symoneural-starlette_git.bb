# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
#
# The following license files were not able to be identified and are
# represented as "Unknown" below, you will need to check them yourself:
#   LICENSE.md
LICENSE = "Unknown"
LIC_FILES_CHKSUM = "file://LICENSE.md;md5=11e8c8dbfd5fa373c703de492140ff7a"

SRC_URI = "git://github.com/encode/starlette;protocol=https;branch=main"

# Modify these as desired
PV = "1.0+git"
SRCREV = "4f250d6b814587e20c5365f0a5f0c4d42bcb929f"

S = "${WORKDIR}/git"

inherit python_hatchling

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

