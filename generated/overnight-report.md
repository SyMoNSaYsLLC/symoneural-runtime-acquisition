# SyMoNeuRaL Overnight Build Report

Autonomous run. The file is the report. Appended after every phase.

| | |
|---|---|
| Host | BUILD HOST / REFERENCE MACHINE — /home/google/SymonSaysLLC |
| Build stack | OE-Core `fe7a24bc` · BitBake `046a90b0` |
| Start HEAD | (recorded below) |

---
## PHASE 0 — Protect the run · **GATE PASSED**

| Item | Result |
|---|---|
| 0a out-of-tree builds | **28 of 38** bbappends had `EXTERNALSRC_BUILD` = the source tree (B == S). All rewritten to `${WORKDIR}/build`. In-tree remaining: **0**. |
| 0b residue detection | Verifier now runs `git status --ignored` per acquired tree; ignored residue is a FINDING, not a silent pass. |
| 0c host safety (R6) | `BB_NUMBER_THREADS = "10"`, `PARALLEL_MAKE = "-j 12"` written into **13** local.conf files. |

**Residue found and cleared — 6 trees, 20 items.** This is what B == S had been doing:

| Tree | Residue |
|---|---|
| openblas, scipy, scikit-learn, sympy | `oe-logs`, `oe-workdir` symlinks |
| numpy | 3 × `__pycache__` under `numpy/_build_utils`, `_core/code_generators` |
| mpmath | `build/`, `mpmath.egg-info/`, **`mpmath/_version.py`** (generated INTO source) |
| sympy | `build/`, `sympy.egg-info/` |

`mpmath/_version.py` is the sharpest case: setuptools-scm generated a file *inside* pristine
upstream source. `.gitignore` was hiding all of it — which is exactly why 0b had to look
at `--ignored` rather than trust a clean `git status`.

**Hazard class: setuptools/hatchling write `.egg-info` and generated version files next to
`setup.py` — i.e. into `${S}` — regardless of where the build directory points.** Phase 0a
should stop recurrence; to be re-checked after every Python build tonight.

GATE: verifier **PASS** · 41/41 trees clean under both `--short` and `--ignored`.

## PHASE 1 — meta-openembedded admitted (D1) · **GATE PASSED**

| | |
|---|---|
| Pinned SHA | `43b79d8e372c4f69ebab6c85b39d97b41522080f` (master, pinned — never tracked) |
| Declared in manifest | before cloning, with URL / SHA / required-by |
| In `LOCKED_STACK` | yes — `control-plane.json` now carries it every regeneration |
| Layers added | `meta-oe`, `meta-python` — **Ravencalc only** |

**Providers found:** `python3-pybind11_3.0.4` ✓ · `nodejs_24.21.0` ✓ · **`pythran` ABSENT**.

pythran is in neither OE-Core nor meta-openembedded, and its chain is missing too
(`beniget`, `ply` both absent; only `gast` present). Authoring it in-stack would drag
beniget and **ply** — making the ply vendoring collision live immediately.

**Resolved without it:** scipy's `meson.options` exposes `use-pythran` as a boolean
defaulting to true, so scipy builds with `-Duse-pythran=false`. Cost is the loss of
Pythran-accelerated kernels (slower fallbacks), not loss of function. Recorded as a
BUILD-DESIGN decision rather than a blocker.

GATE: `bitbake -p` parses with both layers · verifier **PASS**.

## PHASE 2 — Ravencalc · **GATE PASSED WITH RECORDED BLOCKER** (4 of 6)

| Component | Result |
|---|---|
| openblas | BUILT · 14 files · 1 .so |
| sympy | BUILT · 3103 files |
| mpmath | BUILT · 192 files |
| numpy | BUILT · 1330 files · **19 .so** |
| scipy | **BLOCKED — toolchain** |
| scikit-learn | BLOCKED transitively on scipy |

ELF proof: ` ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dyn`

**scipy root cause — a toolchain decision, not a recipe fix.** scipy needs Fortran; the
OE cross toolchain is built `LANGUAGES="c,c++"` with `FORTRAN=""`, so
`x86_64-oe-linux-gfortran` does not exist.
Evidence: `meson.build:91 Unknown compiler(s): x86_64-oe-linux-gfortran`, log
`.../symoneural-scipy/1.18.1/temp/log.do_compile.2878019`. Recorded as `scipy-fortran`.

