inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Common/src/ml/source/accelerate"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 6afc1e5ee217051fde702b23de2813344dc0fd33
