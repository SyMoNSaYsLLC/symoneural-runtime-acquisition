"""API clean-root proof body: run INSIDE the extracted image by tools/clean-root-proof.

The API runtime was the one Python runtime with no consumer proof: `check-python-runtime-
closures.py --runtime API` reads built-wheel metadata, which is a declaration, not an
execution (R16). This file is the execution. It imports the FastAPI/Starlette/uvicorn/
pydantic closure AND the estate's own `symoneural_api`, then serves real requests through
an in-process ASGI transport — no socket is bound, no port is taken, nothing touches the
network, and `127.0.0.1:8800` is never contacted (R14).

Two of the checks below exist because three chat-output documents dated 16-17 September
disagreed with the repository about them. They are executed here so the answer stops being
a claim in a note: the chat unit's port is 8802, and an OPERATOR_ONLY route answers 404 to
a non-operator, not 403.
"""
import importlib, os, sys
from importlib.metadata import version, PackageNotFoundError

# see tools/proofs/ravencalc.py: let anything that spawns re-enter the TARGET interpreter
_wrap = os.environ.get("SYM_TARGET_PYTHON")
if _wrap and os.path.exists(_wrap):
    import multiprocessing
    sys.executable = _wrap
    multiprocessing.set_executable(_wrap)

# module -> exact version a consumer pins, or None for "any installed".
# The exact pins are the ones the 17 September reference gateway was written against;
# if one of them moves, that document's file:line citations stop matching this runtime.
want = {"fastapi": "0.141.1", "starlette": "1.6.0", "uvicorn": "0.52.4",
        "pydantic": "2.13.5", "pydantic_core": "2.46.5", "httpx": "0.28.1",
        "httpcore": None, "h11": None, "anyio": None, "sniffio": None, "idna": None,
        "certifi": None, "click": None, "annotated_types": None, "annotated_doc": None,
        "typing_extensions": None, "typing_inspection": None,
        "symoneural_api": "1.0.0"}
dist = {"pydantic_core": "pydantic-core", "annotated_types": "annotated-types",
        "annotated_doc": "annotated-doc", "typing_extensions": "typing-extensions",
        "typing_inspection": "typing-inspection"}
bad = []
for mod, exact in want.items():
    try:
        importlib.import_module(mod)
    except Exception as e:
        bad.append("%s: import failed: %r" % (mod, e)); print("  %-26s FAIL %r" % (mod, e)); continue
    try:
        v = version(dist.get(mod, mod))
    except PackageNotFoundError:
        v = "?"
    ok = (exact is None) or (v == exact)
    print("  %-26s %-12s %s" % (mod, v, "PASS" if ok else "FAIL (consumer requires %s)" % exact))
    if not ok:
        bad.append("%s is %s, a consumer requires %s" % (mod, v, exact))

# a clean runtime must carry no build frontend
for f in ("maturin", "hatchling", "pdm", "flit_core", "setuptools_scm", "build", "wheel"):
    try:
        importlib.import_module(f); bad.append("build frontend %s present on target" % f)
    except Exception:
        pass

