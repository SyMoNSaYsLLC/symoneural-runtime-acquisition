# Stratum V2 miner-side applications: translator (SV1 -> SV2 proxy) and jd-client (job declarator
# client) from the miner-apps workspace of the pinned sv2-apps tree.
require symoneural-sv2-apps.inc
# restated for tools/scan-acquisition.py, which pairs a tree with its recipe from the .bb text
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Crypto/src/stratum/source/sv2-apps"
SRCREV = "d7d556d1a3c7e1c26dfccd076b491a38c038a5e0"
PV = "0.7.0"
LICENSE = "Apache-2.0 AND MIT"

inherit symoneural-pristine cargo cargo-update-recipe-crates
CARGO_SRC_DIR = "miner-apps"
CARGO_LOCK_SRC_DIR = "${S}/miner-apps"
require ${THISDIR}/${BPN}-crates.inc
