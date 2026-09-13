# SyMoNeuRaL Phase 10 Report

## ITEM LEDGER — resume from the first item not marked DONE

Per COMMON/STATE. Appended after every item; this file is the report.

| Item | State | Evidence |
|---|---|---|
| 10a Fortran toolchain | **DONE** | rc=0, ~10 min, sstate rsync'd 2.4 GB / 255 entries (R10) |
| 10b symoneural-pristine class | **DONE** | positive + negative test; PIN MISMATCH fatal fires |
| 10c Recipes -> meta-symoneural | **DONE** | 38/38 migrated, 0 left in any workspace |
| 10d Six defect classes | **DONE** | 0 non-SPDX, 0 stubs-beside-inherit, 0 missing inherit, R12 task added |
| 10e npm recipes (4) | **IN PROGRESS** | blocked on nodejs-native (V8 compiling in CLI cooker) |
| 10f Parity rebuild | **10 of 12 DONE** | Ravencalc rc=0, API rc=0; CLI 2 pending on 10e's nodejs |
| R11 zero externalsrc | **DONE** | 0 in any parsed layer, all 9 runtimes |
| R12' stratum rlibs -> staticdev | **IN PROGRESS** | CARGO_INSTALL_LIBRARIES set; 16 rlibs; building |
| R6' threads per build dir | **DONE** | BB=10 / PM=-j 12 on all 10 build dirs (Adaptive-Fabric was unset) |
| Trees clean --ignored | **DONE** | 41/41 during a live build, 41/41 after |
| Control-plane verifier | **DONE** | CONTROL-PLANE PASS, ESTATE-COMPLETENESS PASS |
| Phase 10 GATE | **OPEN** | waits on 10e + CLI parity |

### DECISIONS FOR GARRETT

1. **sv2-apps: "one recipe per workspace, four recipes" does not match the tree.**
   Advisor Item 2 says both. On disk there are exactly **two** cargo workspaces,
   holding **four** binary packages between them:

   | workspace | members |
   |---|---|
   | `miner-apps/` | `jd-client`, `translator` |
   | `pool-apps/` | `jd-server`, `pool` |

   So "one per workspace" gives 2 and "four recipes" gives 4. Both readings are
   buildable. Two is the technically cheaper one: a cargo workspace shares a
   single `Cargo.lock`, so one recipe per workspace means one generated
   `-crates.inc` closure each, whereas four recipes duplicate that closure twice
   over and must be kept in lockstep by hand. Four gives independently
   installable binaries and matches the literal instruction.
   **Not acted on** — it is Crypto/Phase-11 work and does not block the Phase 10
   gate. Recorded rather than guessed because the two readings produce materially
   different recipe sets.
2. **`--skip-dependency-check` as policy.** Used on scipy's PEP-517 build to get
   past a transitive closure gap. Works, but it disables the backend's own
   dependency assertion estate-wide if adopted as a pattern.
3. **`pydantic-core` ownership** — still open from the earlier phase.
4. **mpmath tests no longer installed** (192 -> 115). Correct per upstream
   packaging, documented below. Flagging only because anything that ran
   `mpmath.tests` implicitly will now fail to import.

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

> **SUPERSEDED — the table below is NOT current evidence.** These counts were
> produced under the first version of `symoneural-pristine`. That class has since
> changed three times: `do_fetch` no longer noexec (it was silently starving every
> `crate://`/npm SRC_URI), the export became a `do_unpack` prefunc instead of
> replacing the task, and `cleandirs` moved onto the prefunc (on `do_unpack` it
> deleted the export before `do_populate_lic` ran). Parity must be re-captured
> under the fixed class before the gate. Kept for the findings, not the numbers.


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

## R13 / R15 — SECRETS AND OWNER (read-only; no value was read or written)

`symoneural-secrets` is installed at `/usr/local/sbin/symoneural-secrets` and has
provisioned `/etc/symoneural` (`schema symoneural-secrets/1`, updated
2026-09-13T01:20:02-0400). Read `manifest.json` only — names, `kind` and `status`.
No `.env` file was opened; all six are `0600 root`.

**44 keys across 6 files — 40 `set`, 4 `unset`.** By kind: 24 `config`,
11 `internal`, 9 `external`. `suspect: []`.

