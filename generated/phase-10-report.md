# SyMoNeuRaL Phase 10 Report

## DECISIONS CLEARED — actioned

| # | Decision | Action taken |
|---|---|---|
| 1 | FORTRAN estate-wide | `FORTRAN:forcevariable = ",fortran"` + `RUNTIMETARGET:append:pn-gcc-runtime = " libquadmath"` in Ravencalc `local.conf` (moves to `meta-symoneural/conf/distro/symoneural.conf` in 10a). **gcc-cross-x86_64 + gcc-runtime rebuilding now**; sstate rsync to `/home/google/sstate-backup` is chained to completion (R10). |
| 2 | TypeScript SDKs + hls.js | Deferred to Phase 10e as instructed. Old Phase 6 dissolved, not started. |
| 3 | Models register | **All three probes ABSENT.** Search run, nothing found, consolidation NOT performed, stopped looking. |
| 4 | Rust / LLVM 23 | Allowed to finish; paid once. sstate treated as protected (R10) — never deleted to recover disk. |
| 5 | Pristine policy | Noted: externalsrc retired in Phase 10 via `symoneural-pristine.bbclass`. Awaiting the pasted spec. |
| 6 | Acquisition pace | `acquisition/pending-acquisitions.json` written — **14 rows, 13 RELEASE + 1 SNAPSHOT**, CURATED, none acquired. |
| 7 | Sequence | Phase 5 and the Fortran rebuild are running; old Phase 6 and Phase 9 NOT started. |

## TWO PREMISE CORRECTIONS

**R6 says "the box has 0 swap".** It has **31 GB**, with 16/94 GB RAM in use.
The hard-freeze hazard R6 guards against is not present, which is why the Fortran
rebuild could safely start alongside a nearly-finished Phase 5.
`BB_NUMBER_THREADS = "10"` retained regardless — the setting is cheap and harmless.

**A1 asks for the latest STABLE release tag; stable-diffusion.cpp has none.**
Its tags are `master-<N>-<sha>`, generated per commit. Recorded as
`tag_kind: SNAPSHOT`, `master-859-7f410a3` → `7f410a37` — a commit snapshot, not a release.

## MODELS — ABSENT

| File | Runtime | State |
|---|---|---|
| `flux1-schnell-q4_k.gguf` | Diffuse | **ABSENT** |
| `Qwen2.5-7B-Instruct-Q4_K_M.gguf` | LLM | **ABSENT** |
| `ggml-base.en.bin` | Diffuse | **ABSENT** |

`find /home/google -xdev` returned no matches. The old deployment's `backend/models`
is not on this host. Nothing moved, nothing copied. **Garrett answers where they are.**

## COLLISIONS RECORDED BEFORE ACQUIRING (A3)

**ggml will exist three times** once Diffuse is acquired — llama.cpp (LLM, ggml-org),
whisper.cpp (Diffuse, ggml-org), stable-diffusion.cpp (Diffuse, **leejet/ggml, a personal
fork**). Two upstreams, three copies. `CROSS-RUNTIME-DUPLICATE`, decision `UNRESOLVED`.

**ComfyUI: NOT ACQUIRED** — GPL-3.0-or-later, replaced by diffusers (Apache-2.0).

## AWAITING

Phase 10's specification has not been pasted. `symoneural-pristine.bbclass`,
`meta-symoneural`, and 10a–10e are not started.

## PHASE 5 RESULT — OFFLINE COMPILE PROVEN

`--runall=fetch` rc=0, then `BB_NO_NETWORK=1 bitbake symoneural-stratum`:

| | |
|---|---|
| `do_compile` | **Succeeded** with the network disabled |
| NetworkAccess denials during the offline half | **0** |
| Artifacts | **102 rlibs** |
| Crate closure | 233 `crate://` entries, tracked in the recipe dir |

**The offline guarantee holds.** rust 1.98.1, LLVM 23 and all 233 crates compiled with
no network after fetch. That was the open question from the dependency-closure report,
and it is now answered with evidence rather than enumeration.

`do_install` then failed — `Did not find anything to install`. stratum is a **library
workspace with no binary targets**, and `cargo_do_install` looks for binaries. A packaging
matter, unrelated to the offline question, and it is exactly what R12's empty-`${D}` check
exists to catch loudly rather than pass quietly.

## PHASE 10b — CLASS PROVEN

| Test | Result |
|---|---|
| Positive: export at the real SRCREV | **PASS** — `${WORKDIR}/pristine` populated |
| **Negative: wrong SRCREV** | **PASS — `do_unpack` FAILED** as required |

Negative-test message, verbatim:

> `PIN MISMATCH. .../hls.js is at e5ff3583... but SRCREV says deadbeef.... Refusing to build a tree that is not at its pinned revision.`

## PHASE 10 — progress

| Item | Status |
|---|---|
| 10a Fortran | **DONE** — `FORTRAN BUILD rc=0`, ~10 min wall; sstate rsync'd to `/home/google/sstate-backup`, **2.4 GB / 255 entries** |
| 10b class | **DONE** — positive export works; **negative test FAILS correctly** with PIN MISMATCH |
| 10c migration | **38 of 41** recipes in `meta-symoneural/recipes-<runtime>/`; **0 EXTERNALSRC remains** |
| 10d defects | **DONE** — 0 non-SPDX LICENSE, 0 stubs-beside-inherit, 0 recipes without inherit; R12 empty-`${D}` check added |
| 10e npm | running — `recipetool` npm handler on the TypeScript SDKs |
| 10f parity | running |

