# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=09280955509d1c4ca14bae02f21d49a6 \
                    file://pydantic-core/LICENSE;md5=ab599c188b4a314d2856b3a55030c75c"

SRC_URI = "git://github.com/pydantic/pydantic;protocol=https;branch=v2.13-fixes"

# Modify these as desired
PV = "1.0+git"
SRCREV = "001dea020e0809844e5b17666432c9135a976f46"

S = "${WORKDIR}/git"

# NOTE: the following library dependencies are unknown, ignoring: h
#       (this is based on recipes that have previously been built and packaged)

inherit python_hatchling

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
	# This is a guess; additional arguments may be required
	oe_runmake install
}

