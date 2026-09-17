# Endpoint register — every documented surface, and who owns it

**17 September 2026.** One list. For each endpoint: which namespace it belongs to, which
unit answers it, what credential it needs, and whether it is **BUILT**, **DESIGNED** or
**RESERVED**. The rule this register exists to enforce:

> **Nothing is built without an assigned endpoint, and no endpoint is listed without a
> state.** A route with no unit is a design note; a unit with no route cannot be reached.

Sources, all read rather than recalled:
`~/Desktop/claude/claude-2026-09-17-api-tree-concrete.md` (the nine rules and the frozen
tree), `~/Downloads/SyMoNeuRaL-Inference-Report-2026-09-16.md` §7 (the 45-entry tree and
its rationale), `~/Desktop/claude/claude-2026-09-17-api-rebrand-map.md` (FreeToken's
surface and where each verb lands), and the three worker sources at their estate pins.

---

## 1. Three namespaces, no bleed

| Namespace | What it is | Credential |
|---|---|---|
| `/health` `/ready` `/version` `/metrics` | bare operational probes at root | `pub` / `client` / `op` |
| `/v1/*` | **dialects verbatim** — OpenAI and Anthropic in their exact shapes, so unmodified SDKs and Claude Code work with no shim | client key |
| `/symoneural/v1/*` | everything first-party: status, capabilities, registry, requests, jobs, GPU, admin | client key or operator token |
| `/api/*` | **RESERVED for the Ollama dialect, verbatim, if it is ever built.** No native route may live here. | — |

`/api/*` is reserved because Ollama's native surface *is* `/api/*` (`server/routes.go`
@ `5ed8dde3`: `/api/chat` 1897, `/api/tags` 1875, `/api/ps` 1895) and its OpenAI shim is
`/v1/*` rewritten into the same handlers. The estate's live `/api/status` and `/api/chat`
collide with Ollama's by name — which is exactly why the namespace is being vacated.

**One canonical path per operation.** Workers register the same handler at several paths
(llama-server registers `/chat/completions` *and* `/v1/chat/completions`,
`tools/server/server.cpp:256-257` @ `5266f24d`). That is the worker's business. The
gateway exposes one path, and an alias is added only for a named client with a reproduced
failure.

---

## 2. Worker surfaces — what each engine actually serves

These are **not** the estate's endpoints. They are the provider-shaped surfaces the
gateway talks *to*, bound on loopback at an ephemeral port chosen by the supervisor, never
forwarded. Each row was read from source at the estate's pin.

### 2.1 `symoneural-llama-cpp` — llama-server b10809 (`5266f24da75d`)

| Route | Line | Gateway use |
|---|---|---|
| `GET /health` | `server-http.cpp:253-269` | the only readiness signal; 503 `Loading model` until `is_ready` |
| `GET /v1/models` | `server.cpp:246` | id = `--alias <registry id>` (rule 6) |
| `POST /v1/chat/completions` | `server.cpp:257` | pass-through with policy |
| `POST /v1/completions` | `server.cpp:255` | pass-through |
| `POST /v1/responses` | `server.cpp:259` | pass-through |
| `POST /v1/messages` · `/v1/messages/count_tokens` | `server.cpp:263,280` | pass-through |
| `GET /metrics` | `server.cpp:249` | scraped, not forwarded |
| `POST /tokenize` · `/detokenize` | `server.cpp:272-273` | backs `/symoneural/v1/tokenize` |
| `GET /props` | README 895–918 | the capabilities document |

### 2.2 `symoneural-stable-diffusion-cpp` — sd-server at `7f410a3793c5` — **NEW, 17 Sep**

Read from `examples/server/routes_*.cpp` in the pristine tree. Three dialects in one
binary:

| Dialect | Routes |
|---|---|
| **OpenAI** | `POST /v1/images/generations` · `POST /v1/images/edits` · `GET /v1/models` |
| **A1111 / `sdapi`** | `POST /sdapi/v1/txt2img` · `POST /sdapi/v1/img2img` · `GET /sdapi/v1/samplers` · `/schedulers` · `/sd-models` · `/loras` · `/upscalers` · `/options` · `/latent-upscale-modes` |
| **sd.cpp native** | `GET /sdcpp/v1/capabilities` · `POST /sdcpp/v1/img_gen` · `POST /sdcpp/v1/vid_gen` · `GET /sdcpp/v1/jobs/{id}` |

