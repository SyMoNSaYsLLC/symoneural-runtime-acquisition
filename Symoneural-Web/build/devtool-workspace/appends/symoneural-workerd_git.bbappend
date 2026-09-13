inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Web/src/runtime/source/workerd"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 909e388c86905a217391cb557ac3260f1daff3d0
