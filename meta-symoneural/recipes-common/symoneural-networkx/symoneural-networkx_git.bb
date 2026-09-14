# NetworkX for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels: torch 2.14 declares networkx>=2.5.1
# unconditionally (torch.fx graph passes). Acquired 2026-09-14 under the estate rule
# "own what you ship": layer copies are build tooling at most, never the shipped
# provider. Tag networkx-3.6.1 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/util/source/networkx"

SUMMARY = "NetworkX for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/networkx/networkx"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=f7592b173aee2da0e062f9cfa0378e9d"

SRC_URI = "git://github.com/networkx/networkx;protocol=https;nobranch=1;branch=main"
PV = "3.6.1"
SRCREV = "7530809bfa1ea7ed6fdf918a4d1431488953cb1f"

# Mirrors meta-python python3-networkx_3.6.1.bb with one correction: that recipe
# still lists python3-decorator, but networkx 3.6.1's pyproject declares no
# dependencies at all (dependencies = []), so no decorator edge is carried here.
# networkx requires-python is >=3.11,!=3.14.1; the target interpreter is 3.14.7.
inherit python_setuptools_build_meta

RDEPENDS:${PN} += " \
    python3-compression python3-html python3-json python3-netclient python3-numbers \
    python3-pickle python3-profile python3-threading python3-xml \
"
