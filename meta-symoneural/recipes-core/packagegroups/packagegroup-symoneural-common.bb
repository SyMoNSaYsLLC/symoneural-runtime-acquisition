# The deployable Common runtime surface: the estate-wide Torch/Transformers foundation
# and, through their RDEPENDS, the runtime closure their wheels declare
# (tools/check-python-runtime-closures.py --runtime Common must PASS for this group to
# mean anything). The API packagegroup supplies the shared web stack that
# huggingface-hub reaches through httpx.
# symoneural-accelerate rejoins the group for the P7 C7 proof (2026-09-14). It was
# DEFERRED BY RECORDED RULING against the USE_DISTRIBUTED=0 torch because
# Accelerator.prepare() imports torch.distributed.tensor (accelerate/utils/other.py
# model_has_dtensor, guarded by torch VERSION only). The C7 torch is built
# USE_DISTRIBUTED=1 + Gloo; the Common clean-root proof now runs prepare() plus one
# SGD epoch (CPU mode and S2/GPU mode) and the ruling unresolved.json:accelerate-torch-
# distributed is promoted ONLY if that path actually succeeds - not because it imports.
SUMMARY = "SyMoNeuRaL Common runtime - Torch + Transformers foundation"
LICENSE = "MIT"
inherit packagegroup

RDEPENDS:${PN} = " \
    symoneural-pytorch \
    symoneural-accelerate \
    symoneural-transformers \
    symoneural-huggingface-hub \
    symoneural-tokenizers \
    symoneural-safetensors \
    symoneural-numpy \
    packagegroup-symoneural-api \
"
