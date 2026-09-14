# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# Unable to find any files that looked like license statements. Check the accompanying
# documentation and source headers and set LICENSE and LIC_FILES_CHKSUM accordingly.
#
# NOTE: LICENSE is being set to "CLOSED" to allow you to at least start building - if
# this is not accurate with respect to the licensing of the software being built (it
# will not be in most cases) you must specify the correct value before using this
# recipe for anything other than initial testing/development!
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Crypto/src/stratum/source/sv2-spec"

# REFERENCE-ONLY, but not unlicensed: the tree carries License/BSD-3-Clause and
# License/CC0-1.0. CLOSED would have been a false statement about a dual-permissive
# spec. The files sit in a License/ DIRECTORY, which is why scanners miss them.
LICENSE = "BSD-3-Clause OR CC0-1.0"
LIC_FILES_CHKSUM = "file://License/BSD-3-Clause;md5=bd3412dad92085eb3afc5bf9d701adf0 \
                    file://License/CC0-1.0;md5=65d3616852dbf7b1a6d4b53b00626032"

SRC_URI = "git://github.com/stratum-mining/sv2-spec;protocol=https;branch=main"

# Modify these as desired
PV = "1.0+git"
SRCREV = "67d2178e12b2c3da948f656b0e1030afafb8d891"

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

