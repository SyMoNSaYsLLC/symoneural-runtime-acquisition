# quarantine/

Material moved out of its working location rather than deleted (estate rule:
never delete, move or quarantine and say exactly where it went). Nothing here is
consumed by a recipe, a scanner or a proof. Each subtree records where it came
from, when, and why. Written 2026-09-15 from the records cited; before that date
no file explained this directory.

Tracked-state rule: only this README and `devtool-workspace-2026-09-13/` are
tracked. The other two subtrees are deliberately untracked and must stay that
way — they are exactly what a forbidden `git add .` would sweep into a commit.

| Subtree | Tracked | Origin | Moved | Why |
|---|---|---|---|---|
| `devtool-workspace-2026-09-13/` | yes (114 paths per `git ls-files quarantine/`, 2026-09-15) | `Symoneural-<Runtime>/build/devtool-master/workspace/` for the 13 runtimes (API, Adaptive-Fabric, Build, CLI, Common, Crypto, LLM, Live, Ravencalc, Remix, Streamer, Web; Platform never had one) | 2026-09-13 | Phase 10c migrated every recipe out of the per-runtime devtool `externalsrc` workspaces into `meta-symoneural/` (R11: no recipe uses externalsrc). The retired workspace layers were kept as the pre-migration record. A duplicate `BBFILE_COLLECTIONS` between a retired workspace and a live one had wedged every parse — `generated/phase-10-report.md:239-246` — which is why they were moved out of the build directories rather than left in place. Contents per runtime: devtool `README`, `.devtool_md5`, `conf/layer.conf`, `appends/*.bbappend`, `recipes/*/*.bb`. |
| `repin-2026-09-14/mpmath-1.4.1/` | **no — keep untracked** | `Symoneural-Ravencalc/src/numerics/source/mpmath/` at commit `c1131e2d64ab…` (mpmath 1.4.1) | 2026-09-14 | Ruling A on `sympy-mpmath-constraint` (`acquisition/unresolved.json`, `ruling_2026_09_14`): sympy 1.14.0 declares `mpmath<1.4,>=1.1.0`, so the pin moved to 1.3.0 `b5c04506ef0cd4a1f1213f8389ee21c9c3551582` (`acquisition/source-lock.json`, component mpmath) and the 1.4.1 tree was displaced here. Revisit when a sympy release lifts the `<1.4` bound; then this tree is the candidate to re-ingest. Recorded as intentional in `docs/maintenance/2026-09-14-overnight-platform-and-compile-remaining.md:13`. |
| `residue-2026-09-14/Symoneural-Ravencalc/src/numerics/source/numpy/vendored-meson/meson/mesonbuild/**/__pycache__/*.cpython-314.pyc` | no (ignored by `__pycache__/`) | the pristine numpy tree, same relative paths | 2026-09-14 | R1 residue: a build wrote 149 target-Python-3.14 bytecode files into the acquired numpy tree. The pristine class exports `${S}` from the git object store, so the writer was a host-side invocation of numpy's vendored meson, not a recipe task. The files were moved out (not deleted) so the tree verifies clean again; they are kept as evidence of the breach path. Safe to discard once the cause is recorded in a maintenance note. |

## Rules for this directory

- Do not build from, scan, or `git add` anything under `repin-*/` or `residue-*/`.
- When something new is quarantined, add a row here in the same commit: origin
  path, date, reason, and the record that authorised the move.
- A quarantined upstream tree is still upstream's bytes at a known commit; it is
  not a pin and `acquisition/source-lock.json` must never reference it.
