# jiter - fast iterable JSON parser (Rust extension) for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (anthropic-sdk-python jiter<1,>=0.4.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag v0.17.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/json/source/jiter"

SUMMARY = "jiter - fast iterable JSON parser (Rust extension) for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/pydantic/jiter"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=aa97bb3778992892e226b4504b83b60c"

SRC_URI = "git://github.com/pydantic/jiter;protocol=https;nobranch=1;branch=main"
PV = "0.17.0"
SRCREV = "2b5ec63e505b44775e29b865c3161ea13bdad16b"

# the Python distribution is one crate of the workspace; the lockfile is the workspace's
PEP517_SOURCE_PATH = "${S}/crates/jiter-python"
CARGO_MANIFEST_PATH = "${S}/crates/jiter-python/Cargo.toml"
CARGO_LOCK_SRC_DIR = "${S}"
inherit python_maturin cargo-update-recipe-crates
DEPENDS += "python3-maturin-native"
# the Cargo closure is an acquisition: `bitbake -c update_crates symoneural-jiter` writes it
require ${THISDIR}/symoneural-jiter-crates.inc
INSANE_SKIP:${PN} = "already-stripped"
