# PyYAML for the SyMoNeuRaL Common runtime
# A RUNTIME dependency of the Common wheels (huggingface-hub pyyaml>=5.1; transformers pyyaml>=5.1). Acquired 2026-09-14 under the
# estate rule "own what you ship": layer copies are build tooling at most, never the
# shipped provider. Tag 6.0.3 at the pin below; licence read from the tree.
# Built by symoneural-pristine from the committed tree object (HEAD:<source_path>).
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/data/source/pyyaml"

SUMMARY = "PyYAML for the SyMoNeuRaL Common runtime"
HOMEPAGE = "https://github.com/yaml/pyyaml"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=6d8242660a8371add5fe547adf083079"

SRC_URI = "git://github.com/yaml/pyyaml;protocol=https;nobranch=1;branch=main"
PV = "6.0.3"
SRCREV = "49790e73684bebad1df05ef8d828fa12f685bffb"

# PyYAML ships its OWN PEP 517 backend: pyproject.toml declares
#   build-backend = "_pyyaml_pep517"  with  backend-path = ["packaging"]
# so the backend module is inside the tree and python_pep517's default
# setuptools backend would be wrong. Cython >= 3.0 is required for Python >= 3.13
# and libyaml provides the C extension's runtime.
inherit python_pep517
PEP517_BUILD_API = "_pyyaml_pep517"
DEPENDS += "python3-setuptools-native symoneural-cython-native libyaml"
