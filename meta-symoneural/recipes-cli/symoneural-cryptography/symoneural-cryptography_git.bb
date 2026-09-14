# cryptography (Rust + OpenSSL) for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (pyjwt[crypto] cryptography>=3.4.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag 50.0.1 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/auth/source/cryptography"

SUMMARY = "cryptography (Rust + OpenSSL) for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/pyca/cryptography"
LICENSE = "Apache-2.0 OR BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE;md5=8c3617db4fb6fae01f1d253ab91511e4 \
                    file://LICENSE.APACHE;md5=4e168cce331e5c827d4c2b68a6200e1b \
                    file://LICENSE.BSD;md5=5ae30ba4123bc4f2fa49aa0b0dce887b"

SRC_URI = "git://github.com/pyca/cryptography;protocol=https;nobranch=1;branch=main"
PV = "50.0.1"
SRCREV = "ffde75a2b594822c740a2e4748b56c00548302bf"

# Cargo workspace at the tree root (members: src/rust); the extension links the TARGET
# OpenSSL through openssl-sys/pkg-config, never a vendored copy. Build environment
# mirrors oe-core's python3-cryptography (borrowed as build knowledge, not as provider).
CARGO_MANIFEST_PATH = "${S}/src/rust/Cargo.toml"
CARGO_LOCK_SRC_DIR = "${S}"
inherit pkgconfig
DEPENDS += "openssl python3-cffi-native python3-setuptools-native"
LDSHARED += "-pthread"
export CRYPTOGRAPHY_BUILD_OPENSSL_NO_LEGACY = "1"
TARGET_CFLAGS:append = " -I${STAGING_INCDIR}/python${PYTHON_BASEVERSION}"
inherit python_maturin cargo-update-recipe-crates
DEPENDS += "python3-maturin-native"
# the Cargo closure is an acquisition: `bitbake -c update_crates symoneural-cryptography` writes it
require ${THISDIR}/symoneural-cryptography-crates.inc
INSANE_SKIP:${PN} = "already-stripped"
RDEPENDS:${PN} += "symoneural-cffi python3-numbers python3-threading"
