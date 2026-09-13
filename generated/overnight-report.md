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
