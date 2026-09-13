inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-CLI/src/anthropic/source/anthropic-sdk-python"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: eb21a4352015686c30f5759e8c2f02d70f5371e2
