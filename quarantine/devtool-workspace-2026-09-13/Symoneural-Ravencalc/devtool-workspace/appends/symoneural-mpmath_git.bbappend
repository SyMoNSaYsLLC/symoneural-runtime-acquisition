inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/symbolic/source/mpmath"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: c1131e2d64abcbb57728ca8a499c920c0c69e67f
