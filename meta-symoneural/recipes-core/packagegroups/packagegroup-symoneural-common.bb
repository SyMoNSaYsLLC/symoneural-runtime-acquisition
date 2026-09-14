# The deployable Common runtime surface: the estate-wide Torch/Transformers foundation
# and, through their RDEPENDS, the runtime closure their wheels declare
# (tools/check-python-runtime-closures.py --runtime Common must PASS for this group to
# mean anything). The API packagegroup supplies the shared web stack that
# huggingface-hub reaches through httpx.
# NOT in this group (2026-09-14): symoneural-accelerate. It builds and packages, and
# every one of its runtime edges is estate-owned, but on this torch (built
# USE_DISTRIBUTED=0) Accelerator.prepare() fails - accelerate/utils/other.py
# model_has_dtensor imports torch.distributed.tensor guarded only by torch VERSION,
# never by torch.distributed.is_available(). Shipping it would be a phantom
# completion. Evidence: docs/common/COMMON-CLOSURE.md. Decision pending: rebuild
# torch with USE_DISTRIBUTED=1 (upstream's Linux default; gloo CPU backend) or
# defer accelerate to the Phase 12 torch by recorded ruling.
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
