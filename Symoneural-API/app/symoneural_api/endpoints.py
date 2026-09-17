"""The endpoint register — every gateway route, who answers it, and whether it exists.

docs/api/ENDPOINT-REGISTER.md is the prose; this is the same register as data, so the
rule it enforces can be executed rather than asserted:

    Nothing is built without an assigned endpoint, and no endpoint is listed
    without a state.

Three namespaces, no bleed (the nine rules, 2026-09-17):

  root            /health /ready /version /metrics   bare operational probes
  DIALECT  /v1/*          OpenAI and Anthropic in their EXACT shapes, so unmodified
                          SDKs and Claude Code work with no shim
  NATIVE   /symoneural/v1/*   everything first-party
  RESERVED /api/*        held for the Ollama dialect, verbatim, if it is ever built.
                          Ollama's native surface IS /api/* (server/routes.go @ 5ed8dde3:
                          /api/chat 1897, /api/tags 1875), and the eight routes this
                          estate serves there today collide with it by name. That is why
                          the namespace is being vacated, not extended.

STATE is measured against disk, never against intent:
  BUILT     a handler answers today
  DESIGNED  in the frozen tree; no handler
  RESERVED  namespace held, nothing planned
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from .routeclass import RouteClass
from . import units


class Namespace(enum.StrEnum):
    ROOT = "root"
    DIALECT = "/v1"
    NATIVE = "/symoneural/v1"
    RESERVED = "/api"


class EndpointState(enum.StrEnum):
    BUILT = "BUILT"
    DESIGNED = "DESIGNED"
    RESERVED = "RESERVED"


@dataclass(frozen=True, slots=True)
class Endpoint:
    method: str
    path: str
    namespace: Namespace
    route_class: RouteClass
    unit: str                       # a name in units.REGISTRY
    state: EndpointState
    worker: str = ""                # the engine behind it, if any
    note: str = ""

    @property
    def key(self) -> str:
        return f"{self.method} {self.path}"


# The gateway itself is NOT a rack unit: it has no entry in units.REGISTRY, no port of
# its own in the 8801-8810 block and no GPU claim. It is the thing the units are behind.
# Routes that the gateway answers from its own state - probes, the registry, jobs, the
# GPU view - carry this instead of a unit name.
GATEWAY = "api"

_PUB = RouteClass.PUBLIC_BOOTSTRAP
_APP = RouteClass.AUTHENTICATED_APPLICATION
_OP = RouteClass.OPERATOR_ONLY

REGISTRY: tuple[Endpoint, ...] = (
    # ---- root probes -------------------------------------------------------------
    Endpoint("GET", "/health", Namespace.ROOT, _PUB, "api", EndpointState.DESIGNED,
             note="must touch no worker and never be expensive"),
    Endpoint("GET", "/ready", Namespace.ROOT, _PUB, "api", EndpointState.DESIGNED,
             note="503 the moment an activation, deactivation or drain starts"),
    Endpoint("GET", "/version", Namespace.ROOT, _APP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/metrics", Namespace.ROOT, _OP, "api", EndpointState.DESIGNED),

    # ---- /v1 dialects ------------------------------------------------------------
    Endpoint("GET", "/v1/models", Namespace.DIALECT, _APP, "api", EndpointState.DESIGNED,
             note="lists activatable models too, marked inactive; never activate implicitly"),
    Endpoint("GET", "/v1/models/{model}", Namespace.DIALECT, _APP, "api", EndpointState.DESIGNED),
    Endpoint("POST", "/v1/chat/completions", Namespace.DIALECT, _APP, "chat",
             EndpointState.DESIGNED, worker="llama-server"),
    Endpoint("POST", "/v1/completions", Namespace.DIALECT, _APP, "chat",
             EndpointState.DESIGNED, worker="llama-server"),
    Endpoint("POST", "/v1/responses", Namespace.DIALECT, _APP, "chat",
             EndpointState.DESIGNED, worker="llama-server"),
    Endpoint("GET", "/v1/responses/{id}", Namespace.DIALECT, _APP, "chat", EndpointState.DESIGNED),
    Endpoint("POST", "/v1/responses/{id}/cancel", Namespace.DIALECT, _APP, "chat", EndpointState.DESIGNED),
    Endpoint("POST", "/v1/embeddings", Namespace.DIALECT, _APP, "chat", EndpointState.DESIGNED,
             worker="llama-server", note="404 in the OpenAI envelope unless capabilities.embeddings"),
    Endpoint("POST", "/v1/messages", Namespace.DIALECT, _APP, "chat", EndpointState.DESIGNED,
             worker="llama-server", note="Anthropic; full SSE lifecycle"),
    Endpoint("POST", "/v1/messages/count_tokens", Namespace.DIALECT, _APP, "chat",
             EndpointState.DESIGNED, worker="llama-server",
             note="exact if the worker tokenizes, else estimated:true - never a fake count"),
    # The image rows. sd-server at pin 7f410a37 serves these two in the OpenAI dialect
    # (examples/server/routes_openai.cpp); the estate runs sd-cli per render instead, but
    # the gateway's shape is the dialect's, not the engine's.
    Endpoint("POST", "/v1/images/generations", Namespace.DIALECT, _APP, "image",
             EndpointState.DESIGNED, worker="sd-cli",
             note="worker BUILT and proven 2026-09-17: 768 square in 9.0 s, gate <= 13.44 s"),
    Endpoint("POST", "/v1/images/edits", Namespace.DIALECT, _APP, "image",
             EndpointState.DESIGNED, worker="sd-cli",
             note="added to the tree 2026-09-17; sd-server exposes it at the pin"),

    # ---- /symoneural/v1 native ----------------------------------------------------
    Endpoint("GET", "/symoneural/v1/status", Namespace.NATIVE, _APP, "api", EndpointState.DESIGNED,
             note="today GET /api/status, BUILT"),
    Endpoint("GET", "/symoneural/v1/capabilities", Namespace.NATIVE, _APP, "api",
             EndpointState.DESIGNED, note="gains an image block; rule 8 - declared, not probed"),
    Endpoint("POST", "/symoneural/v1/generate", Namespace.NATIVE, _APP, "chat", EndpointState.DESIGNED),
    Endpoint("POST", "/symoneural/v1/tokenize", Namespace.NATIVE, _APP, "chat", EndpointState.DESIGNED),
    Endpoint("POST", "/symoneural/v1/detokenize", Namespace.NATIVE, _APP, "chat", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/requests", Namespace.NATIVE, _APP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/requests/{id}", Namespace.NATIVE, _APP, "api", EndpointState.DESIGNED),
    Endpoint("POST", "/symoneural/v1/requests/{id}/cancel", Namespace.NATIVE, _APP, "api",
             EndpointState.DESIGNED, note="idempotent; 200 even if already finished"),
    Endpoint("GET", "/symoneural/v1/models", Namespace.NATIVE, _APP, "api", EndpointState.DESIGNED),
    Endpoint("POST", "/symoneural/v1/models", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/models/{id}", Namespace.NATIVE, _APP, "api", EndpointState.DESIGNED),
    Endpoint("PATCH", "/symoneural/v1/models/{id}", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED),
    Endpoint("DELETE", "/symoneural/v1/models/{id}", Namespace.NATIVE, _OP, "api",
             EndpointState.DESIGNED, note="deregister only - never deletes weights"),
    Endpoint("POST", "/symoneural/v1/models/{id}/activate", Namespace.NATIVE, _OP, "api",
             EndpointState.DESIGNED, note="job"),
    Endpoint("POST", "/symoneural/v1/models/{id}/deactivate", Namespace.NATIVE, _OP, "api",
             EndpointState.DESIGNED, note="job"),
    Endpoint("POST", "/symoneural/v1/models/{id}/verify", Namespace.NATIVE, _OP, "api",
             EndpointState.DESIGNED, note="job"),
    Endpoint("GET", "/symoneural/v1/models/{id}/log", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/models/{id}/cache", Namespace.NATIVE, _APP, "api",
             EndpointState.DESIGNED, note="from FreeToken's cache geometry"),
    Endpoint("POST", "/symoneural/v1/models/{id}/cache", Namespace.NATIVE, _OP, "api",
             EndpointState.DESIGNED, note="job"),
    Endpoint("POST", "/symoneural/v1/downloads", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED,
             note="the ONLY route that touches the network; allow-listed; writes outside the repo"),
    Endpoint("GET", "/symoneural/v1/jobs", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/jobs/{id}", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED),
    Endpoint("POST", "/symoneural/v1/jobs/{id}/cancel", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/gpu", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED,
             note="today GET /api/operator/lock, BUILT"),
    Endpoint("POST", "/symoneural/v1/gpu/release", Namespace.NATIVE, _OP, "api",
             EndpointState.DESIGNED, note="break-glass; 409 unless force:true; logged"),
    Endpoint("POST", "/symoneural/v1/gpu/bench", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED,
             note="job; from FreeToken's /bench/run"),
    Endpoint("GET", "/symoneural/v1/gpu/profile", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/units", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/units/{name}", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/apps", Namespace.NATIVE, _APP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/apps/{id}", Namespace.NATIVE, _APP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/apps/{id}/status", Namespace.NATIVE, _APP, "api", EndpointState.DESIGNED),
    Endpoint("POST", "/symoneural/v1/admin/drain", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED),
    Endpoint("POST", "/symoneural/v1/admin/resume", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED),
    Endpoint("GET", "/symoneural/v1/usage", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED,
             note="append-only log with a cursor, not a two-phase ack"),
    Endpoint("GET", "/symoneural/v1/events", Namespace.NATIVE, _OP, "api", EndpointState.DESIGNED,
             note="SSE; replaces polling"),

    # ---- what is actually served today, all in the reserved namespace -------------
    Endpoint("GET", "/api/status", Namespace.RESERVED, _APP, "api", EndpointState.BUILT,
             note="main.py:52 - moves to /symoneural/v1/status"),
    Endpoint("GET", "/api/health", Namespace.RESERVED, _PUB, "api", EndpointState.BUILT,
             note="main.py:91 - moves to /health"),
    Endpoint("GET", "/api/operator/lock", Namespace.RESERVED, _OP, "api", EndpointState.BUILT,
             note="main.py:100 - moves to /symoneural/v1/gpu"),
    Endpoint("POST", "/api/operator/lock/release", Namespace.RESERVED, _OP, "api", EndpointState.BUILT,
             note="main.py:111 - moves to /symoneural/v1/gpu/release"),
    Endpoint("GET", "/api/unit/{name}", Namespace.RESERVED, _APP, "api", EndpointState.BUILT,
             note="main.py:130 - moves to /symoneural/v1/units/{name}"),
    Endpoint("GET", "/api/apps", Namespace.RESERVED, _APP, "api", EndpointState.BUILT,
             note="main.py:172 - moves to /symoneural/v1/apps"),
    Endpoint("GET", "/api/apps/{application_id}", Namespace.RESERVED, _APP, "api", EndpointState.BUILT,
             note="main.py:191"),
    Endpoint("GET", "/api/apps/{application_id}/status", Namespace.RESERVED, _APP, "api",
             EndpointState.BUILT, note="main.py:198"),
)


# A unit with no gateway route, and WHY. This dict is the only permitted answer to
# "why does this unit have no endpoint"; an entry here is a recorded decision, and a
# unit that is in neither this dict nor REGISTRY fails the proof.
UNROUTED: dict[str, str] = {
    "sigils": "no recorded definition anywhere in the repository (docs/diffuse/"
              "ARCHITECTURE.md section 1). It has a port and a rank; giving it a route "
              "would be inventing the product.",
    "ravencalc": "reached on its own port 8801; the frozen tree routes inference and "
                 "control, not every unit's surface.",
    "coder": "reached on its own port 8803; speaks MCP, not an HTTP dialect the gateway "
             "projects.",
    "project": "project and task state is reached on its own port 8804. It is not "
               "inference and not control-plane, so the frozen tree routes neither; if "
               "it ever needs a gateway surface it gets /symoneural/v1, not /v1.",
    "streamer": "reached on its own port 8805; HLS delivery is not a gateway concern.",
    "remix": "reached on its own port 8806; Spotify Connect is its own protocol.",
    "studio": "fine-tuning is driven through jobs, not a dialect route; the job routes "
              "under /symoneural/v1/jobs are the surface.",
    "miner": "Stratum V2 is its own wire protocol on port 8808, not HTTP.",
}


def for_unit(name: str) -> tuple[Endpoint, ...]:
    return tuple(e for e in REGISTRY if e.unit == name)


def built() -> tuple[Endpoint, ...]:
    return tuple(e for e in REGISTRY if e.state is EndpointState.BUILT)


def unassigned_units() -> list[str]:
    """Units with neither an endpoint nor a recorded reason. Must always be empty."""
    return sorted(n for n in units.REGISTRY if not for_unit(n) and n not in UNROUTED)


def unknown_units() -> list[str]:
    """Endpoints naming something that is neither the gateway nor a real unit."""
    return sorted({e.unit for e in REGISTRY if e.unit != GATEWAY and e.unit not in units.REGISTRY})


def duplicate_paths() -> list[str]:
    """Rule 2: one canonical path per operation. No aliases, no redirects."""
    seen, dupes = set(), []
    for e in REGISTRY:
        if e.key in seen:
            dupes.append(e.key)
        seen.add(e.key)
    return dupes
