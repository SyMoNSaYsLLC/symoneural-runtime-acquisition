# pycparser for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (cffi pycparser). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag release_v3.00 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/ffi/source/pycparser"

SUMMARY = "pycparser for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/eliben/pycparser"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=9761c3ffee7ba99c60dca0408fd3262b"

SRC_URI = "git://github.com/eliben/pycparser;protocol=https;nobranch=1;branch=main"
PV = "3.00"
SRCREV = "77de509f0268f44ee587b5a4d9f0d680e269fcae"

inherit python_setuptools_build_meta
# pycparser 3.00 declares [build-system] requires = ["setuptools>=69", "wheel"];
# python_setuptools_build_meta stages only python3-setuptools-native, so
# pyproject-build --no-isolation aborted its dependency check with
#   ERROR Unmet dependencies ... wheel  wanted: any  found: not installed
# wheel is BUILD tooling, never shipped, so the estate rule "own what you ship;
# borrow what you only build with" makes the OE-Core copy the correct provider.
DEPENDS += "python3-wheel-native"
