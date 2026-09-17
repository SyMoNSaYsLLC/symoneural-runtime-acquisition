# Symoneural-API — current implementation (A0 capture, 2026-09-13)

Read from `Symoneural-API/app/` at estate HEAD after commit `fc813f711`. This is the
regression authority for the refactor toward `libsymoneural-api`: behaviour listed
here is preserved by the tests in `Symoneural-API/app/tests/` before any primitive
is extracted. Facts only; the target architecture is in `docs/api/ARCHITECTURE.md`.

## Files

| Path | Lines | Tracked | What |
|---|---|---|---|
| `symoneural_api/main.py` | 165 | yes | FastAPI app "SyMoNeuRaL DispatchOS"; routes below; `main()` runs uvicorn on `$SYMONEURAL_HOST:$SYMONEURAL_PORT` (127.0.0.1:8800) |
| `symoneural_api/routeclass.py` | 144 | yes | five route classes; `authenticate()`, `enforce()`, `classified()`; `Principal`; `AuthzError(status, detail)` |
| `symoneural_api/units.py` | 144 | yes | `Unit` dataclass; `REGISTRY` of 8 units; `unit()`, `gpu_units()`, `backing_packages()` |
| `symoneural_api/gpulock.py` | 171 | yes | file lock at `$SYM_GPU_LOCK` (default `/run/symoneural/gpu.lock`); `PRIORITY`; `Holder`; `current/acquire/release/hold` |
| `src/gpulock.c` + `include/symoneural/gpulock.h` | 288 + 78 | yes | same protocol in C; `sym_gpulock_{priority,path,current,acquire,release,strerror}` |
| `src/rack.c` + `include/symoneural/rack.h` | 173 + 62 | yes | `/proc` host state + `nvidia-smi` subprocess GPU state; JSON that refuses to truncate |
| `src/unit.c` + `include/symoneural/unit.h` | 213 + 89 | **no (untracked)** | unit supervisor: fork/exec, poll, stop; GPU lock before exec |

No build file, no tests existed before this capture. The C was compiled by hand
(`-std=c11 -Wall -Wextra -Werror`, commit `5052b4c4ff`).

## Python surface (`main.py`)

| Route | Class | Behaviour |
|---|---|---|
| `GET /api/status` | PUBLIC_BOOTSTRAP | per unit: `UNCONFIGURED` if `$<token_env>` unset; `OFFLINE` unless `$SYM_<UNIT>_ENABLED=1`; `BUSY` if it holds the GPU lock; `QUEUED` if GPU-class and another holds it; else `READY` |
| `GET /api/health` | PUBLIC_BOOTSTRAP | `{"status":"ready","uptime_s":…}` |
| `GET /api/operator/lock` | OPERATOR_ONLY | holder dict or null, `PRIORITY`, `lock_path` |
| `POST /api/operator/lock/release?unit=` | OPERATOR_ONLY | `gpulock.release(unit, force=True)` |
| `GET /api/unit/{name}` | ENTITLEMENT_REQUIRED, `application=name` | 404 for unknown unit **before** authentication; unit detail + principal kind |

Route-class semantics (`routeclass.enforce`): PUBLIC_BOOTSTRAP → no checks;
SHARED_AUTH → 503 if the unit's token is unprovisioned, else no identity;
otherwise `authenticate()`: 401 without a bearer, operator token (`$SYM_OWNER_TOKEN`)
checked first, then `$SYM_<UNIT>_TOKEN` → `unit:<name>` principal, else 401;
OPERATOR_ONLY → **404** (not 403) for a non-operator; ENTITLEMENT_REQUIRED → 500 if no
application named, 403 unless operator or entitled. Comparison is `hmac.compare_digest`.
Secrets are read from the environment only; missing means unconfigured.

Observed: `Principal.entitlements` is never populated by `authenticate()` — a unit
principal can only pass ENTITLEMENT_REQUIRED as an operator today. `/api/unit/{name}`
passes the **unit name as the application** — the application concept is conflated
with the unit; the generic registry (A10) must separate them.

## Unit registry (`units.py`)

`REGISTRY` (insertion order): ravencalc 8801 CPU · chat 8802 GPU · coder 8803 CPU ·
project 8804 CPU · streamer 8805 NET · remix 8806 NET · studio 8807 GPU · miner 8808
GPU (height 6) · **image 8809 GPU · sigils 8810 GPU**. Each carries `backed_by` (estate
package names), `token_env` (`SYM_<NAME>_TOKEN`), `enabled_variable`
(`SYM_<NAME>_ENABLED` unless overridden).
Names in `DECISIONS.md` §1 not in the registry: live, rack, exp, asic, voice, reinforce.
`gpu_units()` filters by resource; `backing_packages()` is the unit→package graph the API
uses to make "offline" checkable.

