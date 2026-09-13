# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/ml/source/safetensors"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=86d3f3a95c324c9479bd8986968f4327 \
                    file://bindings/python/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327 \
                    file://safetensors/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327"

SRC_URI = "git://github.com/huggingface/safetensors;protocol=https;nobranch=1;branch=master"

# Modify these as desired
# PV is the real upstream release tag at SRCREV, not recipetool's "1.0+git"
# placeholder. The placeholder is not merely cosmetic: it names every .ipk
# <pkg>_1.0+git-r0, and symoneural-pristine exports it as the wheel version
# via *_PRETEND_VERSION/*_BYPASS, where uv-dynamic-versioning parsed it and
# died with IndexError on int(parts[index]).
PV = "0.8.0"
SRCREV = "a406ca3e7a90598be0cd05a50069cb9bf5ef6ba6"


# recipe automatically - you will need to examine the Makefile yourself and ensure
# that the appropriate arguments are passed in.

# --- BUILD SYSTEM -------------------------------------------------------------
# Was a recipetool STUB: no build-system class, so bitbake ran bare `make` and a
# ':' no-op do_install left an empty ${D}, which R12 correctly failed.
#
# safetensors is a Rust core with PyO3 bindings. bindings/python declares
# maturin>=1.0,<2.0; OE ships python3-maturin 1.15.0.
#
# ${S} STAYS AT THE EXPORT ROOT. Moving it to bindings/python would invalidate
# every LIC_FILES_CHKSUM path, and re-anchoring those with ../../ escapes the
# export - which symoneural-pristine's do_unpack assertion refuses, correctly.
# PEP517_SOURCE_PATH is the lever python_pep517 provides for exactly this.
PEP517_SOURCE_PATH = "${S}/bindings/python"
CARGO_MANIFEST_PATH = "${S}/bindings/python/Cargo.toml"

inherit python_maturin cargo-update-recipe-crates

DEPENDS += "python3-maturin-native"

# UPSTREAM SHIPS NO Cargo.lock ANYWHERE - only three Cargo.toml. Without a
# lockfile the crate set resolves from crates.io at build time: non-deterministic
# and offline-breaking. Ours is generated and RECORDED as such:
#   PIN-ORIGIN: SYMONEURAL-GENERATED, cargo 1.97.1 / rustc 1.97.1, 2026-09-13
#   46 packages. See PIN-ORIGIN.md beside this recipe.
# A pin that is ours rather than upstream's is honest once recorded; an
# unrecorded one would read as upstream provenance it does not have.
# bitbake searches FILESPATH for file:// entries, and THISDIR is not on it by
# default - without this the parse fails with "Unable to get checksum for
# SRC_URI entry".
FILESEXTRAPATHS:prepend := "${THISDIR}:"
SRC_URI += "file://Cargo.lock"

do_configure:prepend() {
    lock="${UNPACKDIR}/Cargo.lock"
    [ -f "$lock" ] || lock="${WORKDIR}/Cargo.lock"
    [ -f "$lock" ] || bbfatal "Cargo.lock not found in UNPACKDIR or WORKDIR"
    install -m 0644 "$lock" "${S}/bindings/python/Cargo.lock"
    bbnote "installed SyMoNeuRaL-generated Cargo.lock (PIN-ORIGIN: SYMONEURAL-GENERATED)"
}

require ${THISDIR}/symoneural-safetensors-crates.inc