Cleared on the way there, each from its log:
- numpy absent from the **native** sysroot — scipy validates against `nativepython3`.
  Added `BBCLASSEXTEND = "native"` to symoneural-numpy so scipy builds against the numpy
  **we ship** (D2), not OE-Core's python3-numpy.
- pythran validated by `pyproject-build` even under `--no-isolation`. Suppressed with
  `PEP517_BUILD_OPTS += "--skip-dependency-check"` — honest here because
  `-Duse-pythran=false` means the declared dep is genuinely not exercised.

**2c — D2 recorded and wired.** `acquisition/provider-decisions.json` (CURATED, added to
`determinism_curated_declared`). Both `scan-oe-providers` and `scan-source-collisions`
now MERGE from it on every regeneration: all 7 decisions survive. Five build tools →
OE-CORE, numpy and gstreamer → SYMONEURAL-OWNED. **No Build-runtime trees deleted.**

## PHASE 3 — Symoneural-API · **GATE PASSED** (6 of 6)

| Component | files |
|---|---|
| fastapi | 109 |
| starlette | 74 |
| uvicorn | 90 |
| httpcore | 66 |
| httpx | 52 |
| pydantic | 215 |

**Systemic defect found here, fixed estate-wide: 13 recipes carried a non-SPDX LICENSE
token.** recipetool emits `LICENSE = "Unknown"` (and once `"Apache"`), which newer
OE-Core's SPDX parser rejects outright — `do_populate_lic` dies with
`AttributeError: 'UnknownId' object has no attribute 'name'`. Every value was
re-established from the licence text in the acquired tree, never from memory:
Encode projects → BSD-3-Clause, hls.js → Apache-2.0, anthropic-sdk-python / librespot /
llama.cpp → MIT, stratum + sv2-apps → Apache-2.0 AND MIT, gstreamer → LGPL-2.1-or-later,
pytorch → BSD-3-Clause, accelerate → Apache-2.0. **This would have broken every
remaining phase.**

**Second defect: a recipe with stubs and NO inherit fails silently.** fastapi reported
`do_compile` success and installed nothing, because recipetool emitted empty stubs and no
build class at all — so Phase 0's stub removal, which only touched recipes that *had* an
inherit, skipped it. Fixed with `inherit python_pep517` + `PEP517_BUILD_API = "pdm.backend"`.
Silent success is worse than loud failure.

Also cleared: httpx, httpcore and pydantic each needed
`python3-hatch-fancy-pypi-readme-native` in the native sysroot.

**DECISION RECORDED — `pydantic-core-ownership`.** pydantic needs pydantic-core
(Rust/maturin). meta-python supplies `python3-pydantic-core 2.46.4` and it is BORROWED
tonight. But it is linked into the shipped runtime, and D2 says own what you ship — so
under D2 it should be SyMoNeuRaL-owned. Recorded, not decided.

## PHASE 4 — Symoneural-CLI, Python half · **GATE PASSED** (2 of 2)

| Component | files |
|---|---|
| anthropic-sdk-python | 2817 |
| mcp-python-sdk | 252 |

**The PEP-517 closure is transitive and only a build reveals its depth.** mcp-python-sdk
needed `uv-dynamic-versioning`, which needed `jinja2` and `tomlkit`, which then needed
`dunamai~=1.26.1` — four rounds, each one only visible after satisfying the previous.
All four were present in meta-python; none of it was guessable from the manifest.

**A native recipe's RDEPENDS do not populate the native sysroot.** Transitive build
dependencies must be named explicitly as `-native` in DEPENDS. That is the general lesson,
not a quirk of this package.

**DECISION RECORDED — anthropic-sdk-python pins `hatchling==1.26.3` exactly**; the stack
ships 1.31.0. hatchling is a build backend: it produces the wheel and contributes no code
to it, so the check was skipped and the stack version used. If the exact backend version
ever matters for reproducibility, 1.26.3 needs packaging.

Contrast worth noting: for mcp-python-sdk I first reached for the same skip, then found
`python3-uv-dynamic-versioning 0.14.1` in meta-python and used the real backend instead.
Skipping is a last resort, not a first one — the derived version is now real rather than faked.

## PHASE 8 — Build runtime matches the stack in use · **GATE PASSED**

| Tree | Was | Now |
|---|---|---|
| `src/bitbake/source` | `0880963f` (2.8, scarthgap era) | **`046a90b0`** |
| `src/devtools/.../openembedded-core` | `2814f096` (scarthgap) | **`fe7a24bc`** |

