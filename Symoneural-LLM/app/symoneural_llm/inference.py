"""The SyMoNeuRaL-native inference API. Applications consume THIS; protocol
adapters (Anthropic Messages, later OpenAI) translate to and from it. It owns:
model registry view, sessions, generation with streaming callback, cancellation,
token accounting and capability reporting. It never speaks a third party's wire
format and never takes a filesystem path from a client (models are named by id;
the register maps ids to files).
"""
from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, Iterator

from .backend import Backend, Cancelled, GenerateParams, ModelInfo


@dataclass(slots=True)
class Session:
    session_id: str
    model_id: str
    created: float = field(default_factory=time.time)
    cancel: threading.Event = field(default_factory=threading.Event)
    input_tokens: int = 0
    output_tokens: int = 0
    turns: int = 0
    last_stop: str = "end_turn"      # "end_turn" | "max_tokens" | "stop_sequence"


@dataclass(frozen=True, slots=True)
class Completion:
    session_id: str
    model_id: str
    text: str
    stop_reason: str                 # "end_turn" | "max_tokens" | "stop_sequence" | "cancelled"
    input_tokens: int
    output_tokens: int


class InferenceService:
    def __init__(self, backend: Backend) -> None:
        self._b = backend
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

    # -- capabilities / models ------------------------------------------------
    def capabilities(self) -> dict:
        return {"api": "symoneural-inference/1", "streaming": True, "cancellation": True,
                "models": [{"model_id": m.model_id, "context_length": m.context_length, "capabilities": sorted(m.capabilities)} for m in self._b.models()]}

    def models(self) -> list[ModelInfo]:
        return self._b.models()

    def model(self, model_id: str) -> ModelInfo:
        for m in self._b.models():
            if m.model_id == model_id:
                return m
        raise KeyError(f"unknown model {model_id!r}")

    # -- sessions --------------------------------------------------------------
    def open_session(self, model_id: str) -> Session:
        self.model(model_id)
        self._b.load(model_id)
        s = Session(session_id=uuid.uuid4().hex, model_id=model_id)
        with self._lock:
            self._sessions[s.session_id] = s
        return s

    def session(self, session_id: str) -> Session:
        try:
            return self._sessions[session_id]
        except KeyError:
            raise KeyError(f"unknown session {session_id!r}") from None

    def close_session(self, session_id: str) -> None:
        with self._lock:
            s = self._sessions.pop(session_id, None)
        if s is not None:
            s.cancel.set()

    def cancel(self, session_id: str) -> None:
        self.session(session_id).cancel.set()

    # -- generation ------------------------------------------------------------
    def stream(self, session_id: str, prompt: str, params: GenerateParams | None = None,
               on_token: Callable[[str], None] | None = None) -> Iterator[str]:
        """Yield text pieces; enforce max_tokens and stop sequences here, once."""
        s = self.session(session_id)
        params = params or GenerateParams()
        s.cancel.clear()
        s.input_tokens += len(self._b.tokenize(s.model_id, prompt))
        s.turns += 1
        produced, buf = 0, ""
        for piece in self._b.generate(s.model_id, prompt, params, s.cancel):
            buf += piece
            for stop in params.stop:
                if stop and stop in buf:
                    head = buf[: buf.index(stop)]
                    if head:
                        s.output_tokens += 1
                        if on_token: on_token(head)
                        yield head
                    s.last_stop = "stop_sequence"
                    return
            produced += 1
            s.output_tokens += 1
            if on_token: on_token(piece)
            yield piece
            buf = ""
            if produced >= params.max_tokens:
                s.last_stop = "max_tokens"
                return
        s.last_stop = "end_turn"

    def generate(self, session_id: str, prompt: str, params: GenerateParams | None = None) -> Completion:
        s = self.session(session_id)
        pieces: list[str] = []
        try:
            for p in self.stream(session_id, prompt, params):
                pieces.append(p)
            stop = s.last_stop
        except Cancelled:
            stop = "cancelled"
        return Completion(session_id, s.model_id, "".join(pieces), stop, s.input_tokens, s.output_tokens)
