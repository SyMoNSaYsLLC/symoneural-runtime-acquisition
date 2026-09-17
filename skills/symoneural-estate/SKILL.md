---
name: symoneural-estate
description: Rules, invariants and known failure modes for the SyMoNeuRaL multi-runtime estate built with BitBake/OpenEmbedded. Use when working in the SymonSaysLLC repository, writing or editing meta-symoneural recipes, running bitbake builds, handling estate secrets, committing to the estate repo, or reporting whether estate work is complete.
---

# SyMoNeuRaL estate

A multi-runtime software estate built **from pristine upstream source** with
BitBake/OpenEmbedded. Thirteen runtime directories, 100 pinned upstreams
(`acquisition/source-lock.json` is the count that is true; this line is not),
one GPU.

Everything below was paid for with a failure. Follow it exactly.

---

## R16 — DECLARED IS NOT DONE

**The single most important rule.** An item is done only when **its artifact
exists on disk, or a consumer has exercised it** — and the report names the
evidence: a path, a hash, a `bitbake -e` line, or the consuming task that
succeeded.

A report saying "complete" is not evidence. Neither is a plan, a commit message,
or your own recollection of doing it.

### The three phantom completions that produced this rule

| Declared done | Actually true | How it surfaced |
|---|---|---|
| Fortran runtime | never built | scipy's meson sanity check needed it |
| `symoneural.conf` | never loaded — no `local.conf` sets `DISTRO` | nothing in it ever took effect |
| assertion tasks | defined, never bound into the task graph | the Phase 10 gate looked for their output |

**None was caught by a check run at the time. All three by something downstream
needing them.** That is the pattern to defeat: verify at the time, against disk.

This applies to your own tooling too. A guard script recorded as built was not on
disk; the check that "confirmed" it read `$?` from a pipeline rather than from the
guard, so it reported success while the file was missing.

---

## Hard rules — never violate

| | Rule |
|---|---|
| **R1** | **Never write into any `src/*/source` tree.** Acquired upstream source is read-only. `${S}` is a disposable `git archive HEAD` export. |
| **R2** | **Never edit recipes while a bitbake cooker is live.** Run `tools/edit-guard` — it exits 1 if one is. Check its exit code directly, never through a pipeline. |
| **R10** | **`sstate-cache` is a protected asset.** Never delete it to recover disk. |
| **R13** | **Never prompt for, generate, or commit a secret.** Fingerprints only. `symoneural-secrets status` prints names and fingerprints, never values. |
| **R14** | **`127.0.0.1:8800` is read-only and demo-critical.** Never stop, restart, edit or redeploy it. |
| — | **Never `git add .` or `git add -A`.** Explicit path sets only. |
| — | **Weights never enter git.** Any format, any size. |
| — | **Nothing from August.** August-era artifacts predate the fresh start. |

`git add .` is not a style preference: `developer_settings.json` holds a live API
key, weights are multi-GB, and `build/` holds hundreds of thousands of files. Run
`tools/pre-publish-audit.sh` before any push.

---

## BitBake traps that have actually bitten

**`addtask foo` binds to a function named `do_foo`.** A task function without the
`do_` prefix is silently never bound. This produced one of the three phantoms —
assertion tasks existed, were never in the task graph, and "passed" for weeks.

**`git archive` honours `.gitattributes export-ignore`.** An export is **not**
always a full copy of the worktree. scikit-learn marks `build_tools` export-ignore,
so `LIC_FILES_CHKSUM` entries naming files there fail `do_unpack` permanently.
mpmath has no export-ignore and matched exactly (248 == 248 == 248), which is what
made "exports are complete" look like a rule. It is not.

**An empty `PYTHONPATH` entry means the current directory.**
`python3targetconfig.bbclass` writes `...python-sysconfigdata:$PYTHONPATH`; with
`PYTHONPATH` unset that leaves a trailing colon. In scipy's source tree that put
`scipy/signal/` ahead of the **stdlib** `signal` that `subprocess` imports, and the
error named a completely different module. `PYTHONSAFEPATH=1` does **not** fix it —
it governs `sys.path[0]` only.

**`set -u` kills `oe-init-build-env`.** It references unset variables internally.
Symptom is the misleading part: an empty build log and `rc=1` with zero ERROR
lines, because the build never started.

**`RUNTIMETARGET` does not include `libgfortran`.** Enabling FORTRAN builds the
compiler, not its target runtime. `gfortran` then works standalone and fails only
*with* `--sysroot`, so a bare compile test passes and hides it.

**`LicenseRef-*` SPDX tokens require an actual text file** or `do_create_spdx`
fails.

**npmsw `;dev=1` is a URI parameter**, distinct from the `NPM_INSTALL_DEV` recipe
variable.

**Stale caches impersonate live defects.** autoconf `(cached) no`, sstate
poisoning, meson build-dir state. Before diagnosing a defect, rule out a cache.

---

## Verification discipline

Prefer a command that reads disk over a document that describes disk.

```sh
tools/edit-guard                 # is a cooker live? (check $? directly)
tools/pre-publish-audit.sh       # secrets / weights / size, before any push
symoneural-secrets status        # names + fingerprints, never values
tools/check-history.sh <term>    # has this failed before?
```

The MCP server exposes `verify_claim`, which is R16 as a callable — it checks a
claim against the filesystem rather than against a report.

**Reproduce before theorising.** A hypothesis that does not reproduce is wrong, no
matter how good the story is. Bisect at the exact failing conditions — same
binary, same cwd, same environment — and change one variable.

---

## Where truth lives

| Question | Authoritative source |
|---|---|
| What is done? | `generated/phase-NN-report.md`, **and only if the artifact exists** |
| What changed, when? | `git log` |
| What is pinned? | `acquisition/*.json` — SHA pins, never tags |
| Does this claim hold? | `verify_claim`, or a shell command |

**Sequence is not status.** Phase dependencies are structural and cannot go
stale; status views drift the moment work lands. A duplicated task list once
diverged from the canonical one and an agent executed the retired copy. If two
documents disagree, the repository wins.

---

## Reporting

State what was verified and how. If a fix is applied but not yet exercised, say
exactly that — "applied and reasoned, not yet run" is a complete and honest
status, and it is what R16 requires.

If tests fail, say so with the output. If a step was skipped, say so. Never
soften a partial result into a completed one.
