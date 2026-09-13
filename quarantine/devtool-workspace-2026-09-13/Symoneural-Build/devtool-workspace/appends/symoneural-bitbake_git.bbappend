inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Build/src/bitbake/source"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 0880963fea4d91a034e4a6e007d23f98658ab986
