# hf-xet (Xet storage client, Rust) for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (huggingface-hub hf-xet<2.0.0,>=1.5.2). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag v1.6.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/ml/source/hf-xet"

SUMMARY = "hf-xet (Xet storage client, Rust) for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/huggingface/xet-core"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=86d3f3a95c324c9479bd8986968f4327"

SRC_URI = "git://github.com/huggingface/xet-core;protocol=https;nobranch=1;branch=main"
PV = "1.6.0"
SRCREV = "de71453d952bd8b806edaa997c72313051a49050"

# xet-core is a Rust monorepo; the Python distribution hf-xet is the hf_xet/
# subdirectory. hf_xet is NOT a member of the root [workspace] (members are
# xet_runtime, xet_core_structures, xet_client, xet_data, xet_pkg, git_xet), so its
# own Cargo.lock is the lockfile, not the root one.
PEP517_SOURCE_PATH = "${S}/hf_xet"
CARGO_MANIFEST_PATH = "${S}/hf_xet/Cargo.toml"
CARGO_LOCK_SRC_DIR = "${S}/hf_xet"
inherit python_maturin cargo-update-recipe-crates
DEPENDS += "python3-maturin-native"
# the Cargo closure is an acquisition: `bitbake -c update_crates symoneural-hf-xet` writes it
require ${THISDIR}/symoneural-hf-xet-crates.inc
INSANE_SKIP:${PN} = "already-stripped"
