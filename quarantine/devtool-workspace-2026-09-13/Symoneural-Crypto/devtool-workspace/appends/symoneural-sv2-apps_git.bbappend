inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Crypto/src/stratum/source/sv2-apps"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: d7d556d1a3c7e1c26dfccd076b491a38c038a5e0
