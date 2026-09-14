# opentelemetry-api for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (mcp opentelemetry-api>=1.28.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag v1.44.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/telemetry/source/opentelemetry-python"

SUMMARY = "opentelemetry-api for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/open-telemetry/opentelemetry-python"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=86d3f3a95c324c9479bd8986968f4327"

SRC_URI = "git://github.com/open-telemetry/opentelemetry-python;protocol=https;nobranch=1;branch=main"
PV = "1.44.0"
SRCREV = "53a5a40c9604583c501bcf13970a635f00e62df4"

# one distribution of the opentelemetry-python monorepo
PEP517_SOURCE_PATH = "${S}/opentelemetry-api"
inherit python_hatchling
RDEPENDS:${PN} += "symoneural-typing-extensions"
