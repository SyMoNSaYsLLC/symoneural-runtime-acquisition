# httpx2 for the SyMoNeuRaL CLI runtime
# A RUNTIME dependency of the CLI wheels (anthropic-sdk-python httpx2<3,>=2.0.0; mcp httpx2>=2.5.0). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never
# the shipped provider. Tag v2.12.0 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-CLI/src/http/source/httpx2"

SUMMARY = "httpx2 for the SyMoNeuRaL CLI runtime"
HOMEPAGE = "https://github.com/pydantic/httpx2"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.md;md5=166cfc32dc0986f87a7e950553b52e5e"

SRC_URI = "git://github.com/pydantic/httpx2;protocol=https;nobranch=1;branch=main"
PV = "2.12.0"
SRCREV = "71ae23be5448f859c2b4e21d9972ddfa7b8d759d"

# uv workspace: src/httpx2 and src/httpcore2 are two distributions of this one tree.
# Runtime dependencies are rendered by the uv-dynamic-versioning metadata hook from the
# bypassed version (UV_DYNAMIC_VERSIONING_BYPASS = PV, exported by symoneural-pristine):
# truststore>=0.10, httpcore2==PV, anyio>=4.10, idna>=3.18.
PEP517_SOURCE_PATH = "${S}/src/httpx2"
inherit python_hatchling
DEPENDS += "python3-hatch-fancy-pypi-readme-native python3-uv-dynamic-versioning-native python3-jinja2-native python3-tomlkit-native python3-dunamai-native"
RDEPENDS:${PN} += "symoneural-httpcore2 symoneural-truststore symoneural-anyio symoneural-idna"
