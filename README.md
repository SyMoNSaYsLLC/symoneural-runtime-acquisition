# SyMoNeuRaL

A multi-runtime software estate built from **pristine upstream source** with
BitBake/OpenEmbedded. Every component is pinned to a commit, built from that
commit, and refuses to build if the tree has drifted.

**Status (2026-09-15):** acquisition is CLOSED at **100 pinned sources**
(98 verified byte-identical to upstream, 2 held REFERENCE-ONLY); the layer holds
**110 recipes**; the last recorded workscope audit packaged 85 of 86 target
components (`docs/maintenance/2026-09-14-overnight-platform-and-compile-remaining.md`).
**No release has been cut.** The release unit (`packagegroup-symoneural-rack`)
does not exist yet and the Phase 20 release gate has not started. This is an
estate under construction, not a finished product. Live counts come from
`tools/estate-facts`, `python3 tools/verify-acquisition.py` and the generated
`Symoneural-Runtime-Aquisition.md` — never from this paragraph.

## What this repository is

Two things, deliberately in one repository:

| Path | What |
|---|---|
| `meta-symoneural/` | the OE layer: recipes, `symoneural-pristine.bbclass`, `symoneural-cuda.bbclass`, distro config |
| `acquisition/` | the control plane: source locks, dependency graph, licence inventory, decisions |
| `tools/` | scanners, the acquisition verifier, `edit-guard`, the pre-publish audit, proofs |
| `generated/`, `docs/` | phase reports, evidence transcripts, maintenance records — the estate's own build record |
| `Symoneural-<Runtime>/app/` | first-party code (`libsymoneural-llm`, `symoneural-api`) |
| `Symoneural-<Runtime>/src/<group>/source/<name>/` | **acquired upstream source, committed at its pin** (SOURCES-100, 2026-09-13) |

The acquired trees are the bulk of the repository: about **291,000 tracked
files** and ~8 GB of history. They enter git through `tools/ingest-tree`, which
reads upstream's tree object at the pinned commit (never `git add`, which would
apply upstream `.gitignore` rules and drop files). `.gitignore` states the
policy at its top: nothing under `Symoneural-*/src/*/source/` is ignored; the
per-tree pin stores (`.gitpins/`) are.

## What it is NOT

**No build output.** Everything derived is gitignored:

```
Symoneural-*/build        derived from recipes + pins   (gitignored)
Symoneural-*/downloads    refetchable from SRC_URI      (gitignored)
Symoneural-*/sstate-cache derived; protected on disk by R10, never in git
**/.gitpins/              per-tree pin stores: local provenance, never pushed
```

The recipe is the truth; a build is one instance of executing it. If the output
had to be committed to be preserved, the estate would not be reproducible — and
reproducibility is the whole point.

**No secrets, ever.** `/etc/symoneural/*.env` is root-owned `0600` outside this
repo (R13). `tools/pre-publish-audit.sh` scans filenames and content across all
history (outside the verified upstream trees) before every push; `.gitignore`
denies the known shapes by pattern.

**No model weights.** `SYMON_MODELS_DIR=/home/google/symoneural-models`; the
register is `acquisition/model-register.json`.

## Build from source

### 1. Bootstrap

See **[BOOTSTRAP.md](BOOTSTRAP.md)** — three `git clone` + `git checkout <SHA>`
commands. Required; the estate references it by absolute path.

### 2. Verify the pinned sources

Per **A7**, acquisition happens inside the phase that builds a component, from
`acquisition/pending-acquisitions.json`. Verify what is checked out:

```sh
python3 tools/ingest-tree verify --all
python3 tools/verify-acquisition.py
```

Expect every component `· VERIFIED`, `CONTROL-PLANE RESULT: PASS` and
`ESTATE-COMPLETENESS RESULT: PASS`. `ACQUISITION-STATE: FAIL` is expected — it
is the count of open decisions, not a defect (see the generated report).

### 3. Build

One BitBake per build directory (R3'); separate directories may run
concurrently. `BB_NUMBER_THREADS=10` / `PARALLEL_MAKE=-j 12` per directory (R6').
`tools/symonbake <Runtime> <targets...>` enforces the one-cooker rule with a
lock; `tools/build-all` sweeps the runtimes.

```sh
cd ~/symoneural-bootstrap-master
source openembedded-core/oe-init-build-env \
    /home/google/SymonSaysLLC/Symoneural-Ravencalc/build/devtool-master
bitbake symoneural-numpy symoneural-sympy symoneural-mpmath symoneural-openblas
```

Packages land in `tmp/deploy/ipk/`.

> **Before editing any recipe or class**, run `tools/edit-guard` and check its
> exit code directly (0 = quiescent, 1 = a cooker is live, 2 = could not check —
> treat as live). Editing while a cooker is live makes BitBake reparse mid-run
> and abort with `the basehash value changed ... metadata is not deterministic`.
> That has cost two full build runs here; the guard makes it mechanical rather
> than remembered.

### Known limitations

- **Not relocatable.** `SYMON_TREE` in every recipe, both classes, the conf
  templates and every build directory's `bblayers.conf`/`local.conf` carry
  `/home/google/SymonSaysLLC/...` (over 100 tracked files under
  `meta-symoneural/` alone). Phase 19f (`TEMPLATECONF` + `symonbuild`) is where
  that is fixed. Until then, clone to `/home/google/SymonSaysLLC` or rewrite the
  paths.
- **`DISTRO` is not set** in any build directory, so
  `meta-symoneural/conf/distro/symoneural.conf` has never been loaded; the
  estate-wide settings it should own live in each `build/*/conf/local.conf`
  (untracked). Recorded as a phantom completion under R16; fixing it is a
  release prerequisite.

## Install pre-built packages

See **[INSTALL.md](INSTALL.md)**. No release is published yet — the first
requires `packagegroup-symoneural-rack`, which has not been written.

## Design rules

- **R1** never write into acquired source. Builds export a disposable
  `git archive` copy; the acquired tree is never opened for writing.
- **R11** no recipe uses `externalsrc`. `${S}` is a disposable export asserted
  equal to `SRCREV`; `B` is always out of tree.
- **R12** an empty `${D}` after `do_install` is a FAILURE, not a silent pass.
- **R16** declared is not done. An item is DONE only when its artifact exists on
  disk or a consumer has exercised it, and the report names the evidence.

R16 exists because three things were reported complete here that had never
executed: a Fortran runtime that was never built, a distro config that was never
loaded (still true — see above), and assertion tasks whose names never bound.
Each was caught by something downstream finally needing it.

## Licence

Per-component licences are recorded in `acquisition/license-inventory.json`
(568 licence-bearing files at the last render) and declared per recipe in
`LIC_FILES_CHKSUM`. Upstream components retain their own licences. **The
first-party code has no licence file yet** — `symoneural-api` declares `CLOSED`,
`libsymoneural-llm` declares `MIT`; reconciling that is a release prerequisite.
