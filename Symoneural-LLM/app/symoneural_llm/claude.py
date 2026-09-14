"""Anthropic Messages protocol adapter — one consumer of the native inference API.

Translates POST /v1/messages (messages, system, stream, tools, tool_choice,
tool_result, sampling) into InferenceService calls and back. Prompt assembly is
a plain, documented transcript format; tool calls are emitted when the model
produces the tool-call marker, and tool_result blocks are folded back into the
transcript. The adapter is stateless per request except for the session it
opens/closes; nothing here reaches libllama directly and nothing here is used by
the product's own applications - they consume inference.py.

Tool-use CORRECTNESS is a separate acceptance gate (reconstruction §54): the
unit tests here exercise the protocol translation against the fake backend;
Claude Code conformance runs against a real model.
"""
from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any, Iterator

from .backend import GenerateParams
from .inference import InferenceService

TOOL_CALL = re.compile(r"<tool_call>(\{.*?\})</tool_call>", re.S)


class ProtocolError(ValueError):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


def _text_of(content: Any) -> str:
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        t = block.get("type")
        if t == "text":
            parts.append(block.get("text", ""))
        elif t == "tool_use":
            parts.append(f"<tool_call>{json.dumps({'name': block.get('name'), 'input': block.get('input', {})})}</tool_call>")
        elif t == "tool_result":
            body = block.get("content")
            body = body if isinstance(body, str) else "".join(b.get("text", "") for b in (body or []) if isinstance(b, dict))
            parts.append(f"<tool_result id={block.get('tool_use_id', '')!r}>{body}</tool_result>")
    return "".join(parts)


def build_prompt(req: dict) -> str:
    """Documented transcript format the model is prompted with."""
    out = []
    if req.get("system"):
        out.append(f"[system]\n{_text_of(req['system'])}\n")
    tools = req.get("tools") or []
    if tools:
        out.append("[tools]\n" + "\n".join(json.dumps({"name": t["name"], "description": t.get("description", ""), "input_schema": t.get("input_schema", {})}) for t in tools) + "\n")
        tc = req.get("tool_choice") or {"type": "auto"}
        out.append(f"[tool_choice] {json.dumps(tc)}\n")
    for m in req.get("messages", []):
        if m.get("role") not in ("user", "assistant"):
            raise ProtocolError(400, f"invalid role {m.get('role')!r}")
        out.append(f"[{m['role']}]\n{_text_of(m.get('content'))}\n")
    out.append("[assistant]\n")
    return "".join(out)


def parse_output(text: str) -> list[dict]:
    """Split model text into Anthropic content blocks: text and tool_use."""
    blocks, pos = [], 0
    for m in TOOL_CALL.finditer(text):
        if m.start() > pos and text[pos:m.start()].strip():
            blocks.append({"type": "text", "text": text[pos:m.start()]})
        try:
            call = json.loads(m.group(1))
        except json.JSONDecodeError:
            blocks.append({"type": "text", "text": m.group(0)}); pos = m.end(); continue
        blocks.append({"type": "tool_use", "id": "toolu_" + uuid.uuid4().hex[:24], "name": call.get("name", ""), "input": call.get("input", {})})
        pos = m.end()
    if text[pos:].strip() or not blocks:
        blocks.append({"type": "text", "text": text[pos:]})
    return blocks


class ClaudeAdapter:
    def __init__(self, svc: InferenceService, *, allowed_models: frozenset[str] | None = None) -> None:
        self.svc = svc
        self.allowed_models = allowed_models

    def _params(self, req: dict) -> GenerateParams:
        return GenerateParams(max_tokens=int(req.get("max_tokens", 256)), temperature=float(req.get("temperature", 0.7)),
                              top_p=float(req.get("top_p", 0.95)), stop=tuple(req.get("stop_sequences") or ()))

    def _validate(self, req: dict) -> str:
        model = req.get("model")
        if not model:
            raise ProtocolError(400, "model is required")
        if self.allowed_models is not None and model not in self.allowed_models:
            raise ProtocolError(403, f"model {model!r} not permitted for this application")
        if not isinstance(req.get("messages"), list) or not req["messages"]:
            raise ProtocolError(400, "messages must be a non-empty list")
        if "max_tokens" not in req:
            raise ProtocolError(400, "max_tokens is required")
        return model

    def messages(self, req: dict) -> dict:
        model = self._validate(req)
        s = self.svc.open_session(model)
        try:
            c = self.svc.generate(s.session_id, build_prompt(req), self._params(req))
        finally:
            self.svc.close_session(s.session_id)
        content = parse_output(c.text)
        stop = "tool_use" if any(b["type"] == "tool_use" for b in content) else {"end_turn": "end_turn", "max_tokens": "max_tokens", "stop_sequence": "stop_sequence", "cancelled": "end_turn"}[c.stop_reason]
        return {"id": "msg_" + uuid.uuid4().hex[:24], "type": "message", "role": "assistant", "model": model, "content": content,
                "stop_reason": stop, "stop_sequence": None, "usage": {"input_tokens": c.input_tokens, "output_tokens": c.output_tokens}}

    def messages_stream(self, req: dict) -> Iterator[str]:
        """Server-sent events in the Anthropic streaming shape."""
        model = self._validate(req)
        s = self.svc.open_session(model)
        def ev(name: str, data: dict) -> str:
            return f"event: {name}\ndata: {json.dumps(data)}\n\n"
        msg_id = "msg_" + uuid.uuid4().hex[:24]
        yield ev("message_start", {"type": "message_start", "message": {"id": msg_id, "type": "message", "role": "assistant", "model": model, "content": [], "stop_reason": None, "usage": {"input_tokens": 0, "output_tokens": 0}}})
        yield ev("content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}})
        try:
            for piece in self.svc.stream(s.session_id, build_prompt(req), self._params(req)):
                yield ev("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": piece}})
            sess = self.svc.session(s.session_id)
            stop = sess.last_stop
            yield ev("content_block_stop", {"type": "content_block_stop", "index": 0})
            yield ev("message_delta", {"type": "message_delta", "delta": {"stop_reason": stop, "stop_sequence": None}, "usage": {"output_tokens": sess.output_tokens}})
            yield ev("message_stop", {"type": "message_stop"})
        finally:
            self.svc.close_session(s.session_id)
