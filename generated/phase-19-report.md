# PHASE 19 — Tune, Remix, Adaptive-Fabric, contract freeze, estate closure

## STATUS: PENDING — NOT STARTED

**starts after: Phases 15, 16 and 18 gates**

> **ORDERING (O1).** Each phase's own "Start after" line is authoritative. The
> QUEUED headers' serial chain was a paste convenience and is **WITHDRAWN**.
> Dependency graph:
>
> ```
> 10 → 11 → { 11-T, 18 }
> 11 → 12 → { 13, 14, 17 }
> 13 → 16          14 → 15          { 15, 16, 18 } → 19
> ```
>
> Builds run **concurrently in separate build dirs** when dependencies are met
> (R3', R6'). GPU PROOF steps (12f, 13e/13f, 14e, 16 runs, 17e) execute **one at a
> time through the governor** — train is never evicted, so a 13e run finishes
> before 14e's contention test starts.


Queued 2026-09-13 by Garrett with "QUEUED — do not start." Spec verbatim below.
Nothing acquired, built, tagged or frozen. Per A7, `nvidia-ml-py`, `cupy` and
`cuda-python` have NOT been fetched.

Milestone: the card is a managed device on the bus, every shipped recipe compiles
with the network off, the API is frozen at v1 for the native clients, and the
estate is tagged.

---

## SETTLED

- **S1** Tune: telemetry and power limits via **NVML now**; fan and clock
  **deferred**.
- **S2** Remix: official **Spotify Web API over OAuth PKCE (httpx)** for library,
  search, playlists, playback control; `librespot` an **optional** personal-device
  Connect daemon with its terms caveat on the page; audio-features, analysis and
  recommendations **not used**. Credentials are SET in `spotify.env` (app
  "SyMoNeuRaL Remix", redirect `https://symoneural.com/api/remix/callback`).
- **S3** FreeToken tested **unmodified** on Common's torch 2.14; if it does not
  run, Adaptive-Fabric is **DEFERRED with evidence**.
- **S4** Offline proven by `BB_NO_NETWORK = "1"` from a **clean TMPDIR** after
  fetch.
- **S5** Acquire here (A7): `nvidia-ml-py` (PyPI sdist sha256), `cupy`,
  `cuda-python` (licence characterised from its tree).

## ITEMS

- **19a** Tune: telemetry daemon at 1 Hz → bus frames; footer reads **only** from
  it; power-limit helper with a sudoers rule **restricted to the NVML set call**;
  kernel lab (NVRTC engine + 34-sample curriculum) packaged as
  `symoneural-kernel-lab`, tests run, results to receipts **labelled measured**.
- **19b** Remix per S2 in `Symoneural-API/app/remix`; tokens **encrypted at rest**
  under `/etc/symoneural`; Chat proposes, the API writes the playlist.
- **19c** FreeToken per S3; outcome recorded **either way**.
- **19d** API v1: `/openapi.json` exported to
  `meta-symoneural/api/openapi-v1.json`; conformance test **fails the build on
  drift**; CHANGELOG rule **additive-only**.
- **19e** Offline proof for `packagegroup-symoneural-rack` per S4; **every network
  reach recorded as a defect and fixed in the recipe**.
- **19f** `TEMPLATECONF` for `meta-symoneural`; a `symonbuild` launcher that sets
  the environment and invokes the **pinned** BitBake; regenerate the report; tag
  `estate-v0.1` naming every phase commit.

## GATE

19e passes for **every shipped recipe**; 19d green; footer agrees with
`nvidia-smi` for 60 s; `symonbuild` builds the rack; tag placed (**no remote**).

## COMMIT

`phase 19: Tune on the bus; Remix on the Web API; FreeToken outcome; API v1 frozen; offline proof; symonbuild; estate-v0.1`

## RETURN

- ACQUIRED three: tag → SHA, licences as read
- TUNE fields and agreement; power round trip; kernel tests passed / total
- REMIX OAuth round-trip, playlist written
- FABRIC RUNS / DEFERRED (evidence); API openapi-v1 sha256, conformance green
- OFFLINE proven / total, reaches fixed; ESTATE `symonbuild` works, tag SHA
- DECISIONS FOR GARRETT: none

---

## NOTES CARRIED IN FROM EARLIER PHASES

### 19e is where the scoped offline claim gets settled

`offline-compile` is recorded in `acquisition/unresolved.json` as
**RESOLVED-SCOPED**, and 19e is the phase that closes it properly. The history
matters, because the existing numbers must not be reused:

* Phase 5 proved it on `symoneural-stratum` — `--runall=fetch` rc=0, then
  `BB_NO_NETWORK=1` → `do_compile` **Succeeded**, **0** NetworkAccess denials,
  **102 rlibs**, across rust 1.98.1 + LLVM 23 + 233 `crate://` entries.
* **That run predates `symoneural-pristine`.** The class as first written set
  `do_fetch[noexec] = "1"`, which silently starved every `crate://` entry — the
  vendor directory held **0 crates** and cargo failed with a misleading
  "no matching package named `bitcoin`". Fixed by stripping only the upstream
  `git://` URI at parse time and letting `do_fetch` run; vendored went **0 → 183**.

So the offline guarantee has **never been reproduced under the class the estate
ships**. 19e must re-prove it from scratch. Do **not** cite the Phase 5 figures as
current.

S4's "clean TMPDIR" is the right strictness: a warm `downloads/` makes an offline
fetch pass and proves nothing. This was observed directly in Phase 10 — an offline
`-c fetch` on stratum returned **rc=0** purely because 183 crate tarballs were
already cached.

**N3(c) already helps here.** `symoneural-pristine` now fails at unpack time if a
`crate://` recipe's vendor directory is empty, so the failure 19e is hunting
surfaces at its cause rather than several tasks later.

### 19a

`SYM_RACK_TOKEN` and `SYM_ASIC_TOKEN` are `set`. The GPU is an RTX 5070 Ti
(Blackwell, **sm_120**), driver 615.71.09, CUDA 13.4. Per Phase 12's S1 the estate
builds CUDA as a binary recipe and **never uses the host's nvcc** — 19a's NVML
work should draw from the estate toolkit on the same rule. S5's `nvidia-ml-py` is
NVIDIA's own BSD binding, deliberately **not** the third-party `pynvml`.

### 19b

All three `spotify.env` keys are `status: set` — `SPOTIFY_CLIENT_ID`,
`SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI`. The manifest lists the first two
under `units_that_stay_off_until_set` for "Remix", but since both are set, **Remix
is not held off**. `symoneural-librespot` already exists as a recipe at PV
**0.8.0**; S2 makes it optional, which is the right posture given its terms
caveat. `symoneural-httpx` (PV 0.28.1) builds clean, so S2's HTTP client is ready.

### 19c

`FreeToken/torch` is one of the **6 remaining open** control-plane decisions
(`[ARCHITECTURE] FreeToken/torch — blocks: Adaptive-Fabric build design`). S3
resolves it by **experiment rather than argument**: run it unmodified on torch
2.14 and record the outcome either way. `symoneural-freetoken` exists at PV
**0.1.2**; `symoneural-pytorch` at PV **2.14.0**.

### 19f

The tag must name every phase commit. Phase 10's are `86c0f5e`
("phase 10f: parity rebuild, setuptools-scm defect fixed in the class") and
`685203e` ("phase 10: four class defects fixed, real PV across the estate,
R12' stratum"). `symonbuild` must invoke the **pinned** BitBake at
`~/symoneural-bootstrap-master` — the same bootstrap the whole estate uses, which
per R-rules is read but never modified except the D1 clone.
