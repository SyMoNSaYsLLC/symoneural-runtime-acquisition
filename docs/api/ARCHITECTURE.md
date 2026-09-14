# Symoneural-API architecture (target, reconstruction v1.1)

```
first-party UI  ──►  /demo/<app>.html  ──►  GENERIC APPLICATION API  (/api/apps/<id>/…)
                                                    │
                                        Python API layer (FastAPI)
                                        ├─ routeclass   five route classes, HMAC tokens, fail-closed
                                        ├─ units        registry: 8 units → resource, port, backing packages
                                        ├─ applications registry: definitions, DemoPolicy, derived readiness
                                        ├─ apps/        one module per application (DispatchOS is one)
                                        ├─ gpulock      Python side of the lock protocol (fallback + policy)
                                        └─ native       ctypes → libsymoneural-api (ABI major-checked)
                                                    │
                                        libsymoneural-api  (C17, libc/POSIX only)
                                        gpu lock · unit supervisor · rack telemetry · capabilities
```

Boundaries: Python owns HTTP, schemas, applications, policy, accounts, SMTP and
high-level authorisation; C owns platform primitives with a stable ABI. Native
code names no application, route, page or customer (tested). Inference is a
separate native domain (`libsymoneural-llm`); the two compose above the native
boundary and are never merged.

Runtime closure: 6 direct upstream Python packages + 11 runtime dependencies =
17 upstream runtime sources, derived from wheel METADATA on every run
(`tools/check-python-runtime-closures.py --runtime API`: PASS) and encoded as
recipe RDEPENDS; `packagegroup-symoneural-api` is the deployable surface;
`symoneural-image-api` + `tools/api-clean-root-proof` prove a clean root.

Documents: CURRENT-IMPLEMENTATION.md (A0 baseline), C-ABI.md, APPLICATIONS.md,
SECURITY.md, ../apps/APPLICATION-MODEL.md, ../apps/DISPATCHOS-DEMO.md.
