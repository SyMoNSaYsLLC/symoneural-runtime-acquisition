# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
#
# The following license files were not able to be identified and are
# represented as "Unknown" below, you will need to check them yourself:
#   src/anthropic/_vendor/httpx_aiohttp/LICENSE
#
# NOTE: multiple licenses have been detected; they have been separated with &
# in the LICENSE value for now since it is a reasonable assumption that all
# of the licenses apply. If instead there is a choice between the multiple
# licenses then you should change the value to separate the licenses with |
# instead of &. If there is any doubt, check the accompanying documentation
# to determine which situation is applicable.
LICENSE = "MIT AND Unknown"
LIC_FILES_CHKSUM = "file://LICENSE;md5=2453eb85b33e21e22cb4fa811c650d75 \
                    file://src/anthropic/_vendor/httpx_aiohttp/LICENSE;md5=6cd99a559ccce444ec3f9ef9d16f9e87"

SRC_URI = "git://github.com/anthropics/anthropic-sdk-python;protocol=https;branch=main"

# Modify these as desired
PV = "1.0+git"
SRCREV = "eb21a4352015686c30f5759e8c2f02d70f5371e2"

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

