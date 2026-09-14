# symoneural-llm - the estate-owned LLM runtime (reconstruction v1.1 §49-§56, L4):
# the recorded unit `chat` (HTTP, port 8802, SYM_CHAT_TOKEN, fail-closed) over
# libsymoneural-llm through ctypes, with the Anthropic Messages adapter as one
# consumer. First-party; built from the committed tree HEAD:Symoneural-LLM/app.
# The package has NO upstream Python dependency: the service is the stdlib HTTP
# server (pyproject dependencies = []), so its runtime closure is the stdlib split
# packages below plus the native library.
SUMMARY = "SyMoNeuRaL LLM runtime - the chat unit over libsymoneural-llm (Python)"
HOMEPAGE = "https://symoneural.com"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=f6737acf372c75a15aaeb6e6eca2c340"

inherit symoneural-firstparty python_flit_core
SYMON_FP_PATH = "Symoneural-LLM/app"

# stdlib modules the runtime imports, mapped through oe-core's python3-manifest.json:
#   http.server/hmac/uuid/base64 -> netclient; socketserver -> netserver;
#   hashlib -> crypt; socket -> io; ctypes; json; logging; the rest -> core
RDEPENDS:${PN} += " \
    symoneural-llm \
    python3-core \
    python3-ctypes \
    python3-json \
    python3-netclient \
    python3-netserver \
    python3-crypt \
    python3-io \
    python3-logging \
"
