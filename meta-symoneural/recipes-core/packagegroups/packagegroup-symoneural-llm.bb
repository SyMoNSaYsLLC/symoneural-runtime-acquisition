# The deployable LLM runtime surface: the native ABI library, its operator utility, and
# the Python runtime that is the recorded unit `chat`. libllama and libggml arrive
# through symoneural-llm's shared-library dependencies (they are debian-renamed
# packages - libllama0 - which an allarch packagegroup must not name directly).
# Models are EXTERNAL: nothing here installs weights; the runtime reads
# <registry_root>/<id>.gguf at run time.
SUMMARY = "SyMoNeuRaL LLM runtime - libsymoneural-llm + symoneural-llm (chat unit)"
LICENSE = "MIT"
inherit packagegroup

# symoneural-ggml-cuda is the dlopen'ed CUDA backend module (P7 C6). It is an
# explicit row because the image sets NO_RECOMMENDATIONS and the deploy manifest is
# the install record; it carries the S2 boundary (the host driver's libcuda.so.1) and
# cuda-toolkit-bin. The CPU composition is this group without that row.
RDEPENDS:${PN} = " \
    symoneural-llm \
    symoneural-llm-util \
    symoneural-llm-python \
    symoneural-ggml-cuda \
"
