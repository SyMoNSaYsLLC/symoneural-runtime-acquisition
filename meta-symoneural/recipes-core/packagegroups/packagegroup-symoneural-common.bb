# The deployable Common runtime surface: the estate-wide Torch/Transformers foundation
# and, through their RDEPENDS, the runtime closure their wheels declare
# (tools/check-python-runtime-closures.py --runtime Common must PASS for this group to
# mean anything). The API packagegroup supplies the shared web stack that
# huggingface-hub reaches through httpx.
SUMMARY = "SyMoNeuRaL Common runtime - Torch + Transformers foundation"
LICENSE = "MIT"
inherit packagegroup

RDEPENDS:${PN} = " \
    symoneural-pytorch \
    symoneural-transformers \
    symoneural-huggingface-hub \
    symoneural-tokenizers \
    symoneural-safetensors \
    symoneural-numpy \
    packagegroup-symoneural-api \
"
