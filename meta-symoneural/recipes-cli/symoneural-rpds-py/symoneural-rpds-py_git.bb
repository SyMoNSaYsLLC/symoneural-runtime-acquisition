# rpds-py - persistent data structures (Rust extension) for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (jsonschema rpds-py>=0.25.0; referencing rpds-py>=0.7.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag v2026.6.3 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/json/source/rpds-py"

SUMMARY = "rpds-py - persistent data structures (Rust extension) for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/crate-py/rpds"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=7767fa537c4596c54141f32882c4a984"

SRC_URI = "git://github.com/crate-py/rpds;protocol=https;nobranch=1;branch=main"
PV = "2026.6.3"
SRCREV = "7277eb681f6efd67eca1bbaa32f78d78bdc044a5"

CARGO_MANIFEST_PATH = "${S}/Cargo.toml"
CARGO_LOCK_SRC_DIR = "${S}"
inherit python_maturin cargo-update-recipe-crates
DEPENDS += "python3-maturin-native"
# the Cargo closure is an acquisition: `bitbake -c update_crates symoneural-rpds-py` writes it
require ${THISDIR}/symoneural-rpds-py-crates.inc
INSANE_SKIP:${PN} = "already-stripped"
