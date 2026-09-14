"""The application registry — applications and demos as a GENERIC API concept.

An application is a customer-facing composition of platform capabilities: the
units it requires, the units it can degrade without, the models it may use, the
page that fronts it and the policy profile it runs under. The first registered
application (symoneural_api/apps/) is one entry, not the shape of the registry:
adding a demo means adding a module there plus first-party page content - never
a change to the native platform, and never a customer name in generic code.

Readiness is derived, not declared: an application is READY only when every
required unit has an installable backend (units.backing_packages) AND the unit
is configured; DEGRADED when only optional units are missing; BLOCKED otherwise.
The registry explains *why* rather than returning a vague 500.
"""

from __future__ import annotations

import enum
import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable

from . import units


class Mode(enum.StrEnum):
    DEMO = "demo"            # public, restricted policy, isolated sessions
    CUSTOMER = "customer"    # entitled customers of a tenant
    INTERNAL = "internal"    # operator-only surfaces


class Readiness(enum.StrEnum):
    READY = "READY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class DemoPolicy:
    """What a PUBLIC demo may do. Every field is a restriction; nothing widens.

    A public demo is a separate trust boundary from customer/operator use, so
    admin operations are never reachable through it and mutating operations
    are opt-in per application.
    """
    allowed_models: frozenset[str] = frozenset()
    allowed_units: frozenset[str] = frozenset()
    allow_mutations: bool = False
    max_requests_per_minute: int = 30
    max_concurrent_sessions: int = 4
    session_lifetime_s: int = 900
    tool_capabilities: frozenset[str] = frozenset()   # e.g. {"read_status"}; never shell/file tools by default
    expose_admin: bool = False                           # fixed False; kept explicit so audits can grep it

    def restricts_model(self, model: str) -> bool:
        return model not in self.allowed_models

    def to_public(self) -> dict[str, Any]:
        return {
            "allowed_models": sorted(self.allowed_models),
            "allowed_units": sorted(self.allowed_units),
            "allow_mutations": self.allow_mutations,
            "max_requests_per_minute": self.max_requests_per_minute,
            "max_concurrent_sessions": self.max_concurrent_sessions,
            "session_lifetime_s": self.session_lifetime_s,
            "tool_capabilities": sorted(self.tool_capabilities),
        }


_ID = re.compile(r"^[a-z][a-z0-9-]{1,39}$")
_NS = re.compile(r"^/api/apps/[a-z][a-z0-9-]{1,39}$")
_PAGE = re.compile(r"^/demo/[a-z][a-z0-9-]{1,39}\.html$")


@dataclass(frozen=True, slots=True)
class ApplicationDefinition:
    application_id: str
    display_name: str
    mode: Mode
    required_units: tuple[str, ...]
    optional_units: tuple[str, ...] = ()
    allowed_models: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    public_demo: bool = False
    page: str | None = None                 # /demo/<id>.html for demos
    policy: DemoPolicy | None = None        # required when public_demo

    @property
    def api_namespace(self) -> str:
        return f"/api/apps/{self.application_id}"

    def validate(self) -> None:
        if not _ID.match(self.application_id):
            raise ValueError(f"application_id {self.application_id!r} must match {_ID.pattern}")
        if not _NS.match(self.api_namespace):
            raise ValueError(f"bad api namespace {self.api_namespace}")
        for u in (*self.required_units, *self.optional_units):
            if u not in units.REGISTRY:
                raise ValueError(f"{self.application_id}: unknown unit {u!r}; known: {sorted(units.REGISTRY)}")
        if set(self.required_units) & set(self.optional_units):
            raise ValueError(f"{self.application_id}: a unit cannot be both required and optional")
        if self.public_demo:
            if self.page is None or not _PAGE.match(self.page):
                raise ValueError(f"{self.application_id}: a public demo needs page /demo/<id>.html, got {self.page!r}")
            if self.page != f"/demo/{self.application_id}.html":
                raise ValueError(f"{self.application_id}: page must be /demo/{self.application_id}.html")
            if self.policy is None:
                raise ValueError(f"{self.application_id}: a public demo needs a DemoPolicy")
            if self.policy.expose_admin:
                raise ValueError(f"{self.application_id}: a public demo may never expose admin")
            if not self.policy.allowed_units <= set(self.required_units) | set(self.optional_units):
                raise ValueError(f"{self.application_id}: policy allows units the application does not declare")
        elif self.page is not None and not _PAGE.match(self.page):
            raise ValueError(f"{self.application_id}: page must look like /demo/<id>.html")

    # -- what the browser may know: no paths, no secrets, no service names
    def to_public(self) -> dict[str, Any]:
        return {
            "application_id": self.application_id,
            "display_name": self.display_name,
            "mode": str(self.mode),
            "api_namespace": self.api_namespace,
            "page": self.page,
            "required_units": list(self.required_units),
            "optional_units": list(self.optional_units),
            "allowed_models": list(self.allowed_models),
            "capabilities": list(self.capabilities),
            "public_demo": self.public_demo,
            "policy": self.policy.to_public() if self.policy else None,
        }


