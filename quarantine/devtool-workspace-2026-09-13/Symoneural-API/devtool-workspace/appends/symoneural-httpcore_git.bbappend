inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-API/src/http/source/httpcore"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 98209758cc14e1a5f966fe1dfdc1064b94055d8c
