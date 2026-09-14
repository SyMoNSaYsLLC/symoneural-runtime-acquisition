# The deployable LLM runtime surface: the native ABI library, its operator utility, and
# the Python runtime that is the recorded unit `chat`. libllama and libggml arrive
# through symoneural-llm's shared-library dependencies (they are debian-renamed
# packages - libllama0 - which an allarch packagegroup must not name directly).
# Models are EXTERNAL: nothing here installs weights; the runtime reads
# <registry_root>/<id>.gguf at run time.
SUMMARY = "SyMoNeuRaL LLM runtime - libsymoneural-llm + symoneural-llm (chat unit)"
LICENSE = "MIT"
inherit packagegroup

RDEPENDS:${PN} = " \
    symoneural-llm \
    symoneural-llm-util \
    symoneural-llm-python \
"
