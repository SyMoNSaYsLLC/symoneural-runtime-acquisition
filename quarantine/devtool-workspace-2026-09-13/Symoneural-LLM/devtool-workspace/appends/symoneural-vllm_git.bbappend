inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-LLM/src/inference/source/vllm"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 98dff2a81d747d1dba01a47f939f48c3526d4206
