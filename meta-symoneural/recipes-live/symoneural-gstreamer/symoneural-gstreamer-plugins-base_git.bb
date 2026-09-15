# GStreamer 1.28.7 'base' plugins and helper libraries (subprojects/gst-plugins-base of the
# acquired monorepo) against the estate's own core (symoneural-gstreamer), mirroring oe-core's
# gstreamer1.0-plugins-base_1.28.7.bb option set with a minimal codec selection for the first pass:
# orc, ogg, vorbis, theora, png, jpeg. No X11, no GL, no ALSA, no pango yet - those are explicit
# follow-on enables, each pulling its oe-core library. Per-plugin packaging is oe-core's own include.
require symoneural-gstreamer.inc
SUMMARY = "GStreamer 1.0 'base' plugins and helper libraries (Live runtime)"
LIC_FILES_CHKSUM = "file://subprojects/gst-plugins-base/COPYING;md5=69333daa044cb77e486cc36129f7a770"

DEPENDS = "symoneural-gstreamer glib-2.0 glib-2.0-native iso-codes util-linux zlib"

inherit symoneural-pristine meson pkgconfig gettext
require recipes-multimedia/gstreamer/gstreamer1.0-plugins-packaging.inc

MESON_SOURCEPATH = "${S}/subprojects/gst-plugins-base"

PACKAGECONFIG ??= "orc ogg vorbis theora png jpeg"
PACKAGECONFIG[orc]    = "-Dorc=enabled,-Dorc=disabled,orc orc-native"
PACKAGECONFIG[alsa]   = "-Dalsa=enabled,-Dalsa=disabled,alsa-lib"
PACKAGECONFIG[jpeg]   = "-Dgl-jpeg=enabled,-Dgl-jpeg=disabled,jpeg"
PACKAGECONFIG[ogg]    = "-Dogg=enabled,-Dogg=disabled,libogg"
PACKAGECONFIG[opus]   = "-Dopus=enabled,-Dopus=disabled,libopus"
PACKAGECONFIG[pango]  = "-Dpango=enabled,-Dpango=disabled,pango"
PACKAGECONFIG[png]    = "-Dgl-png=enabled,-Dgl-png=disabled,libpng"
PACKAGECONFIG[theora] = "-Dtheora=enabled,-Dtheora=disabled,libtheora"
PACKAGECONFIG[vorbis] = "-Dvorbis=enabled,-Dvorbis=disabled,libvorbis"

EXTRA_OEMESON += " \
    --wrap-mode=nodownload \
    -Ddoc=disabled \
    -Dexamples=disabled \
    -Dtests=disabled \
    -Dtools=enabled \
    -Dintrospection=disabled \
    -Dgl=disabled \
    -Dx11=disabled -Dxvideo=disabled -Dxshm=disabled \
    -Dcdparanoia=disabled -Dlibvisual=disabled -Dtremor=disabled -Dqt5=disabled \
    ${@gettext_oemeson(d)} \
"

FILES:${PN}-dev += "${libdir}/gstreamer-1.0/include/gst/gl/gstglconfig.h"
FILES:${MLPREFIX}libgsttag-1.0 += "${datadir}/gst-plugins-base/1.0/license-translations.dict"
