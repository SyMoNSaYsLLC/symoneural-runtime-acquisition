inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-API/src/web/source/uvicorn"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 8988c23704fc373c9206cca53ec57dd8ad7f44a5
