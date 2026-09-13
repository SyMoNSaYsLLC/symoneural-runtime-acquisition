inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Crypto/src/stratum/source/sv2-spec"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 67d2178e12b2c3da948f656b0e1030afafb8d891
