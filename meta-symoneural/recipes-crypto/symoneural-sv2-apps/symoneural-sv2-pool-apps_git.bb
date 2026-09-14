# Stratum V2 pool-side applications: pool and jd-server from the pool-apps workspace of the
# pinned sv2-apps tree (same source as symoneural-sv2-apps, separate Cargo workspace and lock).
require symoneural-sv2-apps.inc
SUMMARY = "Stratum V2 pool-side applications (pool, jd-server) ${PV}"

inherit symoneural-pristine cargo cargo-update-recipe-crates
CARGO_SRC_DIR = "pool-apps"
CARGO_LOCK_SRC_DIR = "${S}/pool-apps"
require ${THISDIR}/${BPN}-crates.inc
