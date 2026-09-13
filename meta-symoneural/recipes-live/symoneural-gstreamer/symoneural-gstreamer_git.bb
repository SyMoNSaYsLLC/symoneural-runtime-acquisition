# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
#
# The following license files were not able to be identified and are
# represented as "Unknown" below, you will need to check them yourself:
#   LICENSE
#   subprojects/gst-devtools/dots-viewer/static/dist/bundle.js.LICENSE.txt
#   subprojects/gst-docs/LICENSE.BSD
#   subprojects/gst-docs/LICENSE.CC-BY-SA-4.0
#   subprojects/gst-docs/LICENSE.OPL
#   subprojects/gst-docs/markdown/frequently-asked-questions/legal.md
#   subprojects/gst-docs/markdown/legal-information.md
#   subprojects/gst-editing-services/COPYING
#   subprojects/gst-editing-services/COPYING.LIB
#   subprojects/gst-libav/COPYING
#   subprojects/gst-plugins-bad/ext/sctp/usrsctp/LICENSE.md
#   subprojects/gst-plugins-bad/gst-libs/gst/codecparsers/dboolhuff.LICENSE
#   subprojects/gst-plugins-bad/gst/dvbsubenc/libimagequant/COPYRIGHT
#   subprojects/gst-plugins-bad/sys/directshow/strmbase/LICENSE
#   subprojects/gst-plugins-base/COPYING
#   subprojects/gst-plugins-base/gst-libs/gst/tag/licenses-tables.dat
#   subprojects/gst-plugins-base/gst-libs/gst/tag/licenses.c
#   subprojects/gst-plugins-base/gst-libs/gst/tag/mklicensestables.c
#   subprojects/gst-plugins-base/tests/files/license-uris
#   subprojects/gst-plugins-good/gst/isomp4/LEGAL
#   subprojects/gst-plugins-good/gst/rtp/dboolhuff.LICENSE
#   subprojects/gst-plugins-good/gst/rtsp/COPYING.MIT
#   subprojects/gst-rtsp-server/COPYING
#   subprojects/gst-rtsp-server/COPYING.LIB
#   subprojects/gstreamer-sharp/sources/generated/Gst.Tags/TagLicenseFlags.cs
#   subprojects/gstreamer/COPYING
#
# NOTE: multiple licenses have been detected; they have been separated with &
# in the LICENSE value for now since it is a reasonable assumption that all
# of the licenses apply. If instead there is a choice between the multiple
# licenses then you should change the value to separate the licenses with |
# instead of &. If there is any doubt, check the accompanying documentation
# to determine which situation is applicable.
# LICENSE established from the licence text in the acquired tree. recipetool had
# emitted a non-SPDX token ('Unknown'/'Apache'), which newer OE-Core's SPDX parser
# rejects outright: do_populate_lic dies with
# "AttributeError: 'UnknownId' object has no attribute 'name'".
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Live/src/gstreamer/source/gstreamer"

