# GStreamer 1.28.7 CORE from the acquired monorepo (subprojects/gstreamer), built with meson
# against oe-core's glib/libxml2 exactly as oe-core's gstreamer1.0_1.28.7.bb does - same
# version, same option set, but from the estate's own pinned tree (SYMONEURAL-OWNED ruling for
# Live). The monorepo's other subprojects (plugins-base/good/bad/ugly, libav, rtsp-server ...)
# are follow-on recipes; nothing is fetched from the monorepo's 66 wrap files (meson runs with
# --wrap-mode=nodownload and every dependency comes from the sysroot).
SUMMARY = "GStreamer 1.0 multimedia framework - core library and tools (Live runtime)"
HOMEPAGE = "https://gstreamer.freedesktop.org/"
SECTION = "multimedia"
LICENSE = "LGPL-2.1-or-later"
LIC_FILES_CHKSUM = "file://subprojects/gstreamer/COPYING;md5=69333daa044cb77e486cc36129f7a770"

SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Live/src/gstreamer/source/gstreamer"
SRC_URI = "gitsm://gitlab.freedesktop.org/gstreamer/gstreamer.git;protocol=https;branch=1.28"
SRCREV = "070125524a8422e29d3b69a372ed4f62fd343ffa"
PV = "1.28.7"

DEPENDS = "glib-2.0 glib-2.0-native libxml2 bison-native flex-native"

inherit symoneural-pristine meson pkgconfig gettext

MESON_SOURCEPATH = "${S}/subprojects/gstreamer"

PACKAGECONFIG ??= "check debug tools"
PACKAGECONFIG[debug] = "-Dgst_debug=true,-Dgst_debug=false"
PACKAGECONFIG[tracer-hooks] = "-Dtracer_hooks=true,-Dtracer_hooks=false"
PACKAGECONFIG[coretracers] = "-Dcoretracers=enabled,-Dcoretracers=disabled"
PACKAGECONFIG[check] = "-Dcheck=enabled,-Dcheck=disabled"
PACKAGECONFIG[unwind] = "-Dlibunwind=enabled,-Dlibunwind=disabled,libunwind"
PACKAGECONFIG[dw] = "-Dlibdw=enabled,-Dlibdw=disabled,elfutils"
PACKAGECONFIG[bash-completion] = "-Dbash-completion=enabled,-Dbash-completion=disabled,bash-completion"
PACKAGECONFIG[tools] = "-Dtools=enabled,-Dtools=disabled"

def gettext_oemeson(d):
    if d.getVar('USE_NLS') == 'no':
        return '-Dnls=disabled'
    return '-Dnls=enabled'

EXTRA_OEMESON += " \
    --wrap-mode=nodownload \
    -Ddoc=disabled \
    -Dexamples=disabled \
    -Dtests=disabled \
    -Dbenchmarks=disabled \
    -Ddbghelp=disabled \
    -Dintrospection=disabled \
    ${@gettext_oemeson(d)} \
"

PACKAGES += "${PN}-bash-completion"
FILES:${PN} += "${libdir}/gstreamer-1.0/*.so"
FILES:${PN}-dev += "${libdir}/gstreamer-1.0/*.a ${libdir}/gstreamer-1.0/include"
FILES:${PN}-bash-completion += "${datadir}/bash-completion/completions/ ${datadir}/bash-completion/helpers/gst*"
FILES:${PN}-dbg += "${datadir}/gdb ${datadir}/gstreamer-1.0/gdb"