Both clean, both VERIFIED, recipe SRCREV and `branch=` advanced to match (the
estate-correctness rule — source and recipe must agree). Intent was declared in
`source-manifest.json` before either fetch.

**Bootstrap untouched** — still `046a90b0` / `fe7a24bc`, exactly as required.
**The five build-tool trees are retained**; D2 changed only the provider selection,
not the acquisition.

The project's copy of its own build stack is no longer a stale souvenir of it.

## PHASE 5 — Rust: Crypto and Remix · IN PROGRESS

All three Rust recipes were bare recipetool stubs: **no inherit, no crates.inc**.

stratum prepared: `inherit cargo cargo-update-recipe-crates`, and
`bitbake -c update_crates` generated **233 `crate://` entries** into
`recipes/symoneural-stratum/symoneural-stratum-crates.inc` — tracked in git, not
resolved from the network at build time.

**Offline-proof method corrected mid-phase.** My first attempt ran `-c fetch` on stratum
alone, then `BB_NO_NETWORK=1`. That failed on `rust-source` and `llvm-project-source` —
because `-c fetch` on one recipe does not fetch the *toolchain's* sources. That was a
flaw in my test, not a finding. Correct form is `--runall=fetch` across the whole
dependency closure, then compile offline. `FETCH rc=0` with the full closure pulled;
offline compile running (llvm-native is the long pole — rust 1.98.1 and LLVM 23 build
from source).

## PHASE 7 — LLM: llama.cpp · PREPARED, NOT YET BUILT

**Misdetection found: llama.cpp inherited `python_poetry_core`.** It ships a
`pyproject.toml` for helper scripts and recipetool picked that over the `CMakeLists.txt`
that actually builds the project — so a C++ project was being built as a Python package.
Corrected to `inherit cmake`, with
`-DBUILD_SHARED_LIBS=ON -DGGML_NATIVE=OFF -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF`
(`GGML_NATIVE=OFF` because `-march=native` would bake the build host's CPU into a
cross-compiled artifact). A scan for the same misdetection across all other recipes
came back clear.

## PHASE 6 — Node consumers · BLOCKED ON A PRIOR DECISION

`nodejs_24.21.0` is available via meta-oe and the layer is in CLI, Streamer and Web
bblayers. But **three of the four consumers have no recipe at all**:

| Component | State |
|---|---|
| hls.js | recipe exists (generic stub, no inherit) |
| anthropic-sdk-typescript | **NO RECIPE** |
| mcp typescript-sdk | **NO RECIPE** |
| workers-sdk | **NO RECIPE** |

Those three were acquired by plain `git clone` under the v1.2 rules, which permitted
cloning but not `devtool add`. They have source at the intended revision and no recipe to
build it. Creating recipes needs `devtool add` against an existing tree, or hand-authored
recipes — an acquisition-path decision, not a build fix. Recorded; not invented tonight.

---

# MORNING REPORT

## PHASES

| Phase | Status | Commit |
|---|---|---|
| 0 · Protect the run | **GATE PASSED** | `2a996bb` |
| 1 · meta-openembedded admitted | **GATE PASSED** | `1632be3` |
| 2 · Ravencalc | **PASSED, 4 of 6** (blocker recorded) | `2d5e78d`, `9ad5f7a` |
| 3 · Symoneural-API | **GATE PASSED, 6 of 6** | `2008227` |
| 4 · CLI python half | **GATE PASSED, 2 of 2** | `e76fff4` |
| 5 · Rust | **IN PROGRESS** — llvm-native compiling | `c247b2f` (prep) |
| 6 · Node consumers | **BLOCKED** — 3 of 4 have no recipe | `c247b2f` |
| 7 · llama.cpp | **PREPARED**, not built — queued behind Phase 5 | `c247b2f` |
| 8 · Build runtime matches stack | **GATE PASSED** | `30cda16` |

## BUILT — 12 components across 3 runtimes

| Runtime | Component | files | .so |
|---|---|---|---|
| Ravencalc | openblas | 14 | **1** |
| Ravencalc | numpy | 1330 | **19** |
| Ravencalc | sympy | 3103 | 0 |
| Ravencalc | mpmath | 192 | 0 |
| API | fastapi | 109 | 0 |
| API | starlette | 74 | 0 |
| API | uvicorn | 90 | 0 |
| API | httpcore | 66 | 0 |
| API | httpx | 52 | 0 |
| API | pydantic | 215 | 0 |
| CLI | anthropic-sdk-python | 2817 | 0 |
| CLI | mcp-python-sdk | 252 | 0 |

