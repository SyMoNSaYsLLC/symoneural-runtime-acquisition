inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Crypto/src/stratum/source/stratum"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: c1a7991394254c806f97a5feb4f4be771596ce69
