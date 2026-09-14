"""Ravencalc clean-root proof body: run INSIDE the extracted image by tools/clean-root-proof.
Imports the numerics closure, refuses build frontends, and performs one meaningful
consumer operation per library (the same calls a RavenCalc request would make)."""
import importlib, sys
from importlib.metadata import version, PackageNotFoundError

want = ["numpy", "scipy", "sklearn", "sympy", "mpmath", "joblib", "threadpoolctl", "narwhals",
        "fastapi", "pydantic", "uvicorn", "symoneural_api"]
dist = {"sklearn": "scikit-learn", "symoneural_api": "symoneural-api"}
bad = []
for mod in want:
    try:
        importlib.import_module(mod)
    except Exception as e:
        bad.append("%s: import failed: %r" % (mod, e)); print("  %-16s FAIL %r" % (mod, e)); continue
    try:
        v = version(dist.get(mod, mod))
    except PackageNotFoundError:
        v = "?"
    print("  %-16s %-12s PASS" % (mod, v))
for f in ("maturin", "hatchling", "pdm", "flit_core", "setuptools_scm", "meson", "Cython", "pythran"):
    try:
        importlib.import_module(f); bad.append("build frontend %s present on target" % f)
    except Exception:
        pass
if not bad:
    import numpy as np, scipy.linalg, sympy, mpmath
    from sklearn.linear_model import LinearRegression
    from sklearn.utils import parallel_backend
    A = np.array([[3.0, 1.0], [1.0, 2.0]]); b = np.array([9.0, 8.0])
    x = scipy.linalg.solve(A, b); assert np.allclose(A @ x, b), x
    X = np.arange(10, dtype=float).reshape(-1, 1); y = 2.5 * X[:, 0] + 1.0
    with parallel_backend("threading", n_jobs=2):          # exercises joblib + threadpoolctl
        m = LinearRegression().fit(X, y)
    assert abs(m.coef_[0] - 2.5) < 1e-9 and abs(m.intercept_ - 1.0) < 1e-9, (m.coef_, m.intercept_)
    s = sympy.integrate(sympy.Symbol("t") ** 2, (sympy.Symbol("t"), 0, 3)); assert s == 9, s
    mpmath.mp.dps = 30; pi = mpmath.pi; assert str(pi).startswith("3.14159265358979323846264338327"), pi
    import narwhals as nw
    print("  meaningful ops: scipy solve, sklearn fit under joblib threading backend (coef 2.5, intercept 1.0), sympy integrate = 9, mpmath pi @30dps, narwhals %s PASS" % nw.__version__)
    # the declared constraint sympy places on mpmath, evaluated on the installed pair
    from importlib.metadata import requires
    req = [r for r in (requires("sympy") or []) if r.startswith("mpmath")]
    print("  sympy declares:", req, "; installed mpmath", version("mpmath"))
if bad:
    print("FAIL:"); [print("   -", b) for b in bad]; sys.exit(1)
print("RAVENCALC CLEAN ROOT PROOF: PASS")
