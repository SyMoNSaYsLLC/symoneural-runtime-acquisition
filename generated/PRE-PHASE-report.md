# PRE-PHASE REPORT — state of the estate before Phase 11

> Generated 2026-09-13T07:23:52-04:00. Phase 10 CLOSED at commit `1f007af`.
> This is the baseline every later phase builds on. Nothing below is projected;
> each figure was measured on this box.

## 1. WHAT IS BUILT

| Runtime | Recipe | files in `${D}` | `.so` |
|---|---|---|---|
| Ravencalc | `symoneural-mpmath` | 115 | 0 |
| Ravencalc | `symoneural-numpy` | 1330 | 19 |
| Ravencalc | `symoneural-openblas` | 14 | 1 |
| Ravencalc | `symoneural-sympy` | 3103 | 0 |
| API | `symoneural-fastapi` | 109 | 0 |
| API | `symoneural-httpcore` | 66 | 0 |
| API | `symoneural-httpx` | 52 | 0 |
| API | `symoneural-pydantic` | 215 | 0 |
| API | `symoneural-starlette` | 74 | 0 |
| API | `symoneural-uvicorn` | 90 | 0 |
| CLI | `symoneural-anthropic-sdk-python` | 2817 | 0 |
| CLI | `symoneural-anthropic-sdk-typescript` | 702 | 0 |
| CLI | `symoneural-mcp-python-sdk` | 252 | 0 |
| Crypto | `symoneural-stratum` | 16 | 0 |
| Streamer | `symoneural-hlsjs` | 0 | 0 |

**15 recipes built clean.** All runtimes `rc=0`, 0 ERRORs.

## 2. RAVENCALC — 4 of 6, and the two missing ARE Phase 11

| Component | State |
|---|---|
| `symoneural-numpy` | BUILT 1330 files, 19 `.so` |
| `symoneural-sympy` | BUILT 3103 files |
| `symoneural-mpmath` | BUILT 115 files (tests correctly excluded) |
| `symoneural-openblas` | BUILT 14 files, 1 `.so`, LAPACK linked (2304 Fortran symbols) |
| `symoneural-scipy` | **NOT BUILT — Phase 11 item 11b** |
| `symoneural-scikit-learn` | **NOT BUILT — Phase 11 item 11b** |

**CORRECTION.** An earlier version of this report claimed openblas proves the
Fortran toolchain works. **It does not.** openblas is built
`-DNOFORTRAN=1 -DC_LAPACK=1` — the C-translated LAPACK — so its 2,304
Fortran-mangled symbols come from f2c output, not from gfortran. **No consumer has
used gfortran yet; scipy will be the first.**

The compiler itself is verified present and working, by direct invocation rather
than by inference:

```
$ x86_64-oe-linux-gfortran --version
GNU Fortran (GCC) 16.2.0
$ x86_64-oe-linux-gfortran -c t.f90 -o t.o      ->  2240 bytes
```

It is staged into every target `recipe-sysroot-native` by the cross toolchain, so
**no `DEPENDS` entry is needed** — 11b's `gfortran-cross` names no recipe in any
layer and bitbake refuses it with `Nothing PROVIDES 'gfortran-cross'`.

## 3. CONTROL PLANE
```
-- completeness reconciliation --
  PRESENT-AT-INTENDED-REVISION:  42
  PRESENT-REVISION-MISMATCH:     0
  MISSING:                       0
  EXTRA-UNDECLARED:              0
  INTENT-UNRESOLVED:             0
  DEFERRED:                      2
  -- report agreement --
  source drift:                  report=41     verifier=41     OK
  dependency drift:              report=12825  verifier=12825  OK
  submodule drift:               report=85     verifier=85     OK
  license drift:                 report=430    verifier=430    OK
  CONTROL-PLANE RESULT:      PASS
  ESTATE-COMPLETENESS RESULT: PASS
```

## 4. DECISIONS — 1 open of 14 tracked

| Decision | State |
|---|---|
| `FreeToken/torch` | **OPEN-OWNED-BY-PHASE-19** — Adaptive-Fabric build design |

Closed this phase:

- `all recipes` → **ACCEPTED-HISTORICAL**
- `anthropic-sdk-typescript` → **REFERENCE-ONLY**
- `crates-inc-closure` → **RESOLVED**
- `direct-vs-oe-core` → **RESOLVED**
- `externalsrc-native-shared-tree` → **RESOLVED**
- `mcp-typescript-sdk` → **REFERENCE-ONLY**
- `nodejs` → **RESOLVED**
- `offline-compile` → **RESOLVED-SCOPED**
- `pydantic-core-ownership` → **RESOLVED-OWN**
- `scipy-fortran` → **RESOLVED**
- `scipy-pythran` → **RESOLVED-DEFAULT-A**
- `symoneural-openblas` → **RESOLVED**
- `symoneural-workerd` → **REFERENCE-ONLY**

## 5. GUARDS NOW LIVE (and why that sentence needed writing)

| Guard | Fires | Proven by |
|---|---|---|
| PIN MISMATCH | tree not at SRCREV | negative test — moved HEAD, `do_unpack` failed |
| empty `${D}` (R12) | `do_install` ships nothing | negative test — stubbed `do_install`, fatal raised |
| npm closure | shrinkwrap declares N, none unpacked | fired live: `1169 unpacked for 1072 declared` |
| cargo closure | `crate://` declared, vendor dir empty | **not yet negative-tested** |
| licence files present | `LIC_FILES_CHKSUM` path missing from export | **not yet negative-tested** |
| export non-empty | export deleted between write and use | **not yet negative-tested** |

**All six were no-ops until this phase.** `addtask foo` binds to `do_foo`;
three were declared without the prefix, so bitbake created the tasks, ran them,
and they did nothing — 31 log files reading
`Function do_symon_assert_nonempty_d doesn't exist`. They went undetected
because nothing ever failed: the absence of an error was read as the presence
of a check. The three marked **not yet negative-tested** are currently trusted
on exactly that reasoning.

## 6. HOST

| | |
|---|---|
| GPU | RTX 5070 Ti, Blackwell **sm_120**, driver 615.71.09, CUDA 13.4 |
| CPU | 20 cores |
| RAM / swap | 94 GiB / 31 GiB |
| Disk free | 599G |
| Build dirs | 9 runtimes, `BB_NUMBER_THREADS=10` / `PARALLEL_MAKE=-j 12` each (R6') |
| `:8800` | **not serving** — no listener, no loaded unit. 11a takes the disk-capture fallback |
| `SYMON_MODELS_DIR` | `/home/google/symoneural-models` — exists, **empty** (24K) |
| Secrets | 44 keys, 40 `set` / 4 `unset`; owner bootstrap ready |

## 7. WHAT PHASE 11 INHERITS

- FastAPI stack built: fastapi 109, starlette 74, uvicorn 90, httpx 52, httpcore 66, pydantic 215
- `pydantic-core` ruled **OWN** (11g) at `core-v2.46.5` — the tag that shares pydantic's SRCREV
- `pythran` decided path (A): disabled at build, kept DEFERRED in pending-acquisitions
- 5 decisions pre-staged for closure in 11h/11i
- Target `nodejs` required by nothing; `nodejs-native` cached (9.1 GB + 1.6 GB in sstate)