LICENSE = "LGPL-2.1-or-later"
LIC_FILES_CHKSUM = "file://LICENSE;md5=69333daa044cb77e486cc36129f7a770 \
                    file://subprojects/gst-devtools/dots-viewer/static/dist/bundle.js.LICENSE.txt;md5=55aa52cfa7f72e34297e0c23c328498d \
                    file://subprojects/gst-devtools/validate/COPYING;md5=a6f89e2100d9b6cdffcea4f398e37343 \
                    file://subprojects/gst-docs/LICENSE.BSD;md5=da3ad60ef7ec7817e6abd67effc8d3d7 \
                    file://subprojects/gst-docs/LICENSE.CC-BY-SA-4.0;md5=cf58529a4bfbca0b10c68fbf559caf7c \
                    file://subprojects/gst-docs/LICENSE.LGPL-2.1;md5=4b54a1fd55a448865a0b32d41598759d \
                    file://subprojects/gst-docs/LICENSE.MIT;md5=a50b04414e4853ca21949a0fb1b35f36 \
                    file://subprojects/gst-docs/LICENSE.OPL;md5=a3462923a35559673975080d5a8dd1ba \
                    file://subprojects/gst-docs/markdown/frequently-asked-questions/legal.md;md5=210f31a3094a906e445c0d53000b65f0 \
                    file://subprojects/gst-docs/markdown/legal-information.md;md5=8d63b06666779e31e016de0ef1900ba4 \
                    file://subprojects/gst-editing-services/COPYING;md5=69333daa044cb77e486cc36129f7a770 \
                    file://subprojects/gst-editing-services/COPYING.LIB;md5=69333daa044cb77e486cc36129f7a770 \
                    file://subprojects/gst-examples/COPYING;md5=4fbd65380cdd255951079008b364516c \
                    file://subprojects/gst-examples/webrtc/LICENSE;md5=31d1631886d78e9ff38b6c3b05bb9e9a \
                    file://subprojects/gst-libav/COPYING;md5=69333daa044cb77e486cc36129f7a770 \
                    file://subprojects/gst-plugins-bad/COPYING;md5=4fbd65380cdd255951079008b364516c \
                    file://subprojects/gst-plugins-bad/ext/sctp/usrsctp/LICENSE.md;md5=ffcf846341f3856d79a483eafa18e2a5 \
                    file://subprojects/gst-plugins-bad/gst-libs/gst/codecparsers/dboolhuff.LICENSE;md5=d5b04755015be901744a78cc30d390d4 \
                    file://subprojects/gst-plugins-bad/gst/dvbsubenc/libimagequant/COPYRIGHT;md5=66da4798e2782862e204c1de7115688c \
                    file://subprojects/gst-plugins-bad/sys/directshow/strmbase/LICENSE;md5=5355ff188aa9a1dc019e8e22855b2fc0 \
                    file://subprojects/gst-plugins-bad/sys/dwrite/libcaption/LICENSE.txt;md5=da1082841ec483429abb0e8c8779d6dc \
                    file://subprojects/gst-plugins-base/COPYING;md5=69333daa044cb77e486cc36129f7a770 \
                    file://subprojects/gst-plugins-base/gst-libs/gst/tag/licenses-tables.dat;md5=05a9f393038fe62d7591583c94ae618c \
                    file://subprojects/gst-plugins-base/gst-libs/gst/tag/licenses.c;md5=42174dc3dc2bb4623ab4647b62fdbc9b \
                    file://subprojects/gst-plugins-base/gst-libs/gst/tag/mklicensestables.c;md5=e7a44642b1f96d0ea9f7a1f5b1f01167 \
                    file://subprojects/gst-plugins-base/tests/files/license-uris;md5=ab312cb2fece81fcc6bd2f8a421c3097 \
                    file://subprojects/gst-plugins-good/COPYING;md5=a6f89e2100d9b6cdffcea4f398e37343 \
                    file://subprojects/gst-plugins-good/gst/isomp4/LEGAL;md5=786fb4f4d837bb6bc0e351a5c4bccd4f \
                    file://subprojects/gst-plugins-good/gst/rtp/dboolhuff.LICENSE;md5=4951f35dffe167c1b3b63049741c1f79 \
                    file://subprojects/gst-plugins-good/gst/rtsp/COPYING.MIT;md5=5c99bf83b0380f1df49ed9a5306ed708 \
                    file://subprojects/gst-plugins-ugly/COPYING;md5=a6f89e2100d9b6cdffcea4f398e37343 \
                    file://subprojects/gst-python/COPYING;md5=c34deae4e395ca07e725ab0076a5f740 \
                    file://subprojects/gst-rtsp-server/COPYING;md5=69333daa044cb77e486cc36129f7a770 \
                    file://subprojects/gst-rtsp-server/COPYING.LIB;md5=69333daa044cb77e486cc36129f7a770 \
                    file://subprojects/gstreamer-sharp/COPYING;md5=4b54a1fd55a448865a0b32d41598759d \
                    file://subprojects/gstreamer-sharp/sources/generated/Gst.Tags/TagLicenseFlags.cs;md5=b967c9946c433a7643acc002f779b6f9 \
                    file://subprojects/gstreamer/COPYING;md5=69333daa044cb77e486cc36129f7a770"

SRC_URI = "gitsm://gitlab.freedesktop.org/gstreamer/gstreamer.git;protocol=https;branch=1.28"

# Modify these as desired
# PV is the real upstream release tag at SRCREV, not recipetool's "1.0+git"
# placeholder. The placeholder is not merely cosmetic: it names every .ipk
# <pkg>_1.0+git-r0, and symoneural-pristine exports it as the wheel version
# via *_PRETEND_VERSION/*_BYPASS, where uv-dynamic-versioning parsed it and
# died with IndexError on int(parts[index]).
PV = "1.28.7"
SRCREV = "070125524a8422e29d3b69a372ed4f62fd343ffa"

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

