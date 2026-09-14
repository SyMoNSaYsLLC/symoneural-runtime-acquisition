"""symoneural-llm — the estate-owned LLM runtime, run as the recorded unit `chat`.

The API registry (Symoneural-API/app/symoneural_api/units.py) records unit `chat`
as an HTTP service on port 8802, started by the supervisor with a fixed argv and
gated by the bearer token in SYM_CHAT_TOKEN. This module is that process:

  symoneural-llm serve   [--host 127.0.0.1] [--port 8802] [--registry-root DIR] ...
  symoneural-llm request --model ID --prompt TEXT [--max-tokens N] ...   (in-process, no socket)
  symoneural-llm capabilities [--registry-root DIR]

Boundaries: model ids come from the registry directory and the operator's
--allowed-models; a client names a model by id and can never supply a path or a
command. Protocol translation (Anthropic Messages) is claude.py; inference is
inference.py over backend.Backend; the native binding is native.py. No framework:
the stdlib HTTP server is the whole service surface.
"""
from __future__ import annotations

import argparse
import hmac
import json
import os
import signal
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from . import __version__
from .backend import Backend, FakeBackend
from .claude import ClaudeAdapter, ProtocolError
from .inference import InferenceService

UNIT = "chat"
TOKEN_ENV = "SYM_CHAT_TOKEN"
DEFAULT_PORT = 8802
DEFAULT_REGISTRY = "/var/lib/symoneural/models/llm"
EX_CONFIG = 78          # sysexits: the unit is unconfigured and must not come up serving


def _registry_root(arg: str | None) -> str:
    return arg or os.environ.get("SYM_LLM_REGISTRY_ROOT") or DEFAULT_REGISTRY


def make_backend(args: argparse.Namespace) -> Backend:
    if getattr(args, "fake", False):
        return FakeBackend()
    from .native import LlamaBackend
    return LlamaBackend(_registry_root(args.registry_root), n_threads=args.threads, n_ctx=args.n_ctx, seed=args.seed)


def make_adapter(backend: Backend, allowed: str | None) -> ClaudeAdapter:
    svc = InferenceService(backend)
    models = frozenset(m.strip() for m in allowed.split(",") if m.strip()) if allowed else None
    return ClaudeAdapter(svc, allowed_models=models)


def service_capabilities(adapter: ClaudeAdapter, backend: Backend) -> dict[str, Any]:
    caps = adapter.svc.capabilities()
    caps.update({"unit": UNIT, "runtime": "symoneural-llm", "version": __version__,
                 "protocols": ["anthropic-messages/2023-06-01"],
                 "allowed_models": sorted(adapter.allowed_models) if adapter.allowed_models is not None else None})
    n = getattr(backend, "_n", None)
    if n is not None:
        caps["native"] = {"library": "libsymoneural-llm", "version": n.version(), "abi": n.abi_version,
                          "capabilities": n.capabilities()}
    return caps


def _error(status: int, kind: str, message: str) -> tuple[int, dict]:
    return status, {"type": "error", "error": {"type": kind, "message": message}}