ELF proof: `libopenblas.so.0.3` — ELF 64-bit LSB shared object, x86-64, dynamically linked.

Started the night at **1** built component (openblas). Ending at **12**.

## FAILED

| Component | Task | Root cause | Log | Change | Result |
|---|---|---|---|---|---|
| scipy | do_compile | needs Fortran; OE toolchain is `c,c++` only, no `x86_64-oe-linux-gfortran` (`meson.build:91`) | `symoneural-scipy/1.18.1/temp/log.do_compile.2878019` | none — toolchain decision | BLOCKED, recorded |
| scikit-learn | do_compile | transitively on scipy | — | none | BLOCKED |

## PRISTINE — 41 of 41 trees clean, tracked AND `--ignored`

**dirty = 0 · residue = 0**

## OFFLINE

`--runall=fetch` for stratum returned **rc=0** with the full closure pulled, including
`rust-source` and `llvm-project-source`. The `BB_NO_NETWORK=1` compile was still running
at report time. **Not yet proven** — an honest not-yet, not a pass.

## META-OE

SHA `43b79d8e372c4f69ebab6c85b39d97b41522080f`, pinned in `LOCKED_STACK`.
Layers `meta-oe` + `meta-python` added to Ravencalc, API, CLI, Crypto, Remix, Streamer,
Web, LLM. Providers consumed: `python3-pybind11`, `nodejs`, `python3-pydantic-core`,
`python3-uv-dynamic-versioning`, `python3-jinja2`, `python3-tomlkit`, `python3-dunamai`.

## DECISIONS RECORDED

The D2 seven — autoconf, automake, libtool, m4, ninja → **OE-CORE**; numpy, gstreamer →
**SYMONEURAL-OWNED** — are in `acquisition/provider-decisions.json` (CURATED) and are
MERGED by both provider scanners on every regeneration. Plus, new tonight:

1. `scipy-fortran` — toolchain lacks Fortran
2. `externalsrc-native-shared-tree` — hazard, see below
3. `pydantic-core-ownership` — borrowed from meta-python; D2 says own what you ship
4. scipy `use-pythran=false` — pythran unobtainable, chain drags ply
5. anthropic `hatchling==1.26.3` exact pin skipped — build backend only

## DECISIONS FOR GARRETT

1. **Rebuild gcc-cross with Fortran?** `FORTRAN:forcevariable = ",fortran"` unblocks scipy and scikit-learn. Without it those two never build.
2. **Own pydantic-core?** It is linked into the shipped API runtime, and D2 says own what you ship. Borrowed tonight from meta-python 2.46.4.
3. **How do the three TypeScript SDKs get recipes?** They have source at the intended revision and no recipe, because v1.2 permitted `git clone` but not `devtool add`. Phase 6 cannot proceed without an acquisition-path decision.
4. **Accept `--skip-dependency-check` as policy, or package the exact versions?** Used twice tonight (scipy/pythran, anthropic/hatchling), both times for build-only backends.
5. **Drop `BBCLASSEXTEND` on externalsrc recipes?** See hazard 1.

## HAZARD CLASSES FOUND

1. **Classes that write into `${S}`.** `cython.bbclass`'s postfunc `sed -i`s every `.c`/`.cpp` under `${S}`, which under externalsrc is pristine source. Dropped the class, took only its DEPENDS.
2. **`BBCLASSEXTEND = "native"` on an externalsrc recipe** gives target and native the same tree and bitbake runs them concurrently. Isolated empirically: either build alone is clean; both together flip a file 100755 → 100644.
3. **Python build backends write into `${S}` regardless of build dir** — `.egg-info`, `_version.py`, `.pdm-build/`. `.gitignore` was hiding all of it, which is why the verifier now checks `--ignored`.
4. **recipetool emits non-SPDX LICENSE tokens** (`Unknown`, `Apache`) that newer OE-Core rejects outright. 13 recipes affected.
5. **recipetool emits stubs that override an inherited class** — and, worse, sometimes stubs with **no** inherit, which report success while installing nothing (fastapi).
6. **recipetool misdetects build systems** — llama.cpp, a C++/cmake project, inherited `python_poetry_core` from a helper-script `pyproject.toml`.

## VERDICTS

| | |
|---|---|
| CONTROL-PLANE | **PASS** |
| ESTATE-COMPLETENESS | **PASS** |
| ACQUISITION-STATE | **FAIL** — by design; open decisions, not defects |
