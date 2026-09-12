# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
#
# The following license files were not able to be identified and are
# represented as "Unknown" below, you will need to check them yourself:
#   metadata/src/copyright.rs
#   protocol/proto/player_license.proto
#
# NOTE: multiple licenses have been detected; they have been separated with &
# in the LICENSE value for now since it is a reasonable assumption that all
# of the licenses apply. If instead there is a choice between the multiple
# licenses then you should change the value to separate the licenses with |
# instead of &. If there is any doubt, check the accompanying documentation
# to determine which situation is applicable.
LICENSE = "MIT AND Unknown"
LIC_FILES_CHKSUM = "file://LICENSE;md5=98b2b0c9a6081259c441045ca68b640f \
                    file://metadata/src/copyright.rs;md5=e9644593d31089f5d3b6f483392ec7dc \
                    file://protocol/proto/player_license.proto;md5=93b9409e7bf39ec20c06077d26c1d8c2"

SRC_URI = "git://github.com/librespot-org/librespot;protocol=https;branch=dev"

# Modify these as desired
PV = "1.0+git"
SRCREV = "d36f9f1907e8cc9d68a93f8ebc6b627b1bf7267d"

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

