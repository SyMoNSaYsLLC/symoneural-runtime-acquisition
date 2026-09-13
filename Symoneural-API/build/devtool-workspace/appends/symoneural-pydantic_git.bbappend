inherit externalsrc
EXTERNALSRC = "/home/google/SymonSaysLLC/Symoneural-API/src/model/source/pydantic"
# Out-of-tree build. EXTERNALSRC_BUILD previously pointed at the source tree,
# making B == S: every build wrote objects and generated files into pristine
# acquired source. ${WORKDIR}/build keeps B != S.
EXTERNALSRC_BUILD = "${WORKDIR}/build"

# initial_rev .: 001dea020e0809844e5b17666432c9135a976f46