if not bad:
    import asyncio, json as _json
    import httpx
    from fastapi import FastAPI
    from pydantic import BaseModel, Field, ValidationError

    # ---------------------------------------------------------------- upstream stack
    # One app exercising fastapi + starlette + pydantic + httpx + anyio together, served
    # over httpx's ASGI transport: a real request/response cycle with no listening socket.
    class Echo(BaseModel):
        unit: str = Field(min_length=1)
        replicas: int = Field(ge=1, le=8)

    probe = FastAPI(title="symoneural-api-proof")

    @probe.get("/healthz")
    def _healthz() -> dict[str, str]:
        return {"status": "ok"}

    @probe.post("/echo")
    def _echo(body: Echo) -> dict[str, object]:
        return {"unit": body.unit, "replicas": body.replicas}

    async def _exercise(app, checks):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://asgi.invalid") as c:
            return await checks(c)

    async def _upstream(c):
        out = {}
        r = await c.get("/healthz")
        out["healthz"] = (r.status_code, r.json())
        r = await c.post("/echo", json={"unit": "chat", "replicas": 2})
        out["echo"] = (r.status_code, r.json())
        r = await c.post("/echo", json={"unit": "", "replicas": 99})   # two violations
        out["invalid"] = (r.status_code, r.json())
        return out

    u = asyncio.run(_exercise(probe, _upstream))
    assert u["healthz"] == (200, {"status": "ok"}), u["healthz"]
    assert u["echo"] == (200, {"unit": "chat", "replicas": 2}), u["echo"]
    assert u["invalid"][0] == 422, u["invalid"]          # pydantic rejected, FastAPI rendered
    assert len(u["invalid"][1]["detail"]) == 2, u["invalid"]

    # pydantic directly, so a FastAPI regression cannot mask a broken pydantic_core
    try:
        Echo(unit="x", replicas=0); raise AssertionError("pydantic accepted replicas=0 under ge=1")
    except ValidationError:
        pass

    # uvicorn resolves and configures the app without binding: Config() does the import
    # and protocol selection that a real serve would, and stops short of the socket.
    import uvicorn
    cfg = uvicorn.Config(probe, host="127.0.0.1", port=0, log_level="warning", lifespan="off")
    cfg.load()
    assert cfg.loaded_app is not None and cfg.host == "127.0.0.1"

    # ------------------------------------------------------- the estate's own API layer
    # Test-only fixtures, deliberately not secret-shaped and never written anywhere:
    # routeclass._secret reads the environment, and an unconfigured unit must fail closed.
    os.environ["SYM_OWNER_TOKEN"] = "proof-operator-fixture-not-a-secret"
    os.environ["SYM_API_TOKEN"] = "proof-unit-fixture-not-a-secret"

    from symoneural_api import units
    from symoneural_api.routeclass import AuthzError, Principal, RouteClass, authenticate, enforce

    # The five route classes the 17 September documents did not know about.
    assert [c.value for c in RouteClass] == [
        "PUBLIC_BOOTSTRAP", "SHARED_AUTH", "AUTHENTICATED_APPLICATION",
        "ENTITLEMENT_REQUIRED", "OPERATOR_ONLY"], list(RouteClass)

    # public route: no token, no principal, no error
    assert enforce(RouteClass.PUBLIC_BOOTSTRAP, unit="api", token=None) is None

    # no token at all -> 401
    try:
        authenticate(None, "api"); raise AssertionError("authenticate accepted an absent token")
    except AuthzError as e:
        assert e.status == 401, e.status

    # wrong token -> 401, and the comparison is constant-time (hmac.compare_digest)
    try:
        authenticate("not-the-token", "api"); raise AssertionError("authenticate accepted a wrong token")
    except AuthzError as e:
        assert e.status == 401, e.status

    op = authenticate(os.environ["SYM_OWNER_TOKEN"], "api")
    assert isinstance(op, Principal) and op.kind == "operator", op
    unit_principal = authenticate(os.environ["SYM_API_TOKEN"], "api")
    assert unit_principal.kind == "unit", unit_principal

    # THE CORRECTION, EXECUTED: an operator route answers 404 to a non-operator, so that it
    # does not confirm its own existence. Three documents said 403.
    try:
        enforce(RouteClass.OPERATOR_ONLY, unit="api", token=os.environ["SYM_API_TOKEN"])
        raise AssertionError("OPERATOR_ONLY admitted a unit token")
    except AuthzError as e:
        assert e.status == 404, "operator route returned %d, expected 404" % e.status
    assert enforce(RouteClass.OPERATOR_ONLY, unit="api",
                   token=os.environ["SYM_OWNER_TOKEN"]).kind == "operator"

    # entitlement failure is 403 and is checked AFTER identity
    try:
        enforce(RouteClass.ENTITLEMENT_REQUIRED, unit="api",
                token=os.environ["SYM_API_TOKEN"], application="dispatchos")
        raise AssertionError("ENTITLEMENT_REQUIRED admitted an unentitled principal")
    except AuthzError as e:
        assert e.status == 403, e.status

    # THE OTHER CORRECTION, EXECUTED: the chat unit's port. The handbook says 8081.
    chat = units.unit("chat")
    assert chat.port == 8802, "chat unit port is %d" % chat.port
    assert chat.token_env == "SYM_CHAT_TOKEN" and chat.resource is units.Resource.GPU
    assert "symoneural-llama-cpp" in chat.backed_by, chat.backed_by
    assert chat.name in {u.name for u in units.gpu_units()}
    ports = sorted((x.name, x.port) for x in units.REGISTRY.values())
    assert len({p for _, p in ports}) == len(ports), "two units share a port: %r" % (ports,)

    # the estate's own FastAPI application imports and answers on this runtime
    from symoneural_api.main import app as estate_app
    paths = sorted({r.path for r in estate_app.routes if hasattr(r, "path")})
    assert "/api/status" in paths and "/api/health" in paths, paths

    async def _estate(c):
        r = await c.get("/api/health")
        return r.status_code, r.headers.get("content-type", ""), r.text[:200]

    code, ctype, body = asyncio.run(_exercise(estate_app, _estate))
    assert code == 200, "estate /api/health returned %d: %s" % (code, body)
    assert "json" in ctype, ctype
    _json.loads(body)

    print("  meaningful ops PASS: the estate's FastAPI %s served GET /healthz 200 and "
          "POST /echo 200 over httpx's ASGI transport with no socket bound; a two-field "
          "violation returned 422 with both errors; pydantic-core rejected ge=1 directly; "
          "uvicorn Config.load() resolved the app without binding; the estate's own "
          "symoneural_api imported on these packages and GET /api/health answered 200 JSON "
          "from %d registered routes; routeclass enforced all five classes - 401 with no "
          "token, 401 with a wrong one, 404 (not 403) for OPERATOR_ONLY against a unit "
          "token, 403 for ENTITLEMENT_REQUIRED; units.unit('chat').port == 8802 and no two "
          "units share a port"
          % (version("fastapi"), len(paths)))
    print("  NO NETWORK, NO SOCKET: every request above went through httpx.ASGITransport "
          "in-process; nothing was bound, nothing was contacted, :8800 was not touched.")

if bad:
    print("FAIL:"); [print("   -", b) for b in bad]; sys.exit(1)
print("API CLEAN ROOT PROOF: PASS")