Only the OpenAI dialect is projected to the gateway (§3). `sdapi/*` and `sdcpp/*` are the
worker's business under rule 2 — the same treatment llama-server's unprefixed aliases get.

**The estate does not run sd-server.** `symoneural-stable-diffusion-cpp-server` is a
separate package and no image installs it; the image unit invokes `sd-cli` per render.
These routes are recorded because they are the reference for what the gateway's image
route must accept and return, and because if a long-lived image worker is ever wanted,
this is the surface it would present.

### 2.3 `symoneural-freetoken` — FreeToken 0.1.3 (`cac247a860e3`)

Worker contract rows (`server/api_server.py`, `openai_api.py`, `anthropic_api.py`,
`responses_api.py`): `POST /v1/chat/completions` :118 · `/v1/completions` :126 ·
`GET /v1/models` :134 · `POST /v1/messages` :83 · `/count_tokens` :93 · Responses trio
:116,134,138 · `GET /health` :57 · `/v1/requests` :63 · `/v1/stats` :71 ·
`POST /v1/cache/rebuild` :572 · `GET /v1/cache/status` :813 · `POST /generate` :823.

FreeToken's **daemon** (`daemon/app.py`) is a second control plane and is **dropped, not
rebranded** — `symoneural-api` is the supervisor. Its four features without an estate
equivalent get routes: `/bench/run` and `/bench/profile` → `/symoneural/v1/gpu/bench` and
`/gpu/profile`; `/engine/logs` → `/symoneural/v1/models/{id}/log`; cache geometry →
`/symoneural/v1/models/{id}/cache`.

---

## 3. The gateway tree — assignment and state

`pub` = no auth (`PUBLIC_BOOTSTRAP`) · `client` = client key
(`AUTHENTICATED_APPLICATION`) · `op` = operator token (`OPERATOR_ONLY`) · `→job` = `202`
plus `{id, status_url}`.

**State** is against disk, not against intent:
**BUILT** = a handler answers today · **DESIGNED** = in the frozen tree, no handler ·
**RESERVED** = namespace held, nothing planned.

### 3.1 Root probes

| Endpoint | Class | Unit | State |
|---|---|---|---|
| `GET /health` | pub | api | DESIGNED — today's equivalent is `GET /api/health`, BUILT |
| `GET /ready` | pub | api | DESIGNED |
| `GET /version` | client | api | DESIGNED |
| `GET /metrics` | op | api | DESIGNED |

### 3.2 `/v1/*` — dialects

| Endpoint | Class | Unit | Worker | State |
|---|---|---|---|---|
| `GET /v1/models` · `GET /v1/models/{model}` | client | api | llama-server, sd-server | DESIGNED |
| `POST /v1/chat/completions` | client | **chat** :8802 | llama-server | DESIGNED |
| `POST /v1/completions` | client | chat | llama-server | DESIGNED |
| `POST /v1/responses` · `/{id}` · `/{id}/cancel` | client | chat | llama-server | DESIGNED |
| `POST /v1/embeddings` | client | chat | llama-server | DESIGNED — 404 in the OpenAI envelope unless `capabilities.embeddings` |
| `POST /v1/messages` · `/v1/messages/count_tokens` | client | chat | llama-server | DESIGNED |
| **`POST /v1/images/generations`** | client | **image** | **sd-cli** | **DESIGNED — worker BUILT 17 Sep** |
| **`POST /v1/images/edits`** | client | **image** | **sd-cli** | **DESIGNED — added to the tree 17 Sep (§5)** |

### 3.3 `/symoneural/v1/*` — first-party