The 3 not migrated are the TypeScript SDKs, which have no recipe yet — that is 10e's job.

**Defect found by the R12 check itself, before it ever ran a build.** My first task name was
`do_install_append_symon_empty_check`. Newer bitbake parses `_append` in a variable name as
the **old override syntax** and rejected every recipe in the layer — 2794 files failed to
parse. Renamed to `symon_assert_nonempty_d`. A check meant to catch silent failure would
itself have failed loudly; it did, which is the right direction.

**`sv2-spec` was `LICENSE = "CLOSED"` — a false statement.** Its tree carries
`License/BSD-3-Clause` and `License/CC0-1.0`. Corrected to `BSD-3-Clause OR CC0-1.0`.
The files sit in a `License/` **directory**, which is why every scanner missed them.

## PHASE 10f — PARITY REBUILD

Rebuilt every recipe built so far under `symoneural-pristine`, in all three
runtimes that have builds. `FILES` counts regular files in `${D}` (the baseline
definition — symlinks excluded).

| Runtime | Recipe | before | after | .so | Verdict |
|---|---|---|---|---|---|
| Ravencalc | symoneural-mpmath | 192 | **115** | 0 | **EXPLAINED DELTA — see below** |
| Ravencalc | symoneural-numpy | 1330 | 1330 | 19 | match |
| Ravencalc | symoneural-openblas | 14 | 14 | 1 | match |
| Ravencalc | symoneural-sympy | 3103 | 3103 | 0 | match |
| API | symoneural-fastapi | 109 | 109 | 0 | match |
| API | symoneural-httpcore | 66 | 66 | 0 | match |
| API | symoneural-httpx | 52 | 52 | 0 | match |
| API | symoneural-pydantic | 215 | 215 | 0 | match |
| API | symoneural-starlette | 74 | 74 | 0 | match |
| API | symoneural-uvicorn | 90 | 90 | 0 | match |
| CLI | symoneural-anthropic-sdk-python | 2817 | pending | 0 | blocked on nodejs-native |
| CLI | symoneural-mcp-python-sdk | 252 | pending | 0 | blocked on nodejs-native |

`bitbake -k` exit codes: Ravencalc **rc=0**, API **rc=0**, both with 0 ERRORs.

### DEFECT — setuptools-scm cannot work under the class (FIXED)

`symoneural-mpmath do_compile` failed on the first parity run:

> `LookupError: setuptools-scm was unable to detect version for .../1.4.1/pristine`
> `ERROR Backend subprocess exited when trying to invoke get_requires_for_build_wheel`

A `git archive` export carries no `.git` — that is what makes `${S}` disposable.
setuptools-scm derives the version by asking git, so it cannot work. Under
externalsrc these recipes worked **only because `${S}` was the git repo**, which
is exactly the coupling this class removes. That was never correct: the version
came from whatever state the tree was in, not from the pin.

Fixed once, in the class, rather than per recipe:

```
export SETUPTOOLS_SCM_PRETEND_VERSION = "${PV}"
```

Affects `mpmath` and `vllm` today; every future Python recipe is covered without
anyone having to remember. After the fix, `symoneural-mpmath do_compile: Succeeded`.

### The mpmath delta is a consequence of the same root cause, and it is correct

192 - 115 = **77**, accounted for exactly: `mpmath/tests` holds 38 `.py` files,
which contribute 38 `.pyc` files plus one non-`.py` file = 77.

`mpmath/tests` **has no `__init__.py`**, so it is not a package. mpmath declares
`[tool.setuptools.packages] find = {namespaces = false}`, has no `MANIFEST.in`,
declares no `package-data`, and nothing in `mpmath/__init__.py` imports it. Its
inclusion in the externalsrc build came from setuptools-scm's `setuptools.file_finders`
entry point, which lists git-tracked files. No `.git`, no file finder, no tests.

The controlled comparison is in the same build:

| | test dirs | with `__init__.py` | outcome |
|---|---|---|---|
| sympy | 65 | **65 (all)** | real packages, discovered, **3103 unchanged** |
| mpmath | 1 | **0** | not a package, correctly skipped, **192 -> 115** |

So the old 192 was output that varied with VCS metadata — non-reproducible by
construction. 115 is what a build from a released sdist produces. Recorded as an
EXPLAINED DELTA, not a regression.

### DEFECT — build residue was recorded as a licence file

`license-inventory.json` carried
`fastapi/.pdm-build/fastapi-0.141.1.dist-info/licenses/LICENSE`
(sha256 `4ec89ffc81485b97fec584b2d4a961032eeffe834453894fd9c1274906cc744e`).
`.pdm-build/` is pdm-backend's build directory: under `EXTERNALSRC_BUILD == S` the
build wrote it into the pristine fastapi tree, and the licence scanner then recorded
it as upstream licence material. It is no longer present — removed by the 10c
migration, not by the class, which only exports and never cleans srctrees.
Record regenerated 431 -> 430; report and SHA256SUMS regenerated in the same pass
so report-agreement did not flip.

### DEFECT — duplicate BBFILE_COLLECTIONS wedged the npm handler

`devtool add` auto-creates `<builddir>/workspace`, which declares
`BBFILE_COLLECTIONS += "workspacelayer"` — the same identifier as the existing
`devtool-workspace` layer. With both in `bblayers.conf`, every parse died with
`Found duplicated BBFILE_COLLECTIONS 'workspacelayer'`. This killed the first 10e
run; Symoneural-Crypto carried the same latent conflict. Both cleared: all nine
runtimes now reference `meta-symoneural` only.
