inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Common/src/ml/source/huggingface-hub"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 495b17c8529614759ae0f1ccf1ebe9a61c148b7c
