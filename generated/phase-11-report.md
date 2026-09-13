# PHASE 11 — RavenCalc 6/6 live from estate binaries; the current deployment located

## STATUS: NOT STARTED — blocked on the Phase 10 gate

**starts after: Phase 10 gate** (the phase's own line; authoritative per O1)

Authoritative body re-pasted 2026-09-13 after compaction; supersedes any summary.
**11b amended per O2.** Nothing in this phase has been started.

Milestone: scipy and scikit-learn build with the Fortran toolchain and the control
plane serves the RavenCalc row from the estate's own Python sysroot — **no GPU, no
lock**.

---

## SETTLED

- **S1** DispatchOS's CONTRACT carries forward; the code is rebuilt incrementally.
  Schema `{id,label,slot,state ready|busy|queued|offline,bus gpu|cpu|asic|net,
  href,spec,detail,sub}`; frames `welcome, rack, patch, bus, chat/delta/done,
  calc.result, pong, error`; per-job lock; holder `"<surface> <pid>"`;
  `ACQUIRE_TIMEOUT 300 s`; `DRAIN_FLOOR 1500 MiB`.
- **S2** The unit list is the one served on `127.0.0.1:8800` **TODAY** (it includes
  Streamer, Live, DispatchOS; the August tarball is history). `units.json` is
  written from it.
- **S3** The serving interpreter is **the estate's python3**.
- **S4** **R14: `:8800` is read-only. Capture by reading; never start, stop or
  edit it.**

## ITEMS

- **11a** Locate the current deployment: `systemctl cat symoneural-api` and the
  process on `:8800` → `WorkingDirectory`. Copy its units list, page assets
  (HTML/CSS/JS) and generators into `Symoneural-UI/app/` and `units.json`;
  **never modify the running deployment (R14)**. Record its git HEAD if it has one.
- **11b** scipy: `DEPENDS python3-pybind11-native python3-cython-native
  symoneural-numpy python3 gfortran-cross`; `inherit pkgconfig`; PEP517
  config-settings `setup-args=-Duse-pythran=false` (**pythran unavailable in any
  layer, optional upstream — record it**). scikit-learn: `symoneural-numpy
  symoneural-scipy`.
- **11c** `Symoneural-API/app/`: FastAPI app with `GET /api/status`, `WS /api/ws`,
  `POST /api/ravencalc`; `units.json` from 11a; contract tests for **every** frame
  and state transition; `GpuQueue` behind an interface.
- **11d** `symoneural-dispatch` recipe; `packagegroup-symoneural-rack`; install to
  `Symoneural-API/prod` via the package feed.
- **11e** `symoneural-dispatch.service` (`User=google`, `ExecStartPre` releases
  locks, `ExecStopPost` kills engines, `MemoryMax 24G`, moderate hardening,
  `EnvironmentFile=/etc/symoneural/api.env`) on
  `127.0.0.1:8801` while the current deployment keeps `:8800` — **no cutover in
  this phase**.
- **11f** Proof: `sys.executable`, `fastapi.__file__`, `scipy.__file__` all under
  `Symoneural-API/prod/`.
- **11g** Acquire pydantic/pydantic-core under A7 at the version pydantic's tag
  pins (**`core-v2.46.5`**); `python_maturin`; crate closure tracked; RDEPENDS from
  `symoneural-pydantic`. **`import pydantic` from the estate python must succeed.**
- **11h** Write `acquisition/provider-decisions.json` (D2) and wire the scanners to
  merge it; close `direct-vs-oe-core`.
- **11i** openblas `LICENSE = "BSD-3-Clause AND LicenseRef-netlib-BLAS"` with the
  custom licence file; close `symoneural-openblas`. Close `scipy-fortran` on 11b's
  success, provenance as ACCEPTED-HISTORICAL.
- **11j** Adopt `symoneural-secrets` source into `meta-symoneural/tools/` with a
  recipe; add `--tenant NAME` (R13/R15).

## GATE

Ravencalc **6/6** images; `/api/ravencalc` on `:8801` solves an integral and an
eigenproblem (**scipy path**); WS `rack` frame delivered; 11f holds; **11g import
succeeds**; **open decisions at 1** (FreeToken, owned by Phase 19); clean.

## COMMIT

`phase 11: Ravencalc 6/6 with Fortran; dispatch contract on :8801; pydantic-core owned; current site captured`

## RETURN

- CURRENT deployment root, HEAD, units captured (count)
- RAVENCALC scipy / scikit-learn built; Fortran objects present
- APP contract tests passed / total; PROOF paths **verbatim**
- PYDANTIC-CORE tag → SHA, licence, import OK
- DECISIONS closed this phase (list); DECISIONS FOR GARRETT: none

---

## READINESS — what Phase 10 already put in place

**11b's toolchain exists.** 10a built the Fortran cross toolchain
(`FORTRAN:forcevariable = ",fortran"`, `RUNTIMETARGET:append:pn-gcc-runtime =
" libquadmath"` in `symoneural.conf`), rc=0, sstate rsync'd 2.4 GB / 255 entries
per R10. The `scipy-fortran` decision is closed by O4 on that basis.

**O2 is already half-applied.** `symoneural-scipy` carries
`EXTRA_OEMESON += "-Duse-pythran=false"` and DEPENDS on
`python3-cython-native python3-pybind11-native symoneural-numpy-native
symoneural-numpy python3`. O2's amendment moves the pythran flag to PEP517
config-settings `setup-args=` and adds `gfortran-cross`; `python3-pybind11-native`
already comes from meta-python, which is in every runtime's bblayers. To verify
when the phase starts: `-Duse-pythran=false` reaches meson via the PEP517 path,
and `PEP517_BUILD_OPTS += "--skip-dependency-check"` is still needed or can be
dropped once the DEPENDS list is complete.

**4 of Ravencalc's 6 already build clean** under `symoneural-pristine`:
`symoneural-numpy` (1330 files, 19 `.so`), `symoneural-sympy` (3103),
`symoneural-mpmath` (115), `symoneural-openblas` (14, 1 `.so`, LAPACK present —
2304 Fortran-mangled symbols including `dgesvd_`, `dsyev_`). **scipy and
scikit-learn are the two outstanding**, which is exactly what 11b addresses.

**11a's target is confirmed reachable read-only.** Per R14 and Advisor Item 3,
`:8800` is captured by READING: if it is not serving, locate via
`systemctl cat symoneural-api` → `WorkingDirectory` and capture from disk. It is
**never started or stopped**.

**11c's stack is built.** `symoneural-fastapi` (109 files, PV 0.141.1),
`symoneural-starlette` (74, 1.6.0), `symoneural-uvicorn` (90, 0.52.4),
`symoneural-httpx` (52, 0.28.1), `symoneural-httpcore` (66, 1.0.9),
`symoneural-pydantic` (215, 2.13.5) — all rc=0, parity identical to baseline.

**11e's hardening pattern is superseded by 11-T.** 11-T's S1 replaces the single
`symoneural-dispatch.service` with the template `symoneural-dispatch@.service`,
"hardening identical", the estate's own instance being tenant `symoneural` on
:8801. Build 11e as specified; 11-T generalises it.

**Open decision `pydantic-core-ownership` is closed by O4** — borrow
`python3-pydantic-core` from meta-python, `PROVIDER=meta-python`. That removes the
last packaging question from 11c's dependency chain.


## ⚠ PYTHRAN CONFLICT — 11b as written cannot parse

11b's DEPENDS names `python3-pythran-native`. **It does not exist.**

```
find ~/symoneural-bootstrap-master -iname '*pythran*'   ->  (nothing)
python3-beniget  ABSENT      <- pythran's own hard dependency
python3-gast     PRESENT
python3-ply      PRESENT
```

Searched all of openembedded-core, meta-oe and meta-python. As written, 11b fails
at parse with `Nothing PROVIDES python3-pythran-native`. This also contradicts
Advisor O2, which stated pythran exists in no layer and directed
`-Duse-pythran=false`; the verification agrees with O2.

**Two workable paths, not chosen unilaterally:**

**(A) Disable it (O2).** pythran is OPTIONAL upstream. Build scipy with PEP517
config-settings `setup-args=-Duse-pythran=false` and record *"pythran: not
acquired, disabled at build"*. Costs some scipy hot-loop optimisation. A7
unaffected. Works today — `symoneural-scipy` already carries
`EXTRA_OEMESON += "-Duse-pythran=false"` from an earlier phase.

**(B) Acquire it.** Bring in pythran **and beniget** under A7 in Phase 11, as 11b's
text implies. Two further acquisitions with their own pins, licences and
containment checks.

**Default if unanswered: (A)** — it is the only path that builds without new
acquisitions, and 11b's gate is *"scipy and scikit-learn build"*, which (A)
satisfies. Recorded as `scipy-pythran` in `acquisition/unresolved.json` because the
two paths differ in what enters the estate.

## PYDANTIC-CORE — ruling REVERSED to OWN

An earlier ruling said borrow `python3-pydantic-core` from meta-python. **That is
reversed**: 11g owns it. The reason is decisive — pydantic-core is a **runtime**
dependency of pydantic, and Symoneural-API **ships** pydantic, so borrowing would
place a shipped component outside our own pin, and `import pydantic` fails at
runtime without it (11e cannot start).

Useful convergence: `core-v2.46.5` and `v2.13.5` **both** point at pydantic's
SRCREV `001dea020e0809844e5b17666432c9135a976f46`. Per E4, PV follows the package
the recipe builds, so `symoneural-pydantic` correctly took **2.13.5** and not
`core-v2.46.5` — and the tag deliberately set aside then is exactly the pin 11g
needs now.
