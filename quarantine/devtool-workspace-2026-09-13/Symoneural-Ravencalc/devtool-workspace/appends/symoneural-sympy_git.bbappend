inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Ravencalc/src/symbolic/source/sympy"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 16fa855354eb7bcabd3fe10993841e03b1382692
