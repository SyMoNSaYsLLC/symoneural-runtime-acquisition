# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
#
# The following license files were not able to be identified and are
# represented as "Unknown" below, you will need to check them yourself:
#   src/anthropic/_vendor/httpx_aiohttp/LICENSE
#
# NOTE: multiple licenses have been detected; they have been separated with &
# in the LICENSE value for now since it is a reasonable assumption that all
# of the licenses apply. If instead there is a choice between the multiple
# licenses then you should change the value to separate the licenses with |
# instead of &. If there is any doubt, check the accompanying documentation
# to determine which situation is applicable.
# LICENSE established from the licence text in the acquired tree. recipetool had
# emitted a non-SPDX token ('Unknown'/'Apache'), which newer OE-Core's SPDX parser
# rejects outright: do_populate_lic dies with
# "AttributeError: 'UnknownId' object has no attribute 'name'".
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/anthropic/source/anthropic-sdk-python"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=2453eb85b33e21e22cb4fa811c650d75 \
                    file://src/anthropic/_vendor/httpx_aiohttp/LICENSE;md5=6cd99a559ccce444ec3f9ef9d16f9e87"

SRC_URI = "git://github.com/anthropics/anthropic-sdk-python;protocol=https;branch=main"

# Modify these as desired
# PV is the real upstream release tag at SRCREV, not recipetool's "1.0+git"
# placeholder. The placeholder is not merely cosmetic: it names every .ipk
# <pkg>_1.0+git-r0, and symoneural-pristine exports it as the wheel version
# via *_PRETEND_VERSION/*_BYPASS, where uv-dynamic-versioning parsed it and
# died with IndexError on int(parts[index]).
PV = "1.5.0"
SRCREV = "eb21a4352015686c30f5759e8c2f02d70f5371e2"

# recipetool emitted empty do_configure/do_compile/do_install stubs ALONGSIDE
# a real build-class inherit. A recipe-level function OVERRIDES the inherited
# one, so the stubs silently won: this recipe installed nothing (or ran bare
# `make`) despite inheriting a working class. Stubs removed so the inherited
# class actually runs.
inherit python_hatchling

# NOTE: no Makefile found, unable to determine what needs to be done





# PEP-517 backend needs hatch-fancy-pypi-readme natively. Proven by build failure.
DEPENDS += "python3-hatch-fancy-pypi-readme-native"

# anthropic-sdk-python pins hatchling==1.26.3 EXACTLY. The stack supplies a
# different version. hatchling is a build backend: it produces the wheel and
# contributes no code to it, and the exact pin is upstream being conservative
# rather than a hard requirement. The check is skipped and the stack version used.
# DECISION RECORDED: if the exact backend version matters, package 1.26.3.
PEP517_BUILD_OPTS += "--skip-dependency-check"

# Runtime edges read from this wheel's dist-info METADATA Requires-Dist (estate-provided
# distributions). OE does not derive RDEPENDS from wheel metadata; the recipe must.
# Checked by tools/check-python-runtime-closures.py.
# runtime closure of the anthropic wheel (tools/check-python-runtime-closures.py --runtime CLI):
# anyio, docstring-parser, httpx2, jiter, pydantic, sniffio, typing-extensions
RDEPENDS:${PN} += "symoneural-pydantic symoneural-anyio symoneural-docstring-parser symoneural-httpx2 symoneural-jiter symoneural-sniffio symoneural-typing-extensions"
