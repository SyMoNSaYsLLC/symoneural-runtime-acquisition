# Shared by the symoneural-gstreamer* recipes: ONE pinned GStreamer monorepo (Live runtime), one
# recipe per subproject (core, plugins-base, ...). Each recipe points meson at its subprojects/<x>
# directory of the disposable export and takes every dependency from the sysroot
# (--wrap-mode=nodownload: none of the monorepo's 66 wrap files is ever fetched).
HOMEPAGE = "https://gstreamer.freedesktop.org/"
SECTION = "multimedia"
LICENSE = "LGPL-2.1-or-later"
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Live/src/gstreamer/source/gstreamer"
SRC_URI = "gitsm://gitlab.freedesktop.org/gstreamer/gstreamer.git;protocol=https;branch=1.28"
SRCREV = "070125524a8422e29d3b69a372ed4f62fd343ffa"
PV = "1.28.7"

def gettext_oemeson(d):
    if d.getVar('USE_NLS') == 'no':
        return '-Dnls=disabled'
    return '-Dnls=enabled'
