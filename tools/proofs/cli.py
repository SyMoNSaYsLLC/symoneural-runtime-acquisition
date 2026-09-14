"""CLI clean-root proof body: run INSIDE the extracted image by tools/clean-root-proof.

Imports the anthropic + mcp runtime closure, refuses build frontends, and performs one
meaningful operation per library. NOTHING here touches the network: the estate's product
is its own runtimes, so the Anthropic SDK is exercised as a local library (type
construction and serialisation), never by calling a hosted service.
"""
import importlib, os, sys
from importlib.metadata import version, PackageNotFoundError

# see tools/proofs/ravencalc.py: let anything that spawns re-enter the TARGET interpreter
_wrap = os.environ.get("SYM_TARGET_PYTHON")
if _wrap and os.path.exists(_wrap):
    import multiprocessing
    sys.executable = _wrap
    multiprocessing.set_executable(_wrap)

# module -> exact version a consumer pins, or None for "any installed"
want = {"anthropic": None, "mcp": None, "mcp_types": "2.2.0",   # mcp declares mcp-types==2.2.0
        "httpx2": None, "httpcore2": None, "truststore": None,
        "docstring_parser": None, "jiter": None, "sse_starlette": None,
        "multipart": None, "jwt": None, "cryptography": None, "cffi": None, "pycparser": None,
        "jsonschema": None, "attrs": None, "referencing": None,
        "jsonschema_specifications": None, "rpds": None,
        "opentelemetry": None, "pydantic": None, "starlette": None, "uvicorn": None}
dist = {"jwt": "pyjwt", "multipart": "python-multipart", "rpds": "rpds-py",
        "mcp_types": "mcp-types", "sse_starlette": "sse-starlette",
        "docstring_parser": "docstring-parser", "opentelemetry": "opentelemetry-api",
        "jsonschema_specifications": "jsonschema-specifications"}
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
    import json as _json

    # jiter: the Rust JSON parser anthropic streams responses through
    import jiter
    assert jiter.from_json(b'{"a":[1,2,{"b":null}],"c":true}') == {"a": [1, 2, {"b": None}], "c": True}

    # jsonschema: exercises attrs + referencing + rpds-py (the Rust structures) at once
    import jsonschema
    schema = {"type": "object", "required": ["n"], "properties": {"n": {"type": "integer", "minimum": 3}}}
    jsonschema.validate({"n": 7}, schema)
    try:
        jsonschema.validate({"n": 1}, schema); raise AssertionError("jsonschema accepted n=1 under minimum 3")
    except jsonschema.ValidationError:
        pass

    # pyjwt[crypto] over cryptography's Rust/OpenSSL binding, reached through cffi.
    # RS256 needs a real asymmetric key, so this exercises the native extension,
    # not pyjwt's pure-python HMAC path.
    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem_priv = key.private_bytes(serialization.Encoding.PEM,
                                 serialization.PrivateFormat.PKCS8,
                                 serialization.NoEncryption())
    pem_pub = key.public_key().public_bytes(serialization.Encoding.PEM,
                                            serialization.PublicFormat.SubjectPublicKeyInfo)
    tok = jwt.encode({"sub": "symoneural", "unit": "cli"}, pem_priv, algorithm="RS256")
    assert jwt.decode(tok, pem_pub, algorithms=["RS256"])["sub"] == "symoneural"
    try:
        jwt.decode(tok[:-4] + "AAAA", pem_pub, algorithms=["RS256"])
        raise AssertionError("a tampered RS256 token verified")
    except jwt.InvalidTokenError:
        pass

    # python-multipart: parse a real multipart body through parse_form, the entry
    # point Starlette (and therefore the MCP HTTP transport) actually calls
    import io
    from python_multipart import parse_form
    body = b"--X\r\nContent-Disposition: form-data; name=\"unit\"\r\n\r\nravencalc\r\n--X--\r\n"
    fields = []
    parse_form({"Content-Type": b"multipart/form-data; boundary=X",
                "Content-Length": str(len(body)).encode()},
               io.BytesIO(body), lambda f: fields.append((f.field_name, f.value)), lambda f: None)
    assert fields == [(b"unit", b"ravencalc")], fields

    # httpx2 + httpcore2 + truststore: build a request WITHOUT sending it. No network.
    import httpx2
    req = httpx2.Request("POST", "https://symoneural.invalid/api/apps", json={"id": "dispatchos"})
    assert req.method == "POST" and req.url.host == "symoneural.invalid"
    assert _json.loads(req.content)["id"] == "dispatchos"

    # anthropic SDK as a LOCAL library: the client is constructed and a request is
    # BUILT, never sent. SyMoNeuRaL's own runtimes are the product; this SDK is a
    # protocol/type dependency of the CLI, not an inference backend.
    import anthropic
    client = anthropic.Anthropic(api_key="not-a-real-key", base_url="http://127.0.0.1:1")
    built = client._build_request(anthropic._models.FinalRequestOptions.construct(
        method="post", url="/v1/messages",
        json_data={"model": "local", "max_tokens": 16,
                   "messages": [{"role": "user", "content": "ping"}]}))
    assert built.method == "POST" and "/v1/messages" in str(built.url)
    assert _json.loads(built.read())["messages"][0]["content"] == "ping"

    # mcp + mcp-types: build and round-trip a protocol message through pydantic
    import mcp.types as mt
    init = mt.InitializeRequest(
        method="initialize",
        params=mt.InitializeRequestParams(
            protocolVersion=mt.LATEST_PROTOCOL_VERSION,
            capabilities=mt.ClientCapabilities(),
            clientInfo=mt.Implementation(name="symoneural-cli", version="1.0.0")))
    wire = init.model_dump_json(by_alias=True, exclude_none=True)
    back = mt.InitializeRequest.model_validate_json(wire)
    # the field is client_info in Python and clientInfo on the wire; check BOTH, since
    # the alias is the part the protocol actually depends on
    assert '"clientInfo"' in wire and '"protocolVersion"' in wire, wire
    assert back.params.client_info.name == "symoneural-cli", wire

    # opentelemetry-api: a real span through the API surface
    from opentelemetry import trace
    with trace.get_tracer("symoneural.cli").start_as_current_span("proof") as span:
        assert span is not None

    # sse-starlette: construct the response type the MCP transport streams over
    from sse_starlette.sse import EventSourceResponse
    async def _gen():
        yield {"data": "ok"}
    assert EventSourceResponse(_gen()).status_code == 200

    # docstring-parser: what the anthropic SDK uses to turn tool functions into schemas
    import docstring_parser
    parsed = docstring_parser.parse("Do a thing.\n\nArgs:\n    unit: which unit\n")
    assert parsed.short_description == "Do a thing." and parsed.params[0].arg_name == "unit"

    print("  meaningful ops PASS: jiter parsed nested JSON; jsonschema accepted/rejected "
          "against minimum (attrs+referencing+rpds-py); pyjwt RS256 signed and verified over "
          "cryptography's Rust/OpenSSL binding via cffi and rejected a tampered token; "
          "python-multipart parsed a form part; httpx2 built a POST (unsent); anthropic SDK "
          "built a /v1/messages request locally, never sent; mcp InitializeRequest round-tripped "
          "through mcp-types/pydantic; opentelemetry span; sse-starlette EventSourceResponse 200; "
          "docstring-parser parsed an Args block")
    print("  NO NETWORK: every operation above is local construction, parsing or crypto; "
          "no request is sent and no hosted model is contacted.")

if bad:
    print("FAIL:"); [print("   -", b) for b in bad]; sys.exit(1)
print("CLI CLEAN ROOT PROOF: PASS")