Per R13, the units configured **OFF** because their secret is unset:

| Unset key | Unit held off |
|---|---|
| `SYM_GATEWAY_BENEFICIARY` | TRON licensing |
| `SYM_GATEWAY_CONTRACT` | TRON licensing |
| `SYM_MINER_POOL` | real mining (benchmark still works) |
| `SYM_MINER_WALLET` | real mining |

The manifest's own `units_that_stay_off_until_set` additionally lists five keys
that are `set` but gate optional features (`SMTP_PASS`, `SMTP_USER`,
`SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `TUNNEL_TOKEN`). All five are
currently `set`, so those units are **not** held off. Only the four above are.

**R15 owner:** `SYM_OWNER_EMAIL` and `SYM_OWNER_TOKEN` are both present in
`api.env` and both `status: set`. `SYM_OWNER_EMAIL` shares a fingerprint with
`MAIL_ADMIN`, `MAIL_FROM` and `SMTP_USER`, i.e. one identity across all four.
Nothing further is needed from a human for the accounts service to create the
owner account on first start.

Two signing keypairs are provisioned, public halves only in the manifest:
`contract-signing` (`5ee48936edd69d74`) and `settlement-signing` (`8f753c19fdfbd141`).

**`SYMON_MODELS_DIR` = `/home/google/symoneural-models` exists** with
`hf/ image/ llm/ rembg/ whisper/` — **all empty, 24K total**. The MODELS-ABSENT
finding recorded earlier in this report still stands; no weights are on disk.

## CLASS DEFECTS FOUND BY BUILDING — the export has no `.git`, and that is load-bearing

Four distinct defects, all one root cause: `symoneural-pristine` exports with
`git archive HEAD`, so `${S}` has **no `.git`** and **no SRC_URI is unpacked into
it**. Under externalsrc both facts were accidentally untrue, so nothing had ever
exercised these paths. Each was found by a build, not by inspection.

| # | Symptom | Root cause | Fix (all in the class) |
|---|---|---|---|
| 1 | `LookupError: setuptools-scm was unable to detect version` (mpmath) | setuptools-scm asks git for the version | `export SETUPTOOLS_SCM_PRETEND_VERSION = "${PV}"` |
| 2 | `no matching package named 'bitcoin'`, vendor dir **0 crates** (stratum) | `do_fetch[noexec]="1"` starved *every* SRC_URI, not just the upstream git one | strip only `git://`/`gitsm://` at parse; let `do_fetch` run |
| 3 | `LIC_FILES_CHKSUM points to an invalid file` x45, `${S}` empty | `do_unpack[cleandirs]` runs **after** prefuncs, deleting the export | move flag to `symon_export_pristine[cleandirs]` |
| 4 | `Error getting the version from source uv-dynamic-versioning: This does not appear to be a Git project` (mcp-python-sdk) | a *second* VCS-versioning backend | `export UV_DYNAMIC_VERSIONING_BYPASS = "${PV}"` |

Defect 2 is the one worth remembering. `do_fetch[noexec] = "1"` was written on the
reasoning "the tree is already acquired, there is nothing to fetch." True of the
upstream URI, false of everything else — it silently starved cargo's 233
`crate://` entries and would have done the same to every npm recipe. The 37
recipes with no extra SRC_URI could never have exposed it. Only building a cargo
recipe did. Vendored crates went **0 -> 183** after the fix.

Defect 4 shows the family is open-ended: VCS-derived versioning is a *class* of
backend, not one tool. Both bypass variable names were read from the installed
plugin source, not guessed (`uv_dynamic_versioning/main.py:30`). A third backend
will need a third line, and it belongs in the class, because the cause is the class.

### Consequence for evidence already recorded

The Phase 10f parity table above is SUPERSEDED: it was captured under the class
*before* defects 2-4 were fixed. `offline-compile` in `acquisition/unresolved.json`
was likewise re-stated as **RESOLVED-SCOPED** — its proof (102 rlibs, 0
NetworkAccess denials) is real but was produced under externalsrc, and defect 2
means it had never been reproduced under the class. Re-proof is required before
any release claim.

## PHASE 10f — PARITY, RE-CAPTURED UNDER THE FIXED CLASS

Supersedes the earlier table. All four runtimes rebuilt after defects 1-4 and the
PV correction. `bitbake -k` exit codes: **Ravencalc rc=0, API rc=0, CLI rc=0,
Crypto rc=0 — 0 ERRORs in all four.**

| Runtime | Recipe | before | after | .so | Verdict |
|---|---|---|---|---|---|
| Ravencalc | symoneural-mpmath | 192 | 115 | 0 | EXPLAINED DELTA (see above) |
| Ravencalc | symoneural-numpy | 1330 | **1330** | 19 | match |
| Ravencalc | symoneural-openblas | 14 | **14** | 1 | match |
| Ravencalc | symoneural-sympy | 3103 | **3103** | 0 | match |
| API | symoneural-fastapi | 109 | **109** | 0 | match |
| API | symoneural-httpcore | 66 | **66** | 0 | match |
| API | symoneural-httpx | 52 | **52** | 0 | match |
| API | symoneural-pydantic | 215 | **215** | 0 | match |
| API | symoneural-starlette | 74 | **74** | 0 | match |
| API | symoneural-uvicorn | 90 | **90** | 0 | match |
| CLI | symoneural-anthropic-sdk-python | 2817 | **2817** | 0 | match |
| CLI | symoneural-mcp-python-sdk | 252 | **252** | 0 | match |
| Crypto | symoneural-stratum | (empty ${D}) | **16** | 0 | R12' SATISFIED |

**11 of 12 identical; the twelfth is the documented mpmath case.**

### R12' — stratum installs a real artifact

16 rlibs into `/usr/lib/rustlib/x86_64-oe-linux-gnu/lib/`, packaged
`${PN}-staticdev`: both workspace packages (`libstratum_core.rlib`,
`libstratum_translation.rlib`) plus 14 SV2 protocol libraries
(codec, framing, mining, noise, channels, handlers, parsers, ...).
**0 host `.so` leaked** into the target package.

### DEFECT — every package in the estate was versioned `1.0+git`

23 recipes carried recipetool's placeholder `PV = "1.0+git"`. Not cosmetic:

* every `.ipk` was named `<pkg>_1.0+git-r0`, so version-based dependency
  resolution across the estate was meaningless;
* `symoneural-pristine` exports `PV` as the wheel version, so the placeholder was
  written into Python package metadata. `uv-dynamic-versioning` parsed
  `"1.0+git"` and died on `int(parts[index])` -> `IndexError`. mpmath only ever
  worked because it happened to carry a real `PV`.

Fixed by deriving `PV` from the release tag at each pinned SHA. **22 of 23
resolved**, all matching the pins already on record. Two needed care - a
first-match pick would have got both wrong:

| Recipe | Tags at the SAME commit | Correct PV |
|---|---|---|
| `symoneural-pydantic` | `core-v2.46.5`, `v2.13.5` | **2.13.5** |
| `symoneural-llama-cpp` | `b10809`, `v0.4.0` | **0.4.0** |

Selection is by version *shape* (`^v?\d+(\.\d+)*$`, shortest match), not by
position. `symoneural-sv2-spec` is the single skip: no version tag exists at its
SHA, so there is nothing to derive and none was invented.

### R1 VIOLATION FOUND AND REVERSED — by the cleanliness check, as designed

`Symoneural-CLI/src/anthropic/source/anthropic-sdk-typescript` was **dirty**:

```
?? npm-shrinkwrap.json.copy
!! node_modules/            (3.0 MB)
!! npm-shrinkwrap.json
```

Residue from the FIRST 10e attempt, which handed recipetool the acquired tree
directly. `create_npm.py:_generate_shrinkwrap()` runs `npm shrinkwrap` **inside
the srctree it is given**, so it wrote into pristine upstream source. This is
precisely the hazard R1 exists to prevent, and it is why 10e was redesigned to
export a disposable copy first and only then hand that to recipetool.

Verified before touching anything: **no tracked file was altered** (`git status`
showed only `??`/`!!` entries) and HEAD was still exactly
`135f71e9297683e14614d4307081c0273ed0a09c`, the pinned SHA. The three added paths
were removed; the tree is pristine again.

**41/41 trees clean under `--ignored` after a cargo build** — cargo writes
`.cargo/` and `target/` and had never been exercised against an export until now.
