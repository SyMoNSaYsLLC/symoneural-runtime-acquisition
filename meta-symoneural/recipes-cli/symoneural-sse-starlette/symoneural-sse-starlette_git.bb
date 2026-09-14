# sse-starlette for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (mcp sse-starlette>=3.0.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag v3.4.11 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/http/source/sse-starlette"

SUMMARY = "sse-starlette for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/sysid/sse-starlette"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=512780230e4edd77125d98c5f52abafe"

SRC_URI = "git://github.com/sysid/sse-starlette;protocol=https;nobranch=1;branch=main"
PV = "3.4.11"
SRCREV = "6754ef387da97cf6cfbcd1bd5c216b533937b304"

inherit python_setuptools_build_meta
RDEPENDS:${PN} += "symoneural-starlette symoneural-anyio"
