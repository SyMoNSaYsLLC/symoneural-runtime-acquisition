# DispatchOS — the first application (a demo, not the platform)

Definition: `Symoneural-API/app/symoneural_api/apps/dispatchos.py`.

| | |
|---|---|
| application_id | `dispatchos` |
| mode | demo (public) |
| API namespace | `/api/apps/dispatchos` (generic; descriptor, status) |
| page | `/demo/dispatchos.html` → public URL `symoneural.com/demo/dispatchos.html` (UI runtime, Phase 15d) |
| required units | `ravencalc` (CPU) |
| optional units | `chat` (GPU) — the page degrades when the LLM backend is not installed |
| capabilities | unit-status, gpu-lock-status, ravencalc-compute |
| policy | no mutations, 30 req/min, 4 sessions, 900 s, tools {read_status}, admin never |

Status today (`tools/map-api-runtime.py`, `GET /api/apps/dispatchos/status`):
**BLOCKED** — ravencalc's backing packages are not installed on any clean target
yet (Ravencalc image build pending) and no unit token is provisioned in a test
environment; chat is DEGRADED (llama backend unpackaged). This is the honest
state the reconstruction requires: a visible page without a working backing
package is not completion.

What DispatchOS is **not**: the homepage, the site architecture, the API
architecture, the UI runtime, tenancy, or anything in C. The generic modules are
tested to contain no `dispatchos` string.
