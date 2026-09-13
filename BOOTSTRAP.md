# BOOTSTRAP — what this repository does NOT contain

This repository is SyMoNeuRaL **work product only**: curated recipes, the
`meta-symoneural` layer, the acquisition control plane, the scan tools and the
phase reports. **231 tracked files, ~12 MB.**

Three things it deliberately does not contain, and you need all three to build.

## 1. The BitBake bootstrap — required

Every `bblayers.conf` in this estate references these by **absolute path**. They
are pinned; do not take whatever `master` happens to be today.

```sh
mkdir -p ~/symoneural-bootstrap-master && cd ~/symoneural-bootstrap-master

git clone https://git.openembedded.org/bitbake            bitbake
git -C bitbake            checkout 046a90b0e9b7b914b7a95aec579cdc3fc9c7617a

git clone https://git.openembedded.org/openembedded-core  openembedded-core
git -C openembedded-core  checkout fe7a24bc67118e7e184b5f5247258715e3904e7c

git clone https://git.openembedded.org/meta-openembedded  meta-openembedded
git -C meta-openembedded  checkout 43b79d8e372c4f69ebab6c85b39d97b41522080f
```

`meta-openembedded` is **not optional** — `meta-oe` provides `nodejs` (for the
npm recipes) and `meta-python` provides `python3-pybind11` and
`python3-pydantic-core`.

Not vendored and not a submodule: it is 405 MB of upstream history that is
perfectly reproducible from three SHAs, and copying it would make this repo
30× larger while adding nothing.

## 2. Acquired upstream source — reproducible from the lock

41 upstream trees under `Symoneural-*/src/*/source/` are gitignored. Each is
pinned in `acquisition/source-lock.json` by `commit_sha`, with submodules pinned
in `submodule-lock.json`. They are upstream code, not ours; republishing them
would be redundant and would obscure what is actually SyMoNeuRaL's work.

`symoneural-pristine.bbclass` asserts each tree's `HEAD == SRCREV` at unpack and
**refuses to build a tree that has drifted from its pin**.

## 3. Secrets — and they are never coming in here

`/etc/symoneural/*.env` is root-owned `0600`, provisioned by
`/usr/local/sbin/symoneural-secrets`, and lives outside this repository by design
(R13). Only `/etc/symoneural/manifest.json` is ever read, and only for key
**names** and set/unset **status** — never values.

A full-history scan (every commit, all 231 paths ever added) found no `.env`,
key, or credential file, and no secret-shaped assignment. `.gitignore` now denies
them by pattern so that remains true by construction rather than by anyone
remembering.

Model weights (`SYMON_MODELS_DIR=/home/google/symoneural-models`) also never
enter git.

## Known limitation: absolute paths

`SYMON_TREE` and `bblayers.conf` carry `/home/google/SymonSaysLLC/...` in 89
tracked files. **The recipes will not work from a different checkout location
as-is.** This is honest rather than hidden: the estate is built on one host by
design, and Phase 19f (`TEMPLATECONF` + the `symonbuild` launcher) is where it
becomes relocatable. Until then, clone to `/home/google/SymonSaysLLC` or expect
to rewrite those paths.

## Host this was built on

RTX 5070 Ti (Blackwell, sm_120), driver 615.71.09, CUDA 13.4, 20 cores,
31 GiB swap. `BB_NUMBER_THREADS=10` / `PARALLEL_MAKE=-j 12` per build directory.
