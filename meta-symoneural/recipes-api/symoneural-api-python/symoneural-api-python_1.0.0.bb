# symoneural_api: the generic Python API (FastAPI service, application registry,
# demo policy, unit supervisor binding, ctypes binding to libsymoneural-api).
# First-party, built from HEAD:Symoneural-API/app by symoneural-firstparty.
#
# RDEPENDS follow pyproject [project].dependencies exactly as
# tools/check-python-runtime-closures.py --runtime API evaluates them; the
# native library is a runtime dependency because symoneural_api.native loads
# libsymoneural-api.so.1 (with a recorded Python fallback when absent).
SUMMARY = "SyMoNeuRaL API - generic control plane and application layer (Python)"
HOMEPAGE = "https://symoneural.com"
LICENSE = "CLOSED"

inherit symoneural-firstparty python_flit_core
SYMON_FP_PATH = "Symoneural-API/app"

RDEPENDS:${PN} += " \
    symoneural-fastapi \
    symoneural-pydantic \
    symoneural-uvicorn \
    symoneural-api \
    python3-ctypes \
    python3-json \
    python3-logging \
    python3-asyncio \
"
