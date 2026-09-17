# BOOTSTRAP — what this repository does NOT contain

This repository holds SyMoNeuRaL work product — curated recipes, the
`meta-symoneural` layer, the acquisition control plane, the scan tools, the
phase reports, the first-party `app/` trees — **and** every acquired upstream
source tree at its pinned commit (SOURCES-100, 2026-09-13; ~291,000 tracked
files, ~8 GB of history). The sections below list what it deliberately does
not contain. You need the first to build at all.

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

## 2. The pin stores — `.gitpins/`, never pushed

The 100 upstream trees under `Symoneural-*/src/*/source/` **are committed** (the
policy at the top of `.gitignore`; the earlier rule that gitignored them was
withdrawn on 2026-09-13 — `docs/OBJECTIVE-100-PERCENT-SOURCES.md`). What is not
in git is each tree's own `.git`, moved beside it into `.gitpins/<name>.git`.
Those pin stores are local provenance and are **not needed to verify**:
`tools/ingest-tree verify <component>` (or `--all`) compares
`git rev-parse HEAD:<source_path>` with the lock's `tree_sha` — for trees with
submodules it rebuilds upstream's tree in memory with the recorded gitlinks —
and reports `· VERIFIED` when the committed files equal upstream's tree object.
The lock and the clone are enough.

Each component is pinned in `acquisition/source-lock.json` by `commit_sha` and
`tree_sha`, with submodules pinned in `submodule-lock.json`. A pin store is
only needed to *ingest* a new or moved pin; on a fresh clone it is recreated by
cloning upstream at the recorded commit, as the acquisition procedure does.

`symoneural-pristine.bbclass` exports `${S}` from the object store at
`SRCREV`, asserts `SRCREV == source-lock.json commit_sha` at unpack, and
**refuses to build a tree that has drifted from its pin**.

## 3. Secrets — and they are never coming in here

`/etc/symoneural/*.env` is root-owned `0600`, provisioned by
`/usr/local/sbin/symoneural-secrets`, and lives outside this repository by design
(R13). Only `/etc/symoneural/manifest.json` is ever read, and only for key
**names** and set/unset **status** — never values.

`tools/pre-publish-audit.sh` scans every commit for secret-shaped filenames and
content (outside the verified upstream trees, whose test fixtures are upstream's
bytes) and runs before every push; `.gitignore` denies the known shapes by
pattern so the result stays true by construction rather than by anyone
remembering. The one live credential on this host is
`~/.config/Claude/developer_settings.json`, outside the repository and denied by
name — it is the reason `git add .` is banned here.

Model weights (`SYMON_MODELS_DIR=/home/google/symoneural-models`) also never
enter git.

## Known limitation: absolute paths

`SYMON_TREE` in every recipe, both estate classes, the conf templates and every
build directory's `bblayers.conf`/`local.conf` carry `/home/google/SymonSaysLLC/...`
(over 100 tracked files under `meta-symoneural/` alone; the build-directory
confs are untracked). **The recipes will not work from a different checkout
location as-is.** This is honest rather than hidden: the estate is built on one host by
design, and Phase 19f (`TEMPLATECONF` + the `symonbuild` launcher) is where it
becomes relocatable. Until then, clone to `/home/google/SymonSaysLLC` or expect
to rewrite those paths.

## Host this was built on

RTX 5070 Ti (Blackwell, sm_120), driver 615.71.09, CUDA 13.4, 20 cores,
31 GiB swap. `BB_NUMBER_THREADS=10` / `PARALLEL_MAKE=-j 12` per build directory.