class Handler(BaseHTTPRequestHandler):
    server_version = f"symoneural-llm/{__version__}"
    adapter: ClaudeAdapter
    backend: Backend
    token: str

    def log_message(self, fmt: str, *args: Any) -> None:   # no request bodies, no tokens, no paths
        sys.stderr.write("symoneural-llm: %s %s\n" % (self.command, self.path.split("?")[0]))

    def _json(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(data)

    def _authorised(self) -> bool:
        auth = self.headers.get("Authorization", "")
        presented = auth.removeprefix("Bearer ").strip() if auth.startswith("Bearer ") else ""
        return bool(presented) and hmac.compare_digest(presented.encode(), self.token.encode())

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path == "/api/health":                       # the supervisor's probe; unauthenticated like the API's own
            return self._json(200, {"status": "ready", "unit": UNIT, "runtime": "symoneural-llm", "version": __version__})
        if not self._authorised():
            return self._json(*_error(401, "authentication_error", "bearer token required"))
        if path == "/v1/capabilities":
            return self._json(200, service_capabilities(self.adapter, self.backend))
        if path == "/v1/models":
            models = [{"id": m.model_id, "type": "model", "context_length": m.context_length,
                       "capabilities": sorted(m.capabilities)} for m in self.adapter.svc.models()
                      if self.adapter.allowed_models is None or m.model_id in self.adapter.allowed_models]
            return self._json(200, {"data": models})
        return self._json(*_error(404, "not_found_error", "no such route"))

    def do_POST(self) -> None:
        path = self.path.split("?")[0]
        if not self._authorised():
            return self._json(*_error(401, "authentication_error", "bearer token required"))
        if path != "/v1/messages":
            return self._json(*_error(404, "not_found_error", "no such route"))
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n <= 0 or n > 4 << 20:
                return self._json(*_error(413, "invalid_request_error", "body length"))
            req = json.loads(self.rfile.read(n))
            if not isinstance(req, dict):
                raise ValueError("body must be an object")
        except (ValueError, json.JSONDecodeError) as e:
            return self._json(*_error(400, "invalid_request_error", str(e)))
        try:
            if req.get("stream"):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()
                for event in self.adapter.messages_stream(req):
                    self.wfile.write(event.encode()); self.wfile.flush()
                return
            return self._json(200, self.adapter.messages(req))
        except ProtocolError as e:
            return self._json(*_error(e.status, "invalid_request_error" if e.status == 400 else "permission_error", str(e)))
        except KeyError as e:
            return self._json(*_error(404, "not_found_error", f"unknown model {e}"))
        except Exception as e:   # native/backend failure: status text only, never a path
            return self._json(*_error(502, "api_error", type(e).__name__ + ": " + getattr(e, "strerror", "backend failure")))


def serve(args: argparse.Namespace) -> int:
    token = os.environ.get(TOKEN_ENV)
    if not token:
        sys.stderr.write(f"symoneural-llm: unconfigured: {TOKEN_ENV} is not provisioned; refusing to serve\n")
        return EX_CONFIG
    backend = make_backend(args)
    adapter = make_adapter(backend, args.allowed_models)
    handler = type("BoundHandler", (Handler,), {"adapter": adapter, "backend": backend, "token": token})
    httpd = ThreadingHTTPServer((args.host, args.port), handler)
    httpd.daemon_threads = True
    stop = threading.Event()

    def on_term(_sig, _frm):
        stop.set(); threading.Thread(target=httpd.shutdown, daemon=True).start()
    signal.signal(signal.SIGTERM, on_term); signal.signal(signal.SIGINT, on_term)
    sys.stderr.write(f"symoneural-llm {__version__}: unit {UNIT} listening on {args.host}:{args.port}\n")
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
        close = getattr(backend, "close", None)
        if close: close()
    return 0


def request(args: argparse.Namespace) -> int:
    """One request through the same adapter, in-process: the proof path."""
    backend = make_backend(args)
    adapter = make_adapter(backend, args.allowed_models)
    try:
        if args.file:
            with open(args.file, encoding="utf-8") as f:
                req = json.load(f)
        else:
            req = {"model": args.model, "max_tokens": args.max_tokens, "temperature": args.temperature,
                   "messages": [{"role": "user", "content": args.prompt}]}
        try:
            out = adapter.messages(req)
        except ProtocolError as e:
            print(json.dumps(_error(e.status, "invalid_request_error", str(e))[1])); return 1
        except KeyError as e:
            print(json.dumps(_error(404, "not_found_error", f"unknown model {e}")[1])); return 1
        except Exception as e:   # native/backend failure: type and status text only, never a path
            print(json.dumps(_error(502, "api_error", type(e).__name__ + ": " + getattr(e, "strerror", str(e)))[1])); return 1
        print(json.dumps(out))
        return 0
    finally:
        close = getattr(backend, "close", None)
        if close: close()


def capabilities(args: argparse.Namespace) -> int:
    backend = make_backend(args)
    try:
        print(json.dumps(service_capabilities(make_adapter(backend, args.allowed_models), backend)))
        return 0
    finally:
        close = getattr(backend, "close", None)
        if close: close()


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="symoneural-llm", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    def common(p):
        p.add_argument("--registry-root", default=None, help="directory of <id>.gguf (default: $SYM_LLM_REGISTRY_ROOT or %s)" % DEFAULT_REGISTRY)
        p.add_argument("--allowed-models", default=os.environ.get("SYM_LLM_ALLOWED_MODELS"), help="comma-separated ids clients may name")
        p.add_argument("--threads", type=int, default=0); p.add_argument("--n-ctx", type=int, default=4096)
        p.add_argument("--seed", type=int, default=0)
        p.add_argument("--fake", action="store_true", help="FakeBackend (tests only; no native library)")
    s = sub.add_parser("serve"); common(s)
    s.add_argument("--host", default="127.0.0.1"); s.add_argument("--port", type=int, default=DEFAULT_PORT)
    s.set_defaults(fn=serve)
    r = sub.add_parser("request"); common(r)
    r.add_argument("--model"); r.add_argument("--prompt"); r.add_argument("--file")
    r.add_argument("--max-tokens", type=int, default=64); r.add_argument("--temperature", type=float, default=0.0)
    r.set_defaults(fn=request)
    c = sub.add_parser("capabilities"); common(c); c.set_defaults(fn=capabilities)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "request" and not args.file and not (args.model and args.prompt):
        build_parser().error("request needs --model and --prompt, or --file")
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
