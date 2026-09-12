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
LIC_FILES_CHKSUM = "file://LICENSE.md;md5=5c778842f66a649636561c423c0eec2e"

SRC_URI = "git://github.com/encode/uvicorn;protocol=https;branch=main"

# Modify these as desired
PV = "1.0+git"
SRCREV = "8988c23704fc373c9206cca53ec57dd8ad7f44a5"

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

