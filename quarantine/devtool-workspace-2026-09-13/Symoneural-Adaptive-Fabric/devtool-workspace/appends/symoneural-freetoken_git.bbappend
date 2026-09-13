inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Adaptive-Fabric/src/freetoken/source/FreeToken"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 9db1a39455a3fb107f3db83e381d10ceadfe5d99
