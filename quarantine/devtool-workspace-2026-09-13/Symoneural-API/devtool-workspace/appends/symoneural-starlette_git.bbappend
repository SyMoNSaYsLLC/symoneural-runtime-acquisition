inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-API/src/web/source/starlette"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 4f250d6b814587e20c5365f0a5f0c4d42bcb929f
