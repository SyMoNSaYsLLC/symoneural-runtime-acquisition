# truststore for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (httpx2 truststore>=0.10; httpcore2 truststore>=0.10). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag v0.10.4 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/tls/source/truststore"

SUMMARY = "truststore for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/sethmlarson/truststore"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=74420fc3965c4558a4a1529e63c2867f"

SRC_URI = "git://github.com/sethmlarson/truststore;protocol=https;nobranch=1;branch=main"
PV = "0.10.4"
SRCREV = "0714f72a739d182cdb8502f4e1bb4cf7ebfe4eb5"

inherit python_flit_core
