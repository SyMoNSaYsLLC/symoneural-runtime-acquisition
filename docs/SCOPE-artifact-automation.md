# SCOPE — artifact / repo drift automation

**Status: SCOPED, NOT BUILT.** This is a design for review, not a plan of record.
Nothing here has been implemented.

---

## The problem, with evidence from right now

The published artifact says **"41 recipes in meta-symoneural."** Disk has **39**
`.bb` files and zero `.bbappend`. Found in one command, in a document that is
otherwise carefully written and was republished today.

That is the whole case. Hand-maintained numbers describing a repository drift from
the repository, silently, and the drift is invisible because the prose around it
stays plausible.

The estate already has fifteen machine-readable sources that could have answered
it correctly:

```
acquisition/source-manifest.json     44 entries, keys include component,
                                     intended_revision, revision_authority,
                                     acquisition_state
acquisition/source-lock.json         census + components
acquisition/provider-decisions.json  decisions, not_acquired, pending_collisions
acquisition/license-inventory.json   files
acquisition/model-register.json      rows, provenance
acquisition/unresolved.json          counts, items, resolved
... 9 more, each carrying `schema` and most carrying `provenance`
```

---

## The line that must not be crossed

**Generate facts. Never generate status.**

An auto-regenerating document that emits "Phase 11: in progress" is a status board
that updates itself into being wrong — the `PROJECT-TASKS.md` / `CODER-TASKS.md`
failure with a cron job attached. R16 is the constraint: a generator cannot
establish that an artifact exists on disk or that a consumer exercised it, so it
must not claim either.

| Safe to generate — derivable and checkable | Must stay hand-written |
|---|---|
| recipe counts, per-layer | "Phase N is in progress / complete" |
| pin table: component → SRCREV, tag, authority | any gate assertion |
| licence inventory | anything about intent or rationale |
| phase **sequence** and dependencies (structure) | phase **status** |
| open-decision count from `unresolved.json` | why a decision went the way it did |
| host facts (GPU, OE-Core SHA, BitBake SHA) | "this works" |
| generation timestamp + commit hash | — |

Every generated fact carries its source path inline, so a reader can check it
without trusting the generator.

---

## Hard constraint that shapes the whole design

**GitHub Actions cannot publish the artifact.** Publishing goes through the
Artifact tool, which exists in an assistant session, not in CI. There is no token
or endpoint a workflow could use.

So "artifact auto-updates on push" is **not achievable**, and any design promising
it is wrong. What is achievable is drift *detection* plus deterministic
*regeneration*, with publication staying an explicit act.

---

## Proposed design

### 1. `tools/gen-artifact-facts` — deterministic fact blocks

Reads `acquisition/*.json`, counts files on disk, reads `git rev-parse`, and emits
HTML fragments into **marked regions** of `docs/build-manuals.html`:

```html
<!-- GENERATED:pins BEGIN  source=acquisition/source-manifest.json -->
  ...table...
<!-- GENERATED:pins END -->
```

Only content between markers is touched. Prose outside them is never rewritten —
that is what keeps the document authored rather than assembled.

Same marker discipline as `tools/gen-handbook`, which deletes only files carrying
its own marker rather than by filename pattern.

### 2. `tools/check-artifact-drift` — the actual value

Regenerates into a temp copy, diffs against the committed file, exits non-zero on
difference. Run it three ways:

- **locally** before publishing
- **in `.github/workflows/`** on push and PR — no repo exists there today, so this
  is the first workflow
- **from `tools/pre-publish-audit.sh`**, which already gates pushes

This is the piece that would have caught 41-vs-39 the day it drifted.

### 3. Publication stays manual

I regenerate, review the diff, and publish to the existing artifact URL. A human
or assistant decides that the document is *right*, not merely *current*.

---

## What this does not do, deliberately

- **Does not touch the phase reports.** They are the status record and stay
  hand-written under R16.
- **Does not invent a second source of truth.** The repo is authoritative; the
  artifact becomes a *view* of it for the generated regions only.
- **Does not auto-publish.** See the hard constraint.
- **Does not read `/etc/symoneural`.** No secret, fingerprint or filename from the
  secrets store enters a published document.

---

## Cost and risk

**Cost:** roughly a day. The generator is mechanical; the care goes into choosing
marker boundaries so prose and facts do not interleave badly.

**Risk, and it is real:** marked regions make the document partly generated, and a
future editor may not notice the markers and hand-edit inside one, losing the edit
on the next run. Mitigations: loud comment markers, and `check-artifact-drift`
failing on any in-region hand edit — the same failure surfaces as a CI error
rather than as silent loss.

**Second risk:** scope creep into status. The table above is the boundary. If a
future version starts emitting phase status, it has become the thing it was built
to prevent.

---

## Decision needed

1. Build it, or fix 41→39 by hand and revisit when drift recurs?
2. If built — is a `.github/workflows/` file wanted? There is no CI in this repo
   today, and adding one is a standing commitment, not a one-off.