| Endpoint | Class | Unit | State |
|---|---|---|---|
| `GET status` | client | api | DESIGNED — today `GET /api/status`, BUILT |
| `GET capabilities` | client | api | DESIGNED — gains an `image` block (§5) |
| `POST generate` · `tokenize` · `detokenize` | client | chat | DESIGNED |
| `GET requests` · `requests/{id}` · `POST requests/{id}/cancel` | client/op | api | DESIGNED |
| `GET models` · `GET models/{id}` | client | api | DESIGNED |
| `POST models` · `DELETE models/{id}` | op | api | DESIGNED |
| `POST models/{id}/activate` · `deactivate` · `verify` → job | op | api | DESIGNED |
| `POST downloads` → job | op | api | DESIGNED — the only route that touches the network; allow-listed; writes to the external store |
| `GET jobs` · `jobs/{id}` · `POST jobs/{id}/cancel` | op | api | DESIGNED |
| `GET gpu` · `POST gpu/release` | op | api | DESIGNED — today `GET /api/operator/lock` and `POST /api/operator/lock/release`, BUILT |
| `GET units` · `units/{name}` | op | api | DESIGNED — today `GET /api/unit/{name}`, BUILT |
| `GET apps` · `apps/{id}` · `apps/{id}/status` | client | api | DESIGNED — today `GET /api/apps*`, BUILT |
| `POST admin/drain` → job · `POST admin/resume` | op | api | DESIGNED |
| `GET usage` | op | api | DESIGNED |
| `GET events` | op | api | DESIGNED — SSE, replaces polling |
| `POST gpu/bench` → job · `GET gpu/profile` | op | fabric | DESIGNED — from FreeToken's `/bench/*` |
| `GET/POST models/{id}/cache` → job | client/op | fabric | DESIGNED — from FreeToken's cache geometry |
| `PATCH models/{id}` · `GET models/{id}/log` | op | api | DESIGNED |

### 3.4 `/api/*`

| Endpoint | State |
|---|---|
| `GET /api/status` `/api/health` `/api/unit/{name}` `/api/apps` `/api/apps/{id}` `/api/apps/{id}/status` `/api/operator/lock` `POST /api/operator/lock/release` | **BUILT** — the eight routes `symoneural_api.main` serves today |
| everything else under `/api/` | RESERVED for the Ollama dialect |

On the new instance these eight answer **410 Gone** with `{"see": <new path>}` for one
release. **`127.0.0.1:8800` is untouched (R14)** — it keeps serving them.

---

## 4. What is actually served today

Eight routes, all `/api/*`, in `Symoneural-API/app/symoneural_api/main.py`:

```
GET  /api/status             :52      GET  /api/unit/{name}            :130
GET  /api/health             :91      GET  /api/apps                   :172
GET  /api/operator/lock      :100     GET  /api/apps/{application_id}  :191
POST /api/operator/lock/release :111  GET  /api/apps/{id}/status       :198
```

Forty-five entries designed, eight built, and the eight that exist are in the namespace
the design reserves for someone else. That is the honest state; it is not a defect
introduced today, and nothing in this register changes a handler.

---

## 5. New assignments — 17 September 2026

The Diffuse engine was built today (`sd-cli`, Phase 14a). Under the rule at the top of
this file it does not get to exist without an endpoint:

| What was built | Assigned endpoint | Unit | Notes |
|---|---|---|---|
| `sd-cli` text→image | `POST /v1/images/generations` | `image` (GPU, priority 100) | Already in the frozen tree as *"P2 — image worker"*. The worker now exists, so the row moves from *no worker* to *worker built, gateway handler not written*. |
| `sd-cli` image→image | `POST /v1/images/edits` | `image` | **Added to the tree today.** sd-server exposes it at the pin; OpenAI's dialect defines it; it costs no new namespace. |
| — | `GET /symoneural/v1/capabilities` gains `image:{available, model, sizes, steps, cfg}` | api | Rule 8: capabilities are declared, not probed. A UI must not discover that images are unavailable by failing a render. |
| `sigils` surface | **none yet, and deliberately none** | `sigils` (GPU, priority 90) | `sigils` has no recorded definition anywhere in the repository (`docs/diffuse/ARCHITECTURE.md` §1). It gets a port and a priority, not a route, until it has a purpose. Assigning it `/v1/images/generations` with a different model would be inventing the product. |

Two ports follow from `units.py`, which allocates 8801–8808 today: **image 8809**,
**sigils 8810**. `tools/proofs/api.py` already asserts no two units share a port.

---

## 6. The check, so this file cannot rot

`Symoneural-API/app/symoneural_api/endpoints.py` carries this register as data, and
`tools/proofs/api.py` executes three assertions against it inside the clean-root image:

1. every endpoint names a unit that exists in `units.REGISTRY`;
2. every endpoint carries a `RouteClass`, because rule 3's default is deny and an
   unclassified route is a bug, not a public one;
3. **every GPU unit that has a backing package has at least one endpoint** — the
   mechanical form of "nothing is built without an assigned endpoint".

Assertion 3 is the one that would have caught today's gap: `image` had a priority, a
worker under construction and no route.
