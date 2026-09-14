# The application model (A10)

An **application** is a customer-facing composition of platform capabilities. It
is a Python-layer concept (`Symoneural-API/app/symoneural_api/applications.py`);
the native libraries never see it, and adding one never edits C.

```
ApplicationDefinition
  application_id     ^[a-z][a-z0-9-]{1,39}$          -> api_namespace /api/apps/<id>
  display_name
  mode               demo | customer | internal      -> route class of the namespace
  required_units     must resolve in units.REGISTRY  -> readiness BLOCKED if unmet
  optional_units     may be absent                   -> readiness DEGRADED if unmet
  allowed_models     what the policy may select (browser-visible names only)
  capabilities       declarative, generic
  public_demo        True => page + DemoPolicy mandatory, expose_admin forbidden
  page               /demo/<id>.html (must equal the id)
  policy             DemoPolicy: allowed_models/units, allow_mutations=False,
                     max_requests_per_minute, max_concurrent_sessions,
                     session_lifetime_s, tool_capabilities, expose_admin=False
```

Registration (`register`) validates: unique id, valid units, no unit both
required and optional, page ↔ id consistency, policy present for public demos,
policy units ⊆ declared units, admin never exposed, page not already mapped.
`to_public()` is the browser-safe descriptor: no filesystem paths, secrets,
service names or model paths — enforced by test.

**Readiness is derived** (`readiness()`): for each unit — backing packages
present in the installed set (opkg status; *unknown* never counts as installed),
token provisioned, unit enabled. READY / DEGRADED / BLOCKED with the reason per
unit, so a page can degrade honestly and the API never returns a vague 500.

**Route class by mode** (`route_class_for`): demo → PUBLIC_BOOTSTRAP at the
namespace root (readiness/descriptors; the DemoPolicy governs everything
further), customer → ENTITLEMENT_REQUIRED, internal → OPERATOR_ONLY.

Namespace (`main.py`): `GET /api/apps[?page=]`, `GET /api/apps/{id}`,
`GET /api/apps/{id}/status`. Application-specific APIs live under the same
namespace as the application's own module adds them.

Adding a demo: `symoneural_api/apps/<id>.py` registering one definition, plus
first-party page content for the UI runtime to generate `/demo/<id>.html`.
Nothing else. Tests: `tests/python/test_applications.py` (generic first, one
application's tests separately) and `test_no_customer_name_in_generic_code`.
