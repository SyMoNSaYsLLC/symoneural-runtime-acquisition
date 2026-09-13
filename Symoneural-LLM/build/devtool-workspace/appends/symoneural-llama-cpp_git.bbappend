inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-LLM/src/inference/source/llama.cpp"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 5266f24da75dc449bd56cbed7addb9c8e4a6a73e
