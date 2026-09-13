# SyMoNeuRaL

A multi-runtime software estate built from **pristine upstream source** with
BitBake/OpenEmbedded. Every component is pinned to a commit, built from that
commit, and refuses to build if the tree has drifted.

**Status: Phase 10 of 19 complete.** 16 recipes build clean. This is an estate
under construction, not a finished product.

## What this repository is

Work product only — **231 files, ~12 MB**:

| Path | What |
|---|---|
| `meta-symoneural/` | the OE layer: recipes, `symoneural-pristine.bbclass`, distro config |
| `acquisition/` | the control plane: source locks, dependency graph, licence inventory |
| `tools/` | scanners, the acquisition verifier, `edit-guard`, the pre-publish audit |
| `generated/` | phase reports — the estate's own build record |

## What it is NOT

**No build output.** ~146 GB of it is gitignored, and that is deliberate:

```
Symoneural-*/build        101G      derived from recipes + pins
Symoneural-*/downloads     22G      refetchable from SRC_URI
Symoneural-*/src           16G      upstream source, pinned in acquisition/source-lock.json
Symoneural-*/sstate-cache 8.3G      derived (protected on disk by R10, not in git)
                          ----
tracked                     12M
```

The recipe is the truth; a build is one instance of executing it. If the output
had to be committed to be preserved, the estate would not be reproducible — and
reproducibility is the whole point.

**No upstream source.** 41 acquired trees are pinned by `commit_sha` in
`acquisition/source-lock.json`. They belong to their upstreams.

**No secrets, ever.** `/etc/symoneural/*.env` is root-owned `0600` outside this
repo (R13). A full-history scan found none; `.gitignore` and
`tools/pre-publish-audit.sh` keep it that way by construction.

## Build from source

### 1. Bootstrap

See **[BOOTSTRAP.md](BOOTSTRAP.md)** — three `git clone` + `git checkout <SHA>`
commands. Required; the estate references it by absolute path.

### 2. Acquire the pinned sources

Per **A7**, acquisition happens inside the phase that builds a component, from
`acquisition/pending-acquisitions.json`. Nothing is cloned ahead of its build.
Verify what you have:

```sh
python3 tools/verify-acquisition.py
```

Expect `CONTROL-PLANE RESULT: PASS` and `ESTATE-COMPLETENESS RESULT: PASS`.

### 3. Build

One BitBake per build directory (R3'); separate directories may run
concurrently. `BB_NUMBER_THREADS=10` / `PARALLEL_MAKE=-j 12` per directory (R6').

```sh
cd ~/symoneural-bootstrap-master
source openembedded-core/oe-init-build-env \
    /home/google/SymonSaysLLC/Symoneural-Ravencalc/build/devtool-master
bitbake symoneural-numpy symoneural-sympy symoneural-mpmath symoneural-openblas
```

Packages land in `tmp/deploy/ipk/`.

> **Before editing any recipe**, run `meta-symoneural/tools/edit-guard`. Editing
> while a cooker is live makes BitBake reparse mid-run and abort with
> `the basehash value changed ... metadata is not deterministic`. That has cost
> two full build runs here; the guard makes it mechanical rather than remembered.

### Known limitation

`SYMON_TREE` and `bblayers.conf` carry `/home/google/SymonSaysLLC/...` in 89
tracked files, so **the recipes do not relocate as-is**. Phase 19f
(`TEMPLATECONF` + `symonbuild`) is where that is fixed. Until then, clone to
`/home/google/SymonSaysLLC` or rewrite the paths.

## Install pre-built packages

See **[INSTALL.md](INSTALL.md)**. No release is published yet — the first
requires `packagegroup-symoneural-rack` (Phase 11d).

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
loaded, and assertion tasks whose names never bound. Each was caught by something
downstream finally needing it. `generated/phase-10-report.md` records all three.

## Licence

Per-component licences are recorded in `acquisition/license-inventory.json`
(430 files) and declared per recipe in `LIC_FILES_CHKSUM`. Upstream components
retain their own licences.