> **2026-09-17.** `image` and `sigils` were added when the Diffuse engine was built; both
> are backed by `symoneural-stable-diffusion-cpp`, and the priority table below already
> carried them. Their endpoints — `POST /v1/images/generations` and `/v1/images/edits` for
> `image`, and deliberately none for `sigils` — are in `docs/api/ENDPOINT-REGISTER.md`,
> which `tools/proofs/api.py` asserts against this registry inside the clean-root image.

## GPU lock — the C↔Python contract

Lock file JSON `{"unit":"<name>","pid":<int>,"since":<float epoch>}`; path from
`$SYM_GPU_LOCK` else `/run/symoneural/gpu.lock`. Both halves: `O_CREAT|O_EXCL`
creation, re-entrant for the same unit, stale holder (dead pid; EPERM counts as
alive) is **reaped** by `current()`, release refuses another unit's lock unless
`force`, corrupt file is treated as absent (fail toward an unlocked card), bounded
acquire (Python 30 s / 0.25 s poll; C `timeout_ms`, 250 ms poll), higher priority
**waits**, never preempts. Priorities duplicated in both languages: chat 100, image
100, sigils 90, studio 50, reinforce 50, miner 10, unknown 50. C `fsync`s the file;
Python does not. C caps unit name at 64.

## Unit supervisor (`unit.c`, untracked)

`sym_unit_start`: refuses `UNCONFIGURED` when `$<token_env>` is empty; GPU units
call `sym_gpulock_acquire(name, 30000)` **before** fork; child `setpgid(0,0)`,
resets SIGTERM/SIGINT/SIGPIPE, `execv(exec_path, argv)`, `_exit(127)` on failure.
`sym_unit_poll`: `waitpid(WNOHANG)`; `STARTING→READY` after surviving **2 s** (a
heuristic, no port probe); exit 0 → OFFLINE, non-zero → FAILED (`last_exit_code`),
signal → 128+sig, SIGTERM during STOPPING counts as clean; releases the GPU lock on
exit. `sym_unit_stop`: SIGTERM to the process group, 10 s grace (100 ms polls),
SIGKILL, force-release lock, returns −1 for the unclean path. `sym_unit_json`
refuses to truncate. `restart_count` is never incremented anywhere.

## Rack telemetry (`rack.c`)

`sym_rack_host`: `/proc/meminfo` (MemTotal, MemAvailable, SwapTotal, SwapFree),
`/proc/loadavg`, `/proc/stat procs_running`. **`threads_total` is declared in
`rack.h` and never set.** `sym_rack_gpu`: `popen("nvidia-smi --query-gpu=…")` — a
fixed string through `/bin/sh -c`; absence → `present=false`, rc −1. `sym_rack_json`
refuses to truncate. Verified on this host at commit time ("RTX 5070 Ti, 16303 MiB").

## Deviations from the reconstruction's target (to be resolved, not silently)

1. `popen()` in `rack.c` is a shell invocation — target forbids `/bin/sh -c`; use
   `posix_spawn` + pipe with an argv.
2. Priority table lives in two languages — target: one source (C ABI, Python reads).
3. `unit.c/unit.h` untracked — adopted by this capture (tests below), committed.
4. No library, no build file, no ABI version — targets A7.
5. `rack.h threads_total` unimplemented; `restart_count` unused.
6. Application/unit conflation in `/api/unit/{name}` — target A10 registry.

## Tests written by this capture

`Symoneural-API/app/tests/native/` (C, `make test`): gpulock acquire/busy/reentrant/
release-refusal/stale-reap/corrupt-as-absent/race (one winner among 6); unit
start/STARTING→READY/stop/unconfigured/exec-failure-127/GPU-lock-before-exec/json
non-truncation; rack host fields/JSON parse/non-truncation.
`Symoneural-API/app/tests/python/` (unittest): gpulock protocol incl. the C↔Python
file contract; registry invariants; route classes; FastAPI routes via TestClient.

## Status after A7–A13 (2026-09-14) — what changed since the A0 capture

Facts from disk; the proofs are `tools/api-clean-root-proof` and `tools/api-evidence`.

