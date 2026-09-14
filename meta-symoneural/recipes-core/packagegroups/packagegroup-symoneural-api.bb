# The deployable API runtime surface: the six direct upstream Python packages and,
# through their RDEPENDS, the eleven runtime dependencies their wheels declare
# (tools/check-python-runtime-closures.py --runtime API must PASS for this group to
# mean anything). The estate python3 is listed by its metapackage so the stdlib
# modules the stack imports (json, logging, asyncio, ssl, sqlite3, ...) are present.
# No build frontend (maturin, hatchling, pdm, flit, setuptools) is in this group:
# a clean runtime must not need them (reconstruction v1.1 §68).
SUMMARY = "SyMoNeuRaL API runtime - first-party API + the 17-source Python closure"
LICENSE = "MIT"
inherit packagegroup

RDEPENDS:${PN} = " \
    symoneural-api \
    symoneural-api-util \
    symoneural-api-python \
    symoneural-fastapi \
    symoneural-starlette \
    symoneural-uvicorn \
    symoneural-pydantic \
    symoneural-httpx \
    symoneural-httpcore \
    python3 \
"
