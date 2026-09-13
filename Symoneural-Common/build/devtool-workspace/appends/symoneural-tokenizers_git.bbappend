inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Common/src/ml/source/tokenizers"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 88a4498ad4ea1a9487b0a9b0ff881383fd5a06a3
