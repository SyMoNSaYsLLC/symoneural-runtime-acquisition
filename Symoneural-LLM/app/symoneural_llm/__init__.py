"""SyMoNeuRaL LLM — the Python side of native inference.

  inference.py   the SyMoNeuRaL-native inference API applications consume:
                 models, sessions, generate, stream, cancel, capabilities
  backend.py     the Backend protocol + FakeBackend (tests) ; the libsymoneural-llm
                 ctypes backend lands with L3/L4
  claude.py      the Anthropic Messages protocol ADAPTER over inference.py
                 (POST /v1/messages) - one consumer, not the product's model
"""
__version__ = "0.1.0"
__all__ = ["inference", "backend", "claude"]
