# The deployable Diffuse runtime surface: the image engine and nothing else.
#
# sd-cli and libstable-diffusion.so arrive as one package; the CUDA backend is compiled
# STATIC inside that library (unlike LLM, where symoneural-ggml-cuda is a dlopen'ed
# module and therefore an explicit row here). The S2 boundary - the host driver's
# libcuda.so.1 - is carried on libstable-diffusion.so itself, which symon_cuda_qa_s2
# verified at package time.
#
# NOT in this group, deliberately:
#   symoneural-stable-diffusion-cpp-server  sd-server is built because upstream's
#       examples/CMakeLists.txt adds it unconditionally, not because the estate wants a
#       second HTTP listener in a runtime image. The estate's HTTP surface is the
#       FastAPI gateway.
#   weights  Models are EXTERNAL. Nothing here installs a .gguf or a .safetensors; the
#       unit reads ${SYMON_MODELS_DIR}/image/* at run time (acquisition/model-register.json).
SUMMARY = "SyMoNeuRaL Diffuse runtime - stable-diffusion.cpp (image, sigils units)"
LICENSE = "MIT"
inherit packagegroup

RDEPENDS:${PN} = " \
    symoneural-stable-diffusion-cpp \
"
