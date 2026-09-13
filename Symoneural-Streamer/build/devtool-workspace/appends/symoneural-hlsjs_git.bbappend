inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Streamer/src/hls/source/hls.js"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: e5ff3583965e3af16c4a4b4d2b5f7bd1ffb5b7de