| A0 deviation | State | Evidence |
|---|---|---|
| 1. `popen()` in `rack.c` | RESOLVED | `spawn_first_line()`: fixed argv through `posix_spawnp`, stderr to `/dev/null`, reaped with `waitpid`; `grep popen src/` finds only the comment. `tests/native/test_rack` 11 checks. |
| 2. Priority table in two languages | RESOLVED | one table in C (`sym_gpulock_priority_table`), Python reads it through `symoneural_api.native` (`_load_priority()`), fallback only when the library is absent. |
| 3. `unit.c/unit.h` untracked | RESOLVED | committed; `tests/native/test_unit` 21 checks. |
| 4. No library, no build file, no ABI version | RESOLVED | `CMakeLists.txt`; `libsymoneural-api.so.1` (ABI 1.0.0 = 65536), `symoneural-api-util`; packaged by `meta-symoneural/recipes-api/symoneural-api` (symoneural-firstparty). |
| 5. `threads_total` unset; `restart_count` unused | threads_total RESOLVED (5th field of `/proc/loadavg`, in the JSON); `restart_count` still never incremented (no restart policy exists yet — NOT STARTED) | `test_rack` asserts `threads_total >= procs_running`. |
| 6. Application/unit conflation | RESOLVED | `applications.py` registry, `/api/apps`, `/api/apps/{id}`, `/api/apps/{id}/status`; DispatchOS is `apps/dispatchos.py`, page `/demo/dispatchos.html`. |

Packaging and clean-root proof (rootfs `symoneural-image-api-qemux86-64.rootfs-20260914061826`, rebuilt after the rack.c change; the earlier `...041440` rootfs predated it):
`symoneural-api 1.0.0-r0` (library: NEEDED = `libc.so.6` only), `symoneural-api-util`,
`symoneural-api-python 1.0.0-r0` (flit_core; RDEPENDS fastapi pydantic uvicorn symoneural-api).
In the extracted root through the target `ld.so` with `env -i`: 17 upstream imports PASS,
`pydantic_core 2.46.5`, util `version/abi/capabilities/selftest` PASS, ctypes lock
acquire/release PASS, `GET /api/apps` 200, `GET /api/apps/dispatchos/status` 200 →
`BLOCKED` (ravencalc absent, the honest answer for an API-only root). Artefacts:
`generated/evidence/api/` (§44).

The rack.c change was initially recorded here while only the SOURCE was fixed; the
packaged library still carried the old code. That gap is now closed and asserted
rather than described. `tools/api-clean-root-proof` reads the claim out of the
shipped library on every run:

| Assertion on the packaged artifact | Value |
|---|---|
| `SOURCE-TREE` shipped in the package equals `git rev-parse HEAD:Symoneural-API/app` | `898f4decdfc5…` — equal |
| `popen`/`pclose` imported by `libsymoneural-api.so.1` | **0** (required 0) |
| `posix_spawn*` imported | **6** (required > 0) |

A stale package now fails the proof by name instead of passing quietly. One item is
recorded NOT TESTED rather than claimed: `threads_total` is exercised by the C test
`tests/native/test_rack` on the host, but `symoneural-api-util` has no `rack`
subcommand, so it is not read back out of the shipped binary.

Still open for the API runtime: LICENSE for first-party code is undeclared (`CLOSED`);
clean A/B rebuild reproducibility NOT TESTED; `restart_count`/restart policy NOT STARTED.

## Second proof, in the shared harness (2026-09-17)

`tools/proofs/api.py` puts API in the same clean-root harness CLI, Common and Ravencalc
use: `tools/clean-root-proof API symoneural-image-api`, rc=0. It does not replace
`tools/api-clean-root-proof` (which passes, and is the only thing covering the native
library, the GPU lock and the applications registry) — the two are complementary:

| | `tools/api-clean-root-proof` | `tools/proofs/api.py` (shared harness) |
|---|---|---|
| upstream imports | yes | yes, **at exact pins** (fastapi 0.141.1, starlette 1.6.0, uvicorn 0.52.4, pydantic 2.13.5, pydantic-core 2.46.5, httpx 0.28.1) |
| native `libsymoneural-api.so.1`, GPU lock, applications registry | yes | no |
| host-leakage loader trace | no | yes — "none: no external library initialization" |
| a request actually served | `GET /api/apps`, `/api/health` through the app | the same, plus a fresh app served 200/200/422 over `httpx.ASGITransport`, and `uvicorn Config.load()` |
| route-class enforcement | no | 401 no token, 401 wrong token, **404** OPERATOR_ONLY vs a unit token, 403 ENTITLEMENT_REQUIRED |
| unit registry | no | `chat.port == 8802`; no two units share a port |

The exact-pin assertion exists so the API runtime and the 17 September reference-gateway
document cannot drift apart silently: that document's `file:line` citations were made
against these six versions, and if one moves the proof fails by name.

The route-class and port checks exist because three chat-output documents dated 16–17
September contradicted this file — they recorded 403 for operator routes and `:8081` for
chat. This file was right; the checks now execute the answer instead of asserting it.
Nothing is bound and `127.0.0.1:8800` is not contacted (R14).

Evidence: `generated/evidence/maintenance/2026-09-17-api-clean-root-proof.txt`.
