# pydantic-core 2.46.5 - the Rust validation core pydantic 2.13.5 requires EXACTLY
# (Requires-Dist: pydantic-core==2.46.5). Its canonical source is the pydantic
# monorepo, subdirectory pydantic-core/, at the SAME commit as symoneural-pydantic:
# tag core-v2.46.5 == tag v2.13.5 == 7bba8aca5475. github.com/pydantic/pydantic-core
# stops at v2.41.5 and cannot supply this version; meta-python's 2.46.4 does not
# satisfy the pin. So this recipe builds from the tree the estate already owns -
# one source authority, two wheels (ruling: unresolved.json pydantic-core-ownership).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-API/src/model/source/pydantic"

SUMMARY = "pydantic-core - Rust validation/serialisation core for pydantic"
HOMEPAGE = "https://github.com/pydantic/pydantic"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://pydantic-core/LICENSE;md5=ab599c188b4a314d2856b3a55030c75c"

SRC_URI = "git://github.com/pydantic/pydantic;protocol=https;nobranch=1;branch=main"
PV = "2.46.5"
SRCREV = "001dea020e0809844e5b17666432c9135a976f46"

# the wheel lives in a subdirectory of the export; cargo's lockfile is upstream's
PEP517_SOURCE_PATH = "${S}/pydantic-core"
CARGO_MANIFEST_PATH = "${S}/pydantic-core/Cargo.toml"
CARGO_LOCK_SRC_DIR = "${S}/pydantic-core"
inherit python_maturin cargo-update-recipe-crates
DEPENDS += "python3-maturin-native"
require ${THISDIR}/symoneural-pydantic-core-crates.inc

# Runtime edge from pydantic-core's own pyproject dependencies
RDEPENDS:${PN} += "symoneural-typing-extensions"

# maturin strips the extension itself
INSANE_SKIP:${PN} = "already-stripped"
