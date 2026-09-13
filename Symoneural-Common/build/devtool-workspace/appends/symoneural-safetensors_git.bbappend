inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Common/src/ml/source/safetensors"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: a406ca3e7a90598be0cd05a50069cb9bf5ef6ba6
