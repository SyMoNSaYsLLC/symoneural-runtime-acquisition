# AWCC 1.19.0 - the unofficial Alienware Command Center for Linux (Alienware / Dell G series:
# thermal and fan modes, G-mode, lighting; daemon + CLI + ImGui GUI). GPL-3.0. Approved by Garrett
# on 2026-09-14 as a SEPARATE GPL-3.0 EXECUTABLE in the Platform runtime: its own package and
# process, never linked into proprietary or native estate libraries, GPL obligations preserved.
#
# Upstream's CMakeLists.txt fetches six projects from MOVING branches at configure time
# (FetchContent) and clones libevdev from GitLab (ExternalProject). The estate forbids network
# in a build, so: the six are pinned Platform components handed in through SYMON_DEP_TREES and
# FETCHCONTENT_SOURCE_DIR_* with FETCHCONTENT_FULLY_DISCONNECTED; libevdev comes from oe-core
# (shared + static) through the recipe's ExternalProject.cmake shadow on CMAKE_MODULE_PATH.
# No file of the acquired tree is modified. GL is oe-core's libglvnd (feature glvnd), X11 only
# (GLFW_BUILD_WAYLAND=OFF) for the qemux86-64 baseline.
#
# Run-time boundary, recorded, not provided here: the daemon talks to firmware through the
# acpi_call out-of-tree kernel module (/proc/acpi/call) - a separate acquisition; without it the
# executable starts and answers --help/--version but cannot control hardware.
SUMMARY = "AWCC - Alienware / Dell G-series control (thermal modes, G-mode, lighting): daemon, CLI, GUI"
HOMEPAGE = "https://github.com/tr1xem/AWCC"
SECTION = "base"
LICENSE = "GPL-3.0-only"
LIC_FILES_CHKSUM = "file://LICENSE;md5=641dd5661bc2769a54c6214cdbcce43b"

SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Platform/src/alienware/source/AWCC"
SRCREV = "0ec42c4b3ddc3c4e412ad69353cd251e1f348280"
PV = "1.19.0"

# name:component - exported to ${SYMON_DEPS_DIR}/<name> after tools/ingest-tree verify <component>
SYMON_DEP_TREES = "loguru:loguru json:json glfw:glfw imgui:imgui libusb:libusb-cmake stb:stb"

SRC_URI += "file://ExternalProject.cmake"

inherit symoneural-pristine cmake pkgconfig features_check
REQUIRED_DISTRO_FEATURES = "x11 opengl glvnd"

# system libraries from oe-core (dynamically linked, except libevdev which upstream consumes as a
# static archive): GL dispatch, X11 for GLFW's X11 backend, libudev for libusb's hotplug, libevdev
DEPENDS = "virtual/libgl libx11 libxrandr libxinerama libxcursor libxi libxext xorgproto libevdev udev"

EXTRA_OECMAKE += " \
    -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
    -DFETCHCONTENT_QUIET=OFF \
    -DFETCHCONTENT_SOURCE_DIR_LOGURU=${SYMON_DEPS_DIR}/loguru \
    -DFETCHCONTENT_SOURCE_DIR_JSON=${SYMON_DEPS_DIR}/json \
    -DFETCHCONTENT_SOURCE_DIR_GLFW=${SYMON_DEPS_DIR}/glfw \
    -DFETCHCONTENT_SOURCE_DIR_IMGUI=${SYMON_DEPS_DIR}/imgui \
    -DFETCHCONTENT_SOURCE_DIR_LIBUSB=${SYMON_DEPS_DIR}/libusb \
    -DFETCHCONTENT_SOURCE_DIR_STB=${SYMON_DEPS_DIR}/stb \
    -DGLFW_BUILD_X11=ON -DGLFW_BUILD_WAYLAND=OFF \
    -DLIBUSB_INSTALL_TARGETS=OFF \
    -DCMAKE_MODULE_PATH=${UNPACKDIR} \
    -DSYMON_LIBEVDEV_INCLUDEDIR=${STAGING_INCDIR}/libevdev-1.0 \
    -DSYMON_LIBEVDEV_LIBDIR=${STAGING_LIBDIR} \
"

do_configure:prepend() {
    # the shadow module must be the one CMake finds; the sysroot must hold the static libevdev
    [ -f ${UNPACKDIR}/ExternalProject.cmake ] || bbfatal "ExternalProject.cmake shadow missing from ${UNPACKDIR}"
    [ -f ${STAGING_LIBDIR}/libevdev.a ] || bbfatal "libevdev.a missing in the sysroot: the Platform estate template must build libevdev with -Ddefault_library=both"
    for dep in loguru json glfw imgui libusb stb; do
        [ -d ${SYMON_DEPS_DIR}/$dep ] || bbfatal "dependency export ${SYMON_DEPS_DIR}/$dep missing (SYMON_DEP_TREES)"
    done
}

do_install:append() {
    # upstream installs an absolute /etc/systemd/system unit even on non-systemd distributions;
    # it is inert data here and stays in the package for a systemd host. Nothing else to move.
    [ -x ${D}${bindir}/awcc ] || bbfatal "awcc executable not installed"
    [ -f ${D}${sysconfdir}/awcc/database.json ] || bbfatal "database.json not installed"
    [ -f ${D}${sysconfdir}/udev/rules.d/70-awcc.rules ] || bbfatal "udev rules not installed"
}

FILES:${PN} += "${datadir}/icons ${datadir}/applications ${sysconfdir}/systemd"

# GLFW's X11 backend loads its libraries at run time with dlopen (libX11.so.6, libXrandr.so.2,
# libXinerama.so.1, libXcursor.so.1, libXi.so.6, libXrender.so.1, libXext.so.6; glfw/src/x11_*.c),
# so the automatic shared-library dependencies (libglvnd, libudev1, libstdc++6 ...) do not see them.
# Declared explicitly; the first staged-install proof caught their absence in the package's Depends.
RDEPENDS:${PN} += "libx11 libxrandr libxinerama libxcursor libxi libxrender libxext"
# /etc/awcc/database.json is data upstream ships; keep it out of CONFFILES so upgrades replace it
