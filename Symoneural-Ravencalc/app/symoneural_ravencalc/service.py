"""RavenCalc HTTP surface — Phase 11's gate.

  /api/ravencalc answers from the estate interpreter.

Served by symoneural-uvicorn on symoneural-fastapi, computing through
symoneural-sympy / mpmath / numpy / scipy linked against symoneural-openblas.
Every layer is an estate package built from pinned source.

Route classes follow the DispatchOS classification:

  PUBLIC_BOOTSTRAP        /health, /backends  — must answer while the unit is
                          off or warming, and must expose no user data
  AUTHENTICATED_APPLICATION  every /compute route — requires a unit token
"""

from __future__ import annotations

import os
import time
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from . import compute

UNIT = "ravencalc"
STARTED = time.time()

app = FastAPI(
    title="SyMoNeuRaL RavenCalc",
    version="1.0.0",
    description="Symbolic and numeric computation from the SyMoNeuRaL estate.",
    docs_url="/api/ravencalc/docs",
    openapi_url="/api/ravencalc/openapi.json",
)


# --------------------------------------------------------------------------
# Auth — SHARED_AUTH
# --------------------------------------------------------------------------

def _expected_token() -> str | None:
    """The unit token, supplied by symoneural-secrets via EnvironmentFile=.

    Never defaulted. An absent token means the unit is unconfigured, and an
    unconfigured unit refuses work rather than serving it openly.
    """
    return os.environ.get("SYM_RAVENCALC_TOKEN")


async def require_unit_token(
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    expected = _expected_token()
    if not expected:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "SYM_RAVENCALC_TOKEN is not set; the unit is unconfigured",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bearer token required")

    presented = authorization.removeprefix("Bearer ").strip()
    # Constant-time: a timing side channel on a token check is a real leak.
    import hmac

    if not hmac.compare_digest(presented, expected):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")


Authed = Annotated[None, Depends(require_unit_token)]


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------

class ExpressionIn(BaseModel):
    expression: str = Field(min_length=1, max_length=4096)


class SolveIn(ExpressionIn):
    symbol: str = Field(default="x", min_length=1, max_length=32)


class PreciseIn(ExpressionIn):
    digits: int = Field(default=50, ge=1, le=5000)


class MatrixIn(BaseModel):
    matrix: list[list[float]] = Field(min_length=1, max_length=512)
    rhs: list[float] = Field(min_length=1, max_length=512)


class IntegrateIn(ExpressionIn):
    lower: float
    upper: float


# --------------------------------------------------------------------------
# PUBLIC_BOOTSTRAP
# --------------------------------------------------------------------------

@app.get("/api/ravencalc/health")
def health() -> dict[str, Any]:
    """Answers even when unconfigured. Reports state; exposes no user data."""
    return {
        "unit": UNIT,
        "status": "ready",
        "uptime_s": round(time.time() - STARTED, 1),
        "configured": _expected_token() is not None,
    }


@app.get("/api/ravencalc/backends")
def backends() -> dict[str, Any]:
    """Which estate packages this process actually imported, and from where.

    This is the Phase 11 gate made checkable: it does not assert that the
    estate's numerics are in use, it imports them and reports the file path.
    """
    return {"unit": UNIT, "backends": compute.backends()}


# --------------------------------------------------------------------------
# AUTHENTICATED_APPLICATION
# --------------------------------------------------------------------------

def _run(fn, *args, **kwargs) -> dict[str, Any]:
    try:
        return fn(*args, **kwargs).to_dict()
    except compute.EvaluationError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exc.reason) from exc


@app.post("/api/ravencalc/simplify")
def do_simplify(body: ExpressionIn, _: Authed) -> dict[str, Any]:
    return _run(compute.simplify, body.expression)


@app.post("/api/ravencalc/solve")
def do_solve(body: SolveIn, _: Authed) -> dict[str, Any]:
    return _run(compute.solve, body.expression, body.symbol)


@app.post("/api/ravencalc/precise")
def do_precise(body: PreciseIn, _: Authed) -> dict[str, Any]:
    return _run(compute.precise, body.expression, body.digits)


@app.post("/api/ravencalc/matrix-solve")
def do_matrix_solve(body: MatrixIn, _: Authed) -> dict[str, Any]:
    return _run(compute.matrix_solve, body.matrix, body.rhs)


@app.post("/api/ravencalc/integrate")
def do_integrate(body: IntegrateIn, _: Authed) -> dict[str, Any]:
    return _run(compute.integrate, body.expression, body.lower, body.upper)


def main() -> None:
    """Entry point. Binds 127.0.0.1:8801 — the tunnel is the only way out."""
    import uvicorn

    uvicorn.run(
        app,
        host=os.environ.get("SYM_RAVENCALC_HOST", "127.0.0.1"),
        port=int(os.environ.get("SYM_RAVENCALC_PORT", "8801")),
        log_level=os.environ.get("SYM_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
