# GitHub

## Accounts

| Account | Role |
|---|---|
| `https://github.com/SyMoNSaYsLLC` | **Organisation.** Owns the product repos. |
| `https://github.com/gpmcdonald` | **Personal.** Commit identity (`git config user.name`). |

Verified on disk — the single remote:

```
origin  https://github.com/SyMoNSaYsLLC/symoneural-runtime-acquisition.git
```

Repo is **private**, hardened as though public, because — your words —
*"treat it like you would if its public because you never know."*

## The rule that is not negotiable

**Never `git add .` or `git add -A`.** Explicit path sets only:

```sh
git add meta-symoneural/recipes-ravencalc/symoneural-scipy/symoneural-scipy_git.bb
```

This is not stylistic. `developer_settings.json` contains a live API key, weights
are multi-GB, and `build/` holds hundreds of thousands of files. A single `add .`
at the wrong moment commits all three. `.gitignore` is a backstop, not the
control.

## Before any push

```sh
/home/google/SymonSaysLLC/tools/pre-publish-audit.sh
```

Scans for secrets, model weights and oversized blobs. It exists because the
near-miss already happened once: `inferenceGatewayApiKey` was one `git add .`
away from being committed.

## What never enters git

- **Model weights.** Any format, any size. GGUF, safetensors, `.bin`.
- **`build/`, `tmp/`, `sstate-cache/`, `downloads/`.**
- **Anything under `~/symoneural-ops/`** — includes `claude-org-members.csv`,
  which is other people's personal data (`0600`, dir `0700`).
- **Any credential.**

## NOT STARTED

The second account (`gpmcdonald`) is the commit identity but has no repo of its
own in this project. Multi-account `gh` auth switching is **not configured** —
`gh auth switch` has never been run here. If you want both accounts usable from
one shell, that is a real task, not a setting.
