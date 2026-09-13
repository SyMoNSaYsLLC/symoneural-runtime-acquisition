"""RavenCalc compute core — symbolic and numeric evaluation.

Every import here resolves to an ESTATE package, not a wheel from PyPI:
symoneural-sympy, symoneural-mpmath, symoneural-numpy, symoneural-scipy,
symoneural-scikit-learn, all built from pinned upstream source and linked
against symoneural-openblas.

The module is deliberately import-light at module scope. A RavenCalc process
answers /api/ravencalc/health before any heavy numeric import has happened, so
the surface can report honestly while it is still warming.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


class EvaluationError(Exception):
    """Raised when an expression cannot be evaluated.

    Carries the original text so the caller can report what failed without the
    service having to log user input itself.
    """

    def __init__(self, expression: str, reason: str) -> None:
        super().__init__(reason)
        self.expression = expression
        self.reason = reason


@dataclass(slots=True)
class Result:
    """One evaluation, with the provenance needed to trust it."""

    expression: str
    value: str
    kind: str
    elapsed_ms: float
    backend: str
    exact: bool = False
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "expression": self.expression,
            "value": self.value,
            "kind": self.kind,
            "exact": self.exact,
            "elapsed_ms": round(self.elapsed_ms, 3),
            "backend": self.backend,
            "detail": self.detail,
        }


# --------------------------------------------------------------------------
# Symbolic
# --------------------------------------------------------------------------

def simplify(expression: str) -> Result:
    """Simplify an expression symbolically. Exact — no floating point."""
    import sympy

    t0 = time.perf_counter()
    try:
        parsed = sympy.sympify(expression)
        simplified = sympy.simplify(parsed)
    except (sympy.SympifyError, TypeError, AttributeError) as exc:
        raise EvaluationError(expression, f"could not parse: {exc}") from exc

    return Result(
        expression=expression,
        value=str(simplified),
        kind="symbolic",
        exact=True,
        elapsed_ms=(time.perf_counter() - t0) * 1000,
        backend=f"sympy {sympy.__version__}",
        detail={"free_symbols": sorted(str(s) for s in simplified.free_symbols)},
    )


def solve(expression: str, symbol: str = "x") -> Result:
    """Solve expression == 0 for `symbol`. Exact roots where sympy can find them."""
    import sympy

    t0 = time.perf_counter()
    try:
        sym = sympy.Symbol(symbol)
        roots = sympy.solve(sympy.sympify(expression), sym)
    except (sympy.SympifyError, TypeError, NotImplementedError) as exc:
        raise EvaluationError(expression, f"could not solve: {exc}") from exc

    return Result(
        expression=expression,
        value=str(roots),
        kind="roots",
        exact=True,
        elapsed_ms=(time.perf_counter() - t0) * 1000,
        backend=f"sympy {sympy.__version__}",
        detail={"symbol": symbol, "count": len(roots)},
    )


def precise(expression: str, digits: int = 50) -> Result:
    """Evaluate to arbitrary precision via mpmath.

    `digits` is clamped to 5000. Unbounded precision on an unauthenticated
    surface is a denial-of-service vector, not a feature.
    """
    import mpmath

    digits = max(1, min(int(digits), 5000))
    t0 = time.perf_counter()
    prior = mpmath.mp.dps
    try:
        mpmath.mp.dps = digits
        value = mpmath.mpf(mpmath.mpmathify(expression))
        text = mpmath.nstr(value, digits)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise EvaluationError(expression, f"could not evaluate: {exc}") from exc
    finally:
        mpmath.mp.dps = prior

    return Result(
        expression=expression,
        value=text,
        kind="numeric",
        exact=False,
        elapsed_ms=(time.perf_counter() - t0) * 1000,
        backend=f"mpmath {mpmath.__version__}",
        detail={"digits": digits},
    )


# --------------------------------------------------------------------------
# Numeric — these are the paths that exercise OpenBLAS
# --------------------------------------------------------------------------

def matrix_solve(matrix: list[list[float]], rhs: list[float]) -> Result:
    """Solve Ax = b. This is the path that actually exercises OpenBLAS."""
    import numpy as np

    t0 = time.perf_counter()
    try:
        a = np.asarray(matrix, dtype=np.float64)
        b = np.asarray(rhs, dtype=np.float64)
    except (ValueError, TypeError) as exc:
        raise EvaluationError("matrix_solve", f"bad input: {exc}") from exc

    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise EvaluationError("matrix_solve", f"matrix must be square, got {a.shape}")
    if b.shape[0] != a.shape[0]:
        raise EvaluationError(
            "matrix_solve", f"rhs length {b.shape[0]} != matrix rank {a.shape[0]}"
        )

    try:
        x = np.linalg.solve(a, b)
    except np.linalg.LinAlgError as exc:
        raise EvaluationError("matrix_solve", f"singular or ill-conditioned: {exc}") from exc

    residual = float(np.linalg.norm(a @ x - b))
    return Result(
        expression=f"solve A({a.shape[0]}x{a.shape[1]}) x = b",
        value=repr(x.tolist()),
        kind="linear-algebra",
        elapsed_ms=(time.perf_counter() - t0) * 1000,
        backend=f"numpy {np.__version__}",
        detail={
            "shape": list(a.shape),
            "residual_norm": residual,
            "condition_number": float(np.linalg.cond(a)),
        },
    )


def integrate(expression: str, lower: float, upper: float) -> Result:
    """Definite integral by adaptive quadrature (scipy.integrate.quad)."""
    import numpy as np
    from scipy import integrate as si
    import sympy

    t0 = time.perf_counter()
    try:
        sym = sympy.Symbol("x")
        fn = sympy.lambdify(sym, sympy.sympify(expression), modules=["numpy"])
    except (sympy.SympifyError, TypeError) as exc:
        raise EvaluationError(expression, f"could not parse: {exc}") from exc

    try:
        value, abserr = si.quad(fn, float(lower), float(upper))
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise EvaluationError(expression, f"quadrature failed: {exc}") from exc

    import scipy

    return Result(
        expression=f"integral of {expression} from {lower} to {upper}",
        value=repr(float(value)),
        kind="quadrature",
        elapsed_ms=(time.perf_counter() - t0) * 1000,
        backend=f"scipy {scipy.__version__} / numpy {np.__version__}",
        detail={"absolute_error": float(abserr), "lower": lower, "upper": upper},
    )


def backends() -> dict[str, Any]:
    """Report which estate packages are importable, and from where.

    R16 in code: the service does not claim a backend is present, it imports it
    and reports the file it came from. A package installed from the estate feed
    resolves under the target sysroot; anything else is visible in the path.
    """
    found: dict[str, Any] = {}
    for name in ("sympy", "mpmath", "numpy", "scipy", "sklearn"):
        try:
            mod = __import__(name)
        except ImportError as exc:
            found[name] = {"available": False, "error": str(exc)}
            continue
        found[name] = {
            "available": True,
            "version": getattr(mod, "__version__", "unknown"),
            "path": getattr(mod, "__file__", "unknown"),
        }

    blas: dict[str, Any] = {"available": False}
    try:
        import numpy as np

        cfg = getattr(np, "show_config", None)
        if cfg is not None:
            blas = {"available": True, "reported_by": "numpy.show_config"}
    except ImportError:
        pass
    found["blas"] = blas
    return found
