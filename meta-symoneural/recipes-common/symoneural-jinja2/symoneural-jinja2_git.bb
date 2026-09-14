# Jinja2 for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels: torch 2.14 declares jinja2
# unconditionally (torch._inductor renders C++/Triton kernels from templates).
# Acquired 2026-09-14 under the estate rule "own what you ship": layer copies are
# build tooling at most, never the shipped provider. Tag 3.1.6 at the pin below;
# licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/text/source/jinja2"

SUMMARY = "Jinja2 for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/pallets/jinja"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=5dc88300786f1c214c1e9827a5229462"

SRC_URI = "git://github.com/pallets/jinja;protocol=https;nobranch=1;branch=main"
PV = "3.1.6"
SRCREV = "15206881c006c79667fe5154fe80c01c65410679"

# Mirrors oe-core python3-jinja2_3.1.6.bb (ptest omitted: this estate proves runtimes
# with tools/clean-root-proof, not on-target pytest).
inherit python_flit_core

# Jinja2 wheel Requires-Dist: MarkupSafe>=2.0 - the estate-owned provider, not the
# layer's python3-markupsafe. Checked by tools/check-python-runtime-closures.py.
RDEPENDS:${PN} += " \
    symoneural-markupsafe \
    python3-asyncio python3-crypt python3-io python3-json python3-math \
    python3-netclient python3-numbers python3-pickle python3-pprint python3-shell \
    python3-threading \
"
