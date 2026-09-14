# The deployable CLI runtime surface: the two direct upstream Python packages
# (anthropic-sdk-python, mcp) and, through their RDEPENDS, the runtime closure their
# wheels declare (tools/check-python-runtime-closures.py --runtime CLI must PASS for
# this group to mean anything). The API packagegroup supplies the shared web stack.
SUMMARY = "SyMoNeuRaL CLI runtime - anthropic + mcp Python closure"
LICENSE = "MIT"
inherit packagegroup

RDEPENDS:${PN} = " \
    symoneural-anthropic-sdk-python \
    symoneural-mcp-python-sdk \
    packagegroup-symoneural-api \
"
