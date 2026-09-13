"""DispatchOS — the SyMoNeuRaL control plane.

One FastAPI application fronting every unit on the rack. It owns identity,
entitlement, the unit registry and the GPU lock; it owns no inference. A unit
answers for itself, and this layer decides whether the caller may ask.

FastAPI does ALL the routing. Nothing above this rewrites a path or makes a
routing decision - if a request reaches a handler, this file chose it.
"""

from __future__ import annotations

import os
import time
from typing import Annotated, Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from . import gpulock, units
from .routeclass import AuthzError, RouteClass, enforce

STARTED = time.time()

app = FastAPI(
    title="SyMoNeuRaL DispatchOS",
    version="1.0.0",
    description="Control plane for the SyMoNeuRaL rack.",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


def _bearer(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.removeprefix("Bearer ").strip() or None


@app.exception_handler(AuthzError)
async def _authz_handler(_: Request, exc: AuthzError) -> JSONResponse:
    """Authorisation failures carry their own status; nothing is re-mapped."""
    return JSONResponse(status_code=exc.status, content={"detail": exc.detail})


# --------------------------------------------------------------------------
# PUBLIC_BOOTSTRAP — answers while units are off. No customer data, ever.
# --------------------------------------------------------------------------

@app.get("/api/status")
def status() -> dict[str, Any]:
    """The rack, as it is right now.

    Reports only on/off, resource class and lock state. A unit reading OFFLINE
    is telling the truth: nothing here is lit for effect.
    """
    holder = gpulock.current()
    rack = []
    for u in units.REGISTRY.values():
        configured = bool(os.environ.get(u.token_env))
        enabled = os.environ.get(u.enabled_variable, "0") == "1"
        if not configured:
            state = units.UnitState.UNCONFIGURED
        elif not enabled:
            state = units.UnitState.OFFLINE
        elif holder and holder.unit == u.name:
            state = units.UnitState.BUSY
        elif holder and u.resource is units.Resource.GPU:
            state = units.UnitState.QUEUED
        else:
            state = units.UnitState.READY
        rack.append({
            "unit": u.name,
            "resource": str(u.resource),
            "state": str(state),
            "port": u.port,
            "height": u.height,
            "description": u.description,
            "backed_by": list(u.backed_by),
        })

    return {
        "uptime_s": round(time.time() - STARTED, 1),
        "gpu_lock": holder.to_dict() if holder else None,
        "units": rack,
    }


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ready", "uptime_s": round(time.time() - STARTED, 1)}


# --------------------------------------------------------------------------
# OPERATOR_ONLY
# --------------------------------------------------------------------------

@app.get("/api/operator/lock")
def lock_state(authorization: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    enforce(RouteClass.OPERATOR_ONLY, unit="api", token=_bearer(authorization))
    holder = gpulock.current()
    return {
        "holder": holder.to_dict() if holder else None,
        "priorities": gpulock.PRIORITY,
        "lock_path": str(gpulock.LOCK_PATH),
    }


@app.post("/api/operator/lock/release")
def lock_release(
    unit: str,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    """Force-release a stranded lock.

    Operator-only and deliberately explicit: it names the unit rather than
    clearing whatever is there, so releasing the wrong holder takes intent.
    """
    enforce(RouteClass.OPERATOR_ONLY, unit="api", token=_bearer(authorization))
    released = gpulock.release(unit, force=True)
    return {"released": released, "unit": unit}


# --------------------------------------------------------------------------
# ENTITLEMENT_REQUIRED
# --------------------------------------------------------------------------

@app.get("/api/unit/{name}")
def unit_detail(
    name: str,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    try:
        u = units.unit(name)
    except KeyError:
        raise HTTPException(404, f"no such unit: {name}") from None

    principal = enforce(
        RouteClass.ENTITLEMENT_REQUIRED,
        unit=name,
        token=_bearer(authorization),
        application=name,
    )
    return {
        "unit": u.name,
        "resource": str(u.resource),
        "port": u.port,
        "backed_by": list(u.backed_by),
        "principal": principal.kind if principal else None,
    }


def main() -> None:
    import uvicorn

    uvicorn.run(
        app,
        host=os.environ.get("SYMONEURAL_HOST", "127.0.0.1"),
        port=int(os.environ.get("SYMONEURAL_PORT", "8800")),
        log_level=os.environ.get("SYM_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
