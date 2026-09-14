# Recipe created by recipetool, then CURATED for SyMoNeuRaL.
# LICENSE / LIC_FILES_CHKSUM / PV verified against the pinned upstream source tree.
# SRCREV and SRC_URI are the acquisition pins - do not change without re-verifying.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Build/src/bitbake/source"

LICENSE = "GPL-2.0-only AND MIT"
# LIC_FILES_CHKSUM restored to recipetool's full file list.
# Rationale: over-declaring makes bitbake detect licence drift across ALL
# licence-bearing files; under-declaring hides it. Curating this down to one
# canonical file dropped OpenBLAS from 8 files to 1, losing coverage of the
# vendored LAPACK, LAPACKE, ReLAPACK and netlib BLAS reference licences.
# Every path below EXISTS in the pinned tree 046a90b0 (yocto-6.1_M2-99). The
# recipetool list named lib/bs4, lib/progressbar, lib/simplediff and contrib/vim
# paths from the scarthgap-era tree; master moved vendored code to lib/bb/_vendor/
# and its licences to vendor/licenses/ (ply). Verified with md5sum on 2026-09-13.
LIC_FILES_CHKSUM = "file://LICENSE;md5=7e4cfe1c8dee5c6fe34c79c38d7b6b52 \
                    file://LICENSE.GPL-2.0-only;md5=4ee23c52855c222cba72583d301d2338 \
                    file://LICENSE.MIT;md5=030cb33d2af49ccebca74d0588b84a21 \
                    file://doc/COPYING.GPL;md5=751419260aa954499f7abaabaa882bbe \
                    file://doc/COPYING.MIT;md5=5750f3aa4ea2b00c2bf21b2b2a7b714d \
                    file://lib/bb/_vendor/beautifulsoup4.LICENSE;md5=96e0034f7c9443910c486773aa1ed9ac \
                    file://lib/bb/_vendor/progressbar/LICENSE.txt;md5=6d38698d6f983adff50eb75d8cb26e6b \
                    file://lib/bb/_vendor/simplediff/LICENSE;md5=9476fb642383515b0a38a680778c01d5 \
                    file://lib/bb/_vendor/tomli/LICENSE;md5=aaaaf0879d17df0110d1aa8c8c9f46f5 \
                    file://lib/bb/_vendor/typing_extensions.LICENSE;md5=fcf6b249c2641540219a727f35d8d2c2 \
                    file://vendor/licenses/ply/LICENSE;md5=cecb03f754c9edab5fd0718adedda413 \
                    file://lib/toaster/toastergui/static/jquery-treetable-license/GPL-LICENSE.txt;md5=4e5d6fc4fb57eb64189113f37a5a7f0b \
                    file://lib/toaster/toastergui/static/jquery-treetable-license/MIT-LICENSE.txt;md5=327473913c507bd955504292ca0ebaa3"

SRC_URI = "git://git.openembedded.org/bitbake;protocol=https;branch=master"

# Modify these as desired
# lib/bb/__init__.py __version__ at the pin; the tree is yocto-6.1_M2-99, untagged
PV = "2.19.1+git"
SRCREV = "046a90b0e9b7b914b7a95aec579cdc3fc9c7617a"

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

