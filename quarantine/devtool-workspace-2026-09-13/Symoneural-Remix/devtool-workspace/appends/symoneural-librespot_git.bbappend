inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Remix/src/librespot/source/librespot"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: d36f9f1907e8cc9d68a93f8ebc6b627b1bf7267d
