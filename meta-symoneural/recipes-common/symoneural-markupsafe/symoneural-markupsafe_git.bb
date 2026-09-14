# MarkupSafe for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels: Jinja2 declares MarkupSafe>=2.0, and
# torch 2.14 declares jinja2 unconditionally. Acquired 2026-09-14 under the estate
# rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag 3.0.3 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/text/source/markupsafe"

SUMMARY = "MarkupSafe for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/pallets/markupsafe"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=ffeffa59c90c9c4a033c7574f8f3fb75"

SRC_URI = "git://github.com/pallets/markupsafe;protocol=https;nobranch=1;branch=main"
PV = "3.0.3"
SRCREV = "297fc8e356e6836a62087949245d09a28e9f1b13"

# Mirrors oe-core python3-markupsafe_3.0.3.bb. The _speedups C extension is
# cross-compiled by setuptools against the target python3 sysconfig.
inherit python_setuptools_build_meta

RDEPENDS:${PN} += "python3-html python3-stringold"
