inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Common/src/ml/source/transformers"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 856157a2f3e9594954310df18fdccc31ffddebe9
