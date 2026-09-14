# RavenCalc runtime surface: the numerics stack a clean target needs for
# `import numpy, scipy, sklearn, sympy, mpmath` plus the API runtime the service
# runs on (symoneural-fastapi/uvicorn/pydantic through packagegroup-symoneural-api).
SUMMARY = "SyMoNeuRaL RavenCalc runtime"
LICENSE = "MIT"
inherit packagegroup

RDEPENDS:${PN} = " \
    symoneural-numpy \
    symoneural-scipy \
    symoneural-scikit-learn \
    symoneural-sympy \
    symoneural-mpmath \
    packagegroup-symoneural-api \
"