REGISTRY: dict[str, ApplicationDefinition] = {}


def register(app: ApplicationDefinition) -> ApplicationDefinition:
    app.validate()
    if app.application_id in REGISTRY:
        raise ValueError(f"duplicate application_id {app.application_id!r}")
    if app.page and any(a.page == app.page for a in REGISTRY.values()):
        raise ValueError(f"page {app.page} already mapped")
    REGISTRY[app.application_id] = app
    return app


def unregister(application_id: str) -> None:
    REGISTRY.pop(application_id, None)


def application(application_id: str) -> ApplicationDefinition:
    try:
        return REGISTRY[application_id]
    except KeyError:
        raise KeyError(f"unknown application {application_id!r}; known: {sorted(REGISTRY)}") from None


def for_page(page: str) -> ApplicationDefinition | None:
    return next((a for a in REGISTRY.values() if a.page == page), None)


# -- readiness -----------------------------------------------------------------

UnitProbe = Callable[[units.Unit], dict[str, Any]]


def _default_probe(u: units.Unit) -> dict[str, Any]:
    """Per-unit facts the API already knows: configured (token provisioned) and
    enabled. Backing-package presence is asked of the unit graph separately."""
    return {
        "configured": bool(os.environ.get(u.token_env)),
        "enabled": os.environ.get(u.enabled_variable, "0") == "1",
    }


def readiness(app: ApplicationDefinition, *, installed_packages: set[str] | None = None,
              probe: UnitProbe = _default_probe) -> dict[str, Any]:
    """Explain whether an application can run, unit by unit.

    installed_packages: the set of estate packages known to be installed on this
    target (from pkgdata / opkg status / a manifest). None means "unknown", which
    is reported as such and does NOT count as installed.
    """
    detail = []
    blocked, degraded = [], []
    for name in (*app.required_units, *app.optional_units):
        u = units.unit(name)
        required = name in app.required_units
        p = probe(u)
        backers = list(u.backed_by)
        missing = [b for b in backers if installed_packages is not None and b not in installed_packages]
        unknown = installed_packages is None
        ok = p["configured"] and p["enabled"] and not missing and not unknown
        reasons = []
        if unknown: reasons.append("backing packages: installed set unknown")
        if missing: reasons.append("backing packages not installed: " + ", ".join(missing))
        if not p["configured"]: reasons.append(f"unit {name} unconfigured (no {u.token_env})")
        if not p["enabled"]: reasons.append(f"unit {name} not enabled ({u.enabled_variable} != 1)")
        detail.append({"unit": name, "required": required, "ok": ok, "reasons": reasons, "backed_by": backers})
        if not ok:
            (blocked if required else degraded).append(name)
    state = Readiness.BLOCKED if blocked else (Readiness.DEGRADED if degraded else Readiness.READY)
    return {"application_id": app.application_id, "readiness": str(state),
            "blocking_units": blocked, "degraded_units": degraded, "units": detail}


def route_class_for(app: ApplicationDefinition):
    """The route class an application's API namespace runs under.

    Demos are PUBLIC_BOOTSTRAP at the namespace root (readiness/status) with the
    DemoPolicy enforced inside; customer applications require entitlement;
    internal ones are operator-only. Imported lazily to avoid a cycle."""
    from .routeclass import RouteClass
    return {Mode.DEMO: RouteClass.PUBLIC_BOOTSTRAP,
            Mode.CUSTOMER: RouteClass.ENTITLEMENT_REQUIRED,
            Mode.INTERNAL: RouteClass.OPERATOR_ONLY}[app.mode]
