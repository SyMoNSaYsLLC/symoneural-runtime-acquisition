# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
#
# NOTE: multiple licenses have been detected; they have been separated with &
# in the LICENSE value for now since it is a reasonable assumption that all
# of the licenses apply. If instead there is a choice between the multiple
# licenses then you should change the value to separate the licenses with |
# instead of &. If there is any doubt, check the accompanying documentation
# to determine which situation is applicable.
LICENSE = "Apache-2.0 AND ISC AND MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=2ee41112a44fe7014dce33e26468ba93 \
                    file://samples/nodejs-compat-fs-graceful/graceful-fs/LICENSE;md5=163972d49c2f7a3d3b687aeb48e9e3c9 \
                    file://src/rust/cxx/LICENSE-APACHE;md5=22a53954e4e0ec258dfce4391e905dac \
                    file://src/rust/cxx/LICENSE-MIT;md5=b377b220f43d747efdec40d69fcaa69d \
                    file://src/rust/cxx/flags/LICENSE-APACHE;md5=22a53954e4e0ec258dfce4391e905dac \
                    file://src/rust/cxx/flags/LICENSE-MIT;md5=b377b220f43d747efdec40d69fcaa69d \
                    file://src/rust/cxx/gen/build/LICENSE-APACHE;md5=22a53954e4e0ec258dfce4391e905dac \
                    file://src/rust/cxx/gen/build/LICENSE-MIT;md5=b377b220f43d747efdec40d69fcaa69d \
                    file://src/rust/cxx/gen/cmd/LICENSE-APACHE;md5=22a53954e4e0ec258dfce4391e905dac \
                    file://src/rust/cxx/gen/cmd/LICENSE-MIT;md5=b377b220f43d747efdec40d69fcaa69d \
                    file://src/rust/cxx/gen/lib/LICENSE-APACHE;md5=22a53954e4e0ec258dfce4391e905dac \
                    file://src/rust/cxx/gen/lib/LICENSE-MIT;md5=b377b220f43d747efdec40d69fcaa69d \
                    file://src/rust/cxx/macro/LICENSE-APACHE;md5=22a53954e4e0ec258dfce4391e905dac \
                    file://src/rust/cxx/macro/LICENSE-MIT;md5=b377b220f43d747efdec40d69fcaa69d"

SRC_URI = "git://github.com/cloudflare/workerd;protocol=https;branch=main"

# Modify these as desired
PV = "1.0+git"
SRCREV = "909e388c86905a217391cb557ac3260f1daff3d0"

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

