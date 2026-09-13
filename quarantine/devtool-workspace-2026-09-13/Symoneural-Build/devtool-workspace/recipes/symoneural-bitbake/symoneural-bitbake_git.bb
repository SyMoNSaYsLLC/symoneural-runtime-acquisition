# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
LICENSE = "GPL-2.0-only AND MIT"
# LIC_FILES_CHKSUM restored to recipetool's full file list.
# Rationale: over-declaring makes bitbake detect licence drift across ALL
# licence-bearing files; under-declaring hides it. Curating this down to one
# canonical file dropped OpenBLAS from 8 files to 1, losing coverage of the
# vendored LAPACK, LAPACKE, ReLAPACK and netlib BLAS reference licences.
LIC_FILES_CHKSUM = "file://LICENSE;md5=7e4cfe1c8dee5c6fe34c79c38d7b6b52 \
                    file://LICENSE.GPL-2.0-only;md5=4ee23c52855c222cba72583d301d2338 \
                    file://LICENSE.MIT;md5=030cb33d2af49ccebca74d0588b84a21 \
                    file://contrib/vim/LICENSE.txt;md5=9a8bb0266376912777a9634ba661d969 \
                    file://doc/COPYING.GPL;md5=751419260aa954499f7abaabaa882bbe \
                    file://doc/COPYING.MIT;md5=5750f3aa4ea2b00c2bf21b2b2a7b714d \
                    file://lib/bs4/COPYING.txt;md5=83e365dc17176bd72ba7d08ca0555efa \
                    file://lib/progressbar/LICENSE.txt;md5=6d38698d6f983adff50eb75d8cb26e6b \
                    file://lib/simplediff/LICENSE;md5=9476fb642383515b0a38a680778c01d5 \
                    file://lib/toaster/toastergui/static/jquery-treetable-license/GPL-LICENSE.txt;md5=4e5d6fc4fb57eb64189113f37a5a7f0b \
                    file://lib/toaster/toastergui/static/jquery-treetable-license/MIT-LICENSE.txt;md5=327473913c507bd955504292ca0ebaa3"

SRC_URI = "git://git.openembedded.org/bitbake;protocol=https;branch=master"

# Modify these as desired
PV = "2.16.0+git"
SRCREV = "046a90b0e9b7b914b7a95aec579cdc3fc9c7617a"

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

