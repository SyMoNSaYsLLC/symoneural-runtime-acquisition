"""Backend protocol: what libsymoneural-llm exposes, expressed for Python.

Every backend yields TOKENS as text pieces through a generator so streaming,
cancellation and accounting are handled once, in inference.py, regardless of
the engine behind it. The fake backend exists so the router and adapters are
testable before libllama is packaged; it is not an inference engine.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Iterator, Protocol


@dataclass(frozen=True, slots=True)
class ModelInfo:
    model_id: str
    context_length: int
    capabilities: frozenset[str] = frozenset({"text"})   # "text" | "tools" | "vision"


@dataclass(slots=True)
class GenerateParams:
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.95
    stop: tuple[str, ...] = ()


class Cancelled(Exception):
    pass


class Backend(Protocol):
    def models(self) -> list[ModelInfo]: ...
    def load(self, model_id: str) -> None: ...
    def unload(self, model_id: str) -> None: ...
    def tokenize(self, model_id: str, text: str) -> list[int]: ...
    def generate(self, model_id: str, prompt: str, params: GenerateParams, cancel: threading.Event) -> Iterator[str]: ...


class FakeBackend:
    """Deterministic stand-in: echoes a tokenised transform of the prompt so tests
    can assert streaming order, stop sequences, max_tokens and cancellation."""

    def __init__(self, models: tuple[ModelInfo, ...] = (ModelInfo("fake-1", 4096, frozenset({"text", "tools"})),)) -> None:
        self._models = {m.model_id: m for m in models}
        self.loaded: set[str] = set()
        self.calls: list[str] = []

    def models(self) -> list[ModelInfo]:
        return list(self._models.values())

    def load(self, model_id: str) -> None:
        if model_id not in self._models:
            raise KeyError(model_id)
        self.loaded.add(model_id); self.calls.append(f"load:{model_id}")

    def unload(self, model_id: str) -> None:
        self.loaded.discard(model_id); self.calls.append(f"unload:{model_id}")

    def tokenize(self, model_id: str, text: str) -> list[int]:
        return [len(w) for w in text.split()]

    def generate(self, model_id: str, prompt: str, params: GenerateParams, cancel: threading.Event) -> Iterator[str]:
        if model_id not in self.loaded:
            raise RuntimeError(f"{model_id} not loaded")
        words = prompt.split()[-8:] or ["(empty)"]
        for i, w in enumerate(words):
            if cancel.is_set():
                raise Cancelled()
            yield ("" if i == 0 else " ") + w[::-1]
