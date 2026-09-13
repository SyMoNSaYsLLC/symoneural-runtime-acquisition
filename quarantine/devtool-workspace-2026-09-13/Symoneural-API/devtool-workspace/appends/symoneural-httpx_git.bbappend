inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-API/src/http/source/httpx"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 26d48e0634e6ee9cdc0533996db289ce4b430177
