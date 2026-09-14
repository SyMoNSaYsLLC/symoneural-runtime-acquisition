"""Ravencalc clean-root proof body: run INSIDE the extracted image by tools/clean-root-proof.
Imports the numerics closure, refuses build frontends, and performs one meaningful
consumer operation per library (the same calls a RavenCalc request would make)."""
import importlib, os, sys
from importlib.metadata import version, PackageNotFoundError

# Let anything that spawns a subprocess re-enter the TARGET interpreter through the
# same loader + library path (tools/clean-root-proof writes the wrapper). Without
# this, multiprocessing's resource_tracker re-execs a bare sys.executable that cannot
# find its own libraries and dies with BrokenPipeError - a harness artefact, not an
# estate defect. With it, joblib's real process parallelism is genuinely exercised.
# This must happen BEFORE joblib is imported: joblib's vendored loky reads
# sys.executable into a module global (externals/loky/backend/spawn.py) at import
# time and its own resource tracker spawns THAT, ignoring
# multiprocessing.set_executable(). Pointing sys.executable at the wrapper is one
# lever that covers loky, the stdlib resource_tracker, and multiprocessing alike -
# and it is truthful: the wrapper IS how this interpreter is invoked here.
_wrap = os.environ.get("SYM_TARGET_PYTHON")
if _wrap and os.path.exists(_wrap):
    import multiprocessing
    sys.executable = _wrap
    multiprocessing.set_executable(_wrap)

# module -> exact version REQUIRED by a recorded ruling, or None for "any installed".
# An import that merely succeeds proves nothing about which pin reached the target:
# the previous run printed "mpmath 1.4.1 PASS" from a stale image while the ruling
# sympy-mpmath-constraint (RESOLVED-A) had already re-pinned mpmath to 1.3.0.
want = {"numpy": None, "scipy": None, "sklearn": None, "sympy": None,
        "mpmath": "1.3.0",          # ruling: unresolved.json sympy-mpmath-constraint RESOLVED-A
        "joblib": None, "cloudpickle": None, "threadpoolctl": None, "narwhals": None,
        "fastapi": None, "pydantic": None, "uvicorn": None, "symoneural_api": None}
dist = {"sklearn": "scikit-learn", "symoneural_api": "symoneural-api"}
def _square(v):
    """Module-level so the loky backend can ship it to a worker process."""
    return v * v


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
    # Each op must EXERCISE the library it names, not merely touch a module that
    # imports it. sklearn.utils.parallel_backend was removed in scikit-learn 1.5;
    # joblib.parallel_backend is the real entry point sklearn always delegated to.
    import numpy as np, scipy.linalg, sympy, mpmath, joblib, cloudpickle
    from sklearn.linear_model import LinearRegression
    from sklearn.utils.parallel import Parallel, delayed, ThreadpoolController

    # scipy: solve a linear system and check the residual, not just the call
    A = np.array([[3.0, 1.0], [1.0, 2.0]]); b = np.array([9.0, 8.0])
    x = scipy.linalg.solve(A, b); assert np.allclose(A @ x, b), x

    # sklearn under joblib's threading backend: an exact-fit regression
    X = np.arange(10, dtype=float).reshape(-1, 1); y = 2.5 * X[:, 0] + 1.0
    with joblib.parallel_backend("threading", n_jobs=2):
        m = LinearRegression().fit(X, y)
    assert abs(m.coef_[0] - 2.5) < 1e-9 and abs(m.intercept_ - 1.0) < 1e-9, (m.coef_, m.intercept_)

    # sklearn's own parallel path (its Parallel/delayed wrapper over joblib), threaded
    got = Parallel(n_jobs=2, prefer="threads")(delayed(abs)(v) for v in (-3, -1, 4))
    assert got == [3, 1, 4], got

    # joblib's PROCESS backend (loky), which is why cloudpickle is in this closure:
    # the work is sent to real worker processes of the target interpreter.
    procs = joblib.Parallel(n_jobs=2, backend="loky")(
        joblib.delayed(_square)(v) for v in (2, 5, 9))
    assert procs == [4, 25, 81], procs

    # threadpoolctl is REACHED THROUGH sklearn, not imported in isolation:
    # ThreadpoolController is sklearn's threadpoolctl integration, and it must be
    # able to enumerate and cap the native BLAS/OpenMP pools numpy and scipy loaded.
    ctl = ThreadpoolController()
    pools = ctl.info()
    with ctl.limit(limits=1, user_api="blas"):
        assert all(p["num_threads"] == 1 for p in ctl.info() if p["user_api"] == "blas"), ctl.info()
    assert all(p["num_threads"] >= 1 for p in ctl.info()), "thread limits not restored"

    # cloudpickle does the thing pickle CANNOT: serialise a lambda by value.
    # This is why joblib requires it, so prove that capability, not the import.
    import pickle
    try:
        pickle.dumps(lambda v: v * 7); pickled_lambda = True
    except Exception:
        pickled_lambda = False
    assert not pickled_lambda, "stdlib pickle unexpectedly serialised a lambda"
    assert cloudpickle.loads(cloudpickle.dumps(lambda v: v * 7))(6) == 42

    # sympy symbolic integration and mpmath at 30 significant digits
    t = sympy.Symbol("t")
    assert sympy.integrate(t ** 2, (t, 0, 3)) == 9
    # 30 significant digits is far beyond float64 (~17), so this proves the
    # arbitrary-precision core, not a float in disguise. The expected value is pi
    # ROUNDED to 30 digits (3.14159265358979323846264338327950288... -> ...328);
    # an earlier truncation to ...327 was simply wrong arithmetic on my part and had
    # never been reached, because the proof failed before it on cloudpickle.
    mpmath.mp.dps = 30
    assert str(mpmath.pi) == "3.14159265358979323846264338328", mpmath.pi
    assert abs(mpmath.pi - mpmath.mpf("3.14159265358979323846264338327950288")) < mpmath.mpf(10) ** -29
    assert mpmath.mpf(1) / 3 != mpmath.mpf(float(1) / 3), "mpmath is tracking only float64 precision"

    import narwhals as nw
    print("  meaningful ops PASS: scipy.linalg.solve residual ok; LinearRegression under "
          "joblib.parallel_backend('threading') -> coef 2.5 intercept 1.0; sklearn "
          "Parallel/delayed -> [3, 1, 4]; ThreadpoolController capped %d native pool(s) to 1 "
          "and restored; cloudpickle round-tripped a lambda pickle refused; sympy "
          "integrate(t**2, 0..3) = 9; mpmath pi @30dps; narwhals %s"
          % (len([p for p in pools if p["user_api"] == "blas"]), nw.__version__))
    print("  process parallelism PASS: joblib loky backend ran on real worker processes "
          "of the target interpreter (multiprocessing.set_executable -> %s) -> [4, 25, 81]"
          % _wrap)
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
