"""SyMoNeuRaL LLM — the Python side of native inference.

  inference.py   the SyMoNeuRaL-native inference API applications consume:
                 models, sessions, generate, stream, cancel, capabilities
  backend.py     the Backend protocol + FakeBackend (tests)
  native.py      ctypes binding to libsymoneural-llm: LlamaBackend (the target backend)
  claude.py      the Anthropic Messages protocol ADAPTER over inference.py
                 (POST /v1/messages) - one consumer, not the product's model
  main.py        the `symoneural-llm` entrypoint: unit `chat` HTTP service (port 8802,
                 SYM_CHAT_TOKEN, fail-closed), and an in-process `request` proof path
"""
__version__ = "1.0.0"
__all__ = ["inference", "backend", "native", "claude", "main"]
