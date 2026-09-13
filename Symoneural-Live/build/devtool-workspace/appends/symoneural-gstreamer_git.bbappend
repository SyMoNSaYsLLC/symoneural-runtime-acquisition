inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-Live/src/gstreamer/source/gstreamer"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 070125524a8422e29d3b69a372ed4f62fd343ffa

# initial_rev subprojects/gst-integration-testsuites/medias: 8850d668e87752c863b3fb01954464b0d1fffe4c
