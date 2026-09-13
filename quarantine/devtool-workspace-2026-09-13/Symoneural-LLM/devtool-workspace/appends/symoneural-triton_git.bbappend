inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-LLM/src/inference/source/triton"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: c01b6774b1865984607d89d89d3a10833de92037
