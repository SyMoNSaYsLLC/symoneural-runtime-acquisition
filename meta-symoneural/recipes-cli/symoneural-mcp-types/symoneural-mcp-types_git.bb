# mcp-types - the MCP protocol types distribution of the python-sdk monorepo
# A RUNTIME dependency of the CLI wheels (mcp mcp-types==2.2.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag v2.2.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/mcp/source/python-sdk"

SUMMARY = "mcp-types - the MCP protocol types distribution of the python-sdk monorepo"
HOMEPAGE = "https://github.com/modelcontextprotocol/python-sdk"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=7ae711d8a91d3871696f50e34ad3c2d7"

SRC_URI = "git://github.com/modelcontextprotocol/python-sdk;protocol=https;nobranch=1;branch=main"
PV = "2.2.0"
SRCREV = "9972c21aa42054fb1450c5fc614761ed11847ec6"

# one distribution of the python-sdk tree (the other is symoneural-mcp-python-sdk)
PEP517_SOURCE_PATH = "${S}/src/mcp-types"
inherit python_hatchling
DEPENDS += "python3-uv-dynamic-versioning-native python3-jinja2-native python3-tomlkit-native python3-dunamai-native"
RDEPENDS:${PN} += "symoneural-pydantic symoneural-typing-extensions"
