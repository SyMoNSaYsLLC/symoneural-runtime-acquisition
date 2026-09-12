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
LIC_FILES_CHKSUM = "file://LICENSE.md;md5=c624803bdf6fc1c4ce39f5ae11d7bd05"

SRC_URI = "git://github.com/encode/httpx;protocol=https;branch=master"

# Modify these as desired
PV = "1.0+git"
SRCREV = "26d48e0634e6ee9cdc0533996db289ce4b430177"

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

