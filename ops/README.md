# ops/ — operational reference

Material needed to run and configure the estate, as opposed to build it.

## What lives OUTSIDE this repository

| File | Location | Why not tracked |
|---|---|---|
| Claude org members export | `/home/google/symoneural-ops/claude-org-members.csv` | **personal data** — names, emails, roles for other people |
| Provisioned secrets | `/etc/symoneural/*.env` | root-owned `0600`, R13 |
| Model weights | `/home/google/symoneural-models` | size, and licence terms differ per model |

`/home/google/symoneural-ops` is mode `0700`.

### Claude org members export

**Organisation:** `symoneural` (claude.ai)
**Path:** `/home/google/symoneural-ops/claude-org-members.csv`
**Columns:** `Name`, `Email`, `Role`, `Status`, `Seat Tier`
**Current:** 3 member rows, exported 2026-09-13
**Dated snapshots:** `claude-org-members-YYYY-MM-DD.csv` alongside it, so a
refresh never silently overwrites the record of who had access on a given date.

**Used for:** account setup and access decisions during Phase 11-T, where each
customer account is created at a level (`viewer` / `user` / `operator` / `owner`)
and the owner account is bootstrapped from `SYM_OWNER_EMAIL` (R15). Note that
Claude org `Role` and SyMoNeuRaL account `level` are **different systems** — the
CSV informs decisions, it does not drive provisioning.

To refresh: claude.ai → Settings → Organisation → Members → Export CSV, then
save to the path above. **Do not** copy it into the repository tree — `.gitignore`
denies `*members*.csv` by pattern, but the rule exists as a backstop, not as
permission to try.

## What IS tracked here

Non-personal operational data only — e.g. usage or billing exports, which match
`ops/*-usage-*.csv` and are explicitly re-admitted in `.gitignore`.
