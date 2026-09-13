"""Route classification — the estate's authorisation model.

Every route in every unit carries exactly one class. The class decides what is
checked before the handler runs. Nothing is implicit, and there is no default:
an unclassified route is a bug, not a public one.

  PUBLIC_BOOTSTRAP          no checks. Must answer while the unit is OFF or
                            unconfigured, and must expose no customer data.
                            /health and /status only.
  SHARED_AUTH               establishes identity. Gating it would make
                            entitlement unreachable. /login, /logout.
  AUTHENTICATED_APPLICATION identity required. The ordinary unit surface.
  ENTITLEMENT_REQUIRED      identity AND a customer->application grant. This is
                            what makes a "head" a purchasable thing.
  OPERATOR_ONLY             the owner token. Never a customer, never a session.
"""

from __future__ import annotations

import enum
import hmac
import os
from dataclasses import dataclass
from typing import Callable


class RouteClass(enum.StrEnum):
    PUBLIC_BOOTSTRAP = "PUBLIC_BOOTSTRAP"
    SHARED_AUTH = "SHARED_AUTH"
    AUTHENTICATED_APPLICATION = "AUTHENTICATED_APPLICATION"
    ENTITLEMENT_REQUIRED = "ENTITLEMENT_REQUIRED"
    OPERATOR_ONLY = "OPERATOR_ONLY"


class AuthzError(Exception):
    """Authorisation failure carrying the HTTP status it should become."""

    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


@dataclass(frozen=True, slots=True)
class Principal:
    """Who is making a request. Never constructed from user input alone."""

    subject: str
    kind: str                      # "operator" | "unit" | "customer"
    entitlements: frozenset[str] = frozenset()

    def entitled_to(self, application: str) -> bool:
        return application in self.entitlements


def _secret(name: str) -> str | None:
    """Read a provisioned secret. Never defaulted, never generated here.

    symoneural-secrets owns provisioning. A missing value means unconfigured,
    and unconfigured must fail closed.
    """
    value = os.environ.get(name)
    return value if value else None


def _matches(presented: str, expected: str) -> bool:
    return hmac.compare_digest(presented.encode(), expected.encode())


def authenticate(token: str | None, unit: str) -> Principal:
    """Resolve a bearer token to a principal.

    Operator token is checked FIRST and is a distinct principal kind. An
    operator is not a customer with extra flags - conflating them is how
    privilege escalation gets written by accident.
    """
    if not token:
        raise AuthzError(401, "bearer token required")

    owner = _secret("SYM_OWNER_TOKEN")
    if owner and _matches(token, owner):
        return Principal(subject="operator", kind="operator")

    unit_token = _secret(f"SYM_{unit.upper()}_TOKEN")
    if unit_token and _matches(token, unit_token):
        return Principal(subject=f"unit:{unit}", kind="unit")

    raise AuthzError(401, "invalid token")


def enforce(
    route_class: RouteClass,
    *,
    unit: str,
    token: str | None,
    application: str | None = None,
) -> Principal | None:
    """Apply one route class. Returns the principal, or None for public routes.

    The order matters and is deliberate: identity before entitlement, always.
    Checking entitlement first would leak which applications exist to an
    unauthenticated caller.
    """
    if route_class is RouteClass.PUBLIC_BOOTSTRAP:
        return None

    if route_class is RouteClass.SHARED_AUTH:
        # Identity is being established here; requiring it would be circular.
        # The unit must still be configured, or there is nothing to establish.
        if not _secret(f"SYM_{unit.upper()}_TOKEN"):
            raise AuthzError(503, f"unit {unit} is unconfigured")
        return None

    principal = authenticate(token, unit)

    if route_class is RouteClass.OPERATOR_ONLY and principal.kind != "operator":
        # 404, not 403: an operator route should not confirm its own existence
        # to a caller who may not have one.
        raise AuthzError(404, "not found")

    if route_class is RouteClass.ENTITLEMENT_REQUIRED:
        if application is None:
            raise AuthzError(500, "ENTITLEMENT_REQUIRED route named no application")
        if principal.kind != "operator" and not principal.entitled_to(application):
            raise AuthzError(403, f"no entitlement for {application}")

    return principal


def classified(route_class: RouteClass, *, unit: str, application: str | None = None):
    """Decorator recording a route's class on the function itself.

    Making the class introspectable is what allows an audit to enumerate every
    route and its protection without reading each handler - the check that
    catches an unclassified route before it ships.
    """

    def wrap(fn: Callable) -> Callable:
        fn.__route_class__ = route_class      # type: ignore[attr-defined]
        fn.__route_unit__ = unit              # type: ignore[attr-defined]
        fn.__route_application__ = application  # type: ignore[attr-defined]
        return fn

    return wrap
