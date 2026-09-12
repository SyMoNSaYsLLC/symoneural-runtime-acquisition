# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=25efce27fa98f89e99bb6e11f55bf8e8"

SRC_URI = "git://github.com/FlashML-org/FreeToken;protocol=https;branch=main"

# Modify these as desired
PV = "1.0+git"
SRCREV = "9db1a39455a3fb107f3db83e381d10ceadfe5d99"

S = "${WORKDIR}/git"

inherit python_setuptools_build_meta setuptools3

# WARNING: the following rdepends are determined through basic analysis of the
# python sources, and might not be 100% accurate.
RDEPENDS:${PN} += "python3-core"
