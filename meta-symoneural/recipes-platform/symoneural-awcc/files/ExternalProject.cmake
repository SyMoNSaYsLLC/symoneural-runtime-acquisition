# symoneural: shadow of CMake's ExternalProject module for the AWCC build.
#
# AWCC's CMakeLists.txt declares ONE ExternalProject, libevdev, as a git clone from GitLab at build
# time followed by a meson build - a network fetch the estate forbids. The estate provides libevdev
# from oe-core (built as shared + static, see the Platform estate template). This module is found
# first on CMAKE_MODULE_PATH, includes the real module so every other call behaves normally, and
# turns the libevdev ExternalProject into an empty target whose source_dir / binary_dir point at
# the recipe sysroot. AWCC's own code then sets its imported target to
# <SYMON_LIBEVDEV_LIBDIR>/libevdev.a and <SYMON_LIBEVDEV_INCLUDEDIR> (CMake 4.x stores them as the
# upper-case _EP_SOURCE_DIR / _EP_BINARY_DIR target properties), which is exactly where
# oe-core's libevdev stages them. No line of the acquired tree is changed.
include(${CMAKE_ROOT}/Modules/ExternalProject.cmake)

function(ExternalProject_Add name)
  if(name STREQUAL "libevdev")
    if(NOT SYMON_LIBEVDEV_LIBDIR OR NOT SYMON_LIBEVDEV_INCLUDEDIR)
      message(FATAL_ERROR "symoneural: SYMON_LIBEVDEV_LIBDIR / SYMON_LIBEVDEV_INCLUDEDIR must name the sysroot libevdev")
    endif()
    if(NOT EXISTS "${SYMON_LIBEVDEV_LIBDIR}/libevdev.a")
      message(FATAL_ERROR "symoneural: ${SYMON_LIBEVDEV_LIBDIR}/libevdev.a is missing - oe-core libevdev must be built with -Ddefault_library=both")
    endif()
    if(NOT EXISTS "${SYMON_LIBEVDEV_INCLUDEDIR}/libevdev/libevdev.h")
      message(FATAL_ERROR "symoneural: ${SYMON_LIBEVDEV_INCLUDEDIR}/libevdev/libevdev.h is missing")
    endif()
    add_custom_target(${name})
    set_property(TARGET ${name} PROPERTY _EP_SOURCE_DIR "${SYMON_LIBEVDEV_INCLUDEDIR}")
    set_property(TARGET ${name} PROPERTY _EP_BINARY_DIR "${SYMON_LIBEVDEV_LIBDIR}")
    message(STATUS "symoneural: ExternalProject '${name}' replaced by the sysroot libevdev (${SYMON_LIBEVDEV_LIBDIR}/libevdev.a, ${SYMON_LIBEVDEV_INCLUDEDIR})")
    return()
  endif()
  message(FATAL_ERROR "symoneural: unexpected ExternalProject '${name}' - the estate build declares every input; add it as a pinned component")
endfunction()
