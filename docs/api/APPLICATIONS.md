# API applications namespace

See `docs/apps/APPLICATION-MODEL.md` for the model. Routes:

| Route | Class | Returns |
|---|---|---|
| `GET /api/apps` | PUBLIC_BOOTSTRAP | every application's public descriptor; `?page=/demo/x.html` resolves a page to its application (404 if none) |
| `GET /api/apps/{id}` | by application mode | the public descriptor |
| `GET /api/apps/{id}/status` | by application mode | derived readiness: READY / DEGRADED / BLOCKED, blocking/degraded units, per-unit reasons |

The installed-package set comes from `$SYM_OPKG_STATUS` (default
`/var/lib/opkg/status`); when absent it is *unknown* and readiness is BLOCKED
with that reason — a demo cannot look green by accident.
