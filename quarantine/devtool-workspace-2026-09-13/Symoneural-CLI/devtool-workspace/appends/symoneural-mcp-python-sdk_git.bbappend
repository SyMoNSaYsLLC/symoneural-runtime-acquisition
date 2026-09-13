inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-CLI/src/mcp/source/python-sdk"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 9972c21aa42054fb1450c5fc614761ed11847ec6
