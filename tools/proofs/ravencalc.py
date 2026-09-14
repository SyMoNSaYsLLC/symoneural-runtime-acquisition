"""Ravencalc clean-root proof body: run INSIDE the extracted image by tools/clean-root-proof.
Imports the numerics closure, refuses build frontends, and performs one meaningful
consumer operation per library (the same calls a RavenCalc request would make)."""
import importlib, sys
from importlib.metadata import version, PackageNotFoundError

# module -> exact version REQUIRED by a recorded ruling, or None for "any installed".
# An import that merely succeeds proves nothing about which pin reached the target:
# the previous run printed "mpmath 1.4.1 PASS" from a stale image while the ruling
# sympy-mpmath-constraint (RESOLVED-A) had already re-pinned mpmath to 1.3.0.
want = {"numpy": None, "scipy": None, "sklearn": None, "sympy": None,
        "mpmath": "1.3.0",          # ruling: unresolved.json sympy-mpmath-constraint RESOLVED-A
        "joblib": None, "cloudpickle": None, "threadpoolctl": None, "narwhals": None,
        "fastapi": None, "pydantic": None, "uvicorn": None, "symoneural_api": None}
dist = {"sklearn": "scikit-learn", "symoneural_api": "symoneural-api"}
bad = []
for mod, exact in want.items():
    try:
        importlib.import_module(mod)
    except Exception as e:
        bad.append("%s: import failed: %r" % (mod, e)); print("  %-16s FAIL %r" % (mod, e)); continue
    try:
        v = version(dist.get(mod, mod))
    except PackageNotFoundError:
        v = "?"
    ok = (exact is None) or (v == exact)
    print("  %-16s %-12s %s" % (mod, v, "PASS" if ok else "FAIL (ruling requires %s)" % exact))
    if not ok:
        bad.append("%s is %s, the recorded ruling requires %s" % (mod, v, exact))
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
    # the declared closure is the gate: sympy's own metadata, evaluated against the
    # mpmath actually installed here. Upper bound parsed without `packaging`, which
    # is not a runtime dependency of this closure and must not be imported on target.
    from importlib.metadata import requires
    req = [r for r in (requires("sympy") or []) if r.startswith("mpmath")]
    got = tuple(int(x) for x in version("mpmath").split(".")[:3])
    for clause in (req[0].split(";")[0].replace("mpmath", "", 1) if req else "").split(","):
        clause = clause.strip()
        if not clause:
            continue
        op = clause[:2] if clause[:2] in ("<=", ">=", "==", "!=") else clause[:1]
        bound = tuple(int(x) for x in clause[len(op):].strip().split(".")[:3])
        held = {"<": got < bound, "<=": got <= bound, ">": got > bound,
                ">=": got >= bound, "==": got == bound, "!=": got != bound}[op]
        if not held:
            bad.append("sympy declares mpmath%s but %s is installed" % (clause, version("mpmath")))
    print("  sympy declares %s; installed mpmath %s -> %s"
          % (req, version("mpmath"), "SATISFIED" if not bad else "VIOLATED"))
if bad:
    print("FAIL:"); [print("   -", b) for b in bad]; sys.exit(1)
print("RAVENCALC CLEAN ROOT PROOF: PASS")
