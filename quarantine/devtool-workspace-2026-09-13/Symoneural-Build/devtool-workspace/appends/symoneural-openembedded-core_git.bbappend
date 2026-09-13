inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Build/src/devtools/source/openembedded-core"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 2814f0962f56c8d1afa4de76d2895ba9b5cb767d
