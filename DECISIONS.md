# DECISIONS

Answers to the four product questions, decided 2026-09-13. Recorded here because
the evidence for them was scattered across a deleted directory, a 62 MB
transcript, a second estate on another partition, and a Drive — and finding it
took four searches. It does not get rediscovered.

Each answer names its evidence. Where a decision overrides a prior instinct, the
reason is stated.

---

## 1. Unit split — who gets what installed

**Operator-only** (never in a tenant's `units.json`, and not installed on a
tenant instance):

```
studio   exp   rack   miner   asic
```

**Tenant-facing:**

```
ravencalc   chat   image   sigils   voice   remix   project   streamer   coder   live
```

Two packagegroups: `packagegroup-symoneural-rack` (tenant) and
`packagegroup-symoneural-operator`. A tenant instance does not merely *hide* the
miner — it does not have the binary.

**Source:** Phase 11-T **S3** names the operator set verbatim — *"Operator
surfaces (Studio, Exp, Rack power, Miner, ASIC) never appear in a tenant's
units.json"*. **S5** places `coder` in the first tenant's units:
*"Units {ravencalc, project, coder, streamer}"*.

**Correction recorded.** An earlier reading put `coder` and `live` in the
operator set, on the strength of a commit message — *"coders: land the
multi-coder surface, and stop it being publishable"*. That was an over-read:
"not publishable" means not served unauthenticated on the public site, which is
not the same as operator-only. The spec is explicit and a commit message is an
inference; the spec wins.

**Why two packagegroups rather than one plus runtime filtering.** Both restricted
surfaces have a demonstrated enforcement bug in this estate's own history:

* `_coder_token()` read `SYMONEURAL_CODER_TOKEN` while the runtime set
  `SYM_CODER_TOKEN` — leaving Coder *"token-less and fail-closed in production"*.
  Fail-closed was luck; the same mismatch inverted is an open door.
* *"Most surfaces deny correctly (project 401, train 503, gateway 503). But
  `/api/exp/state` returns **200**."*

Not installing a binary is stronger than checking a scope before serving it. Same
argument that keeps secrets out of the repo.

---

## 2. Machine and image — feed now, multiconfig at Phase 19

**Now:** install to `Symoneural-API/prod` via the package feed (11d as written).
No MACHINE, no image.

**Phase 19:** multiconfig with `symoneural-x86-64`, `symoneural-x86`,
`symoneural-arm64`, `symoneural-arm`, plus the QEMU targets.

**Source:** Garrett, prior session — *"we need to setup multiconfig so i can have
machine/symoneural-arm64 symoneural-arm symoneural-x86 and symoneural-x86-64 need
to add all the qemu also"*.

**Weighed against failure.** The prior `/yocto` estate had exactly that structure
and it is where that estate died: `build-ai2` and `build-ai4` both failed on
`nvidia-driver-userspace` (SPDX licence text, then firmware architecture), and
`build-ai5` failed at `do_rootfs: Unable to install packages`. Five build cycles
went into the image path and no rootfs came out.

The ambition is kept; its known failure point is deferred until there is a
running system to build an image *of*. 11-T's tenants run as
`symoneural-dispatch@<name>` on this host, so no image is required for the
business case.

---

## 3. Production means COMMISSIONED

Not "cutover", not "public" — **commissioned**, per
`AUTONOMY-TO-PRODUCTION.md`:

* `ops/commission-collect.sh` and `ops/commission-apply.sh`
* a smoke test
* **`RUNBOOK.md` verified by a stranger test, with a pass count**
* an unpadded gap list
* the API running

**Source:** the definition is Garrett's own, from the prior run. Phases 1–6
completed 2026-09-09 and stopped *awaiting the owner* — collect, decide the 502,
apply, one reboot.

Cutover on `:8801` and public serving via the Phase 15 tunnel are **milestones
along the way**, not the finish line. The finish line is a runbook a stranger can
follow.

### The standing-authorisation hazard, recorded

`AUTONOMY-TO-PRODUCTION.md` granted: *"run Phases 2–6 continuously, unattended —
do not stop at phase boundaries, do not stop to ask what measurement can settle,
do not stop because something is slow, **do not stop because a test fails**."*

That instruction is sound on its face. Combined with **no requirement to evidence
completion**, it is the mechanism that produces phantom completions: never stop on
failure, and nothing forces the question *did that actually work?*

Both estates failed this way. The prior run declared six phases complete. This run
declared a gate passed while all three of its assertion tasks were no-ops
(`addtask foo` binds to `do_foo`; the functions lacked the prefix — 31 log files
reading `Function do_symon_assert_nonempty_d doesn't exist`).

**R16 is the counterweight, not a replacement.** "Don't stop" stays; "declared is
not done — name the evidence" is what makes it safe.

---

## 4. Models

**Register and fetch** the seven rows already in `acquisition/model-register.json`.

**Drop:** `Qwen3-32B` (11.9 GB) and `Qwen3-30B-A3B` (10.6 GB). No gate consumes
them. A register listing models nothing uses is the same defect class as a
`LIC_FILES_CHKSUM` naming a path that does not exist — a declaration that cannot
be satisfied.

**`gpt-oss-20b`: acquire, register, DO NOT rebrand, DO NOT default.**

Evidence, from this estate's own history:

* *"gpt-oss needs ~12.8 GiB; only 7.1 GiB is free with Qwen holding 8.3 GiB.
  **They cannot co-reside**"* — on a 16 GB card it does not join chat, it
  **evicts** it.
* *"the Qwen arm ran on the **production** engine (persona adapter, draft model
  for speculative decode, `-c 65536 -np 2`), while gpt-oss ran bare on
  `-ngl 99 -c 8192`. **Not base-vs-base.**"* — the comparison that would justify it
  was never fair.
* It carries its **own LICENSE and USAGE_POLICY**, not Apache-2.0 like the Qwen
  rows.
* It has a `reasoning_effort` control (low/medium/high) that the August benchmark
  never varied.

So: fetch it and record its sha256 so it is reproducible. **Leave `general.name`
alone** — rebranding a model whose licence carries a usage policy is a provenance
claim that buys nothing. Let Phase 16b settle it with a fair measurement: same
engine flags both arms, `reasoning_effort` varied.

An unresolved argument becomes a measurement. That is what the eval harness is for.

### Rebranding, generally

For the Qwen-derived rows, rebranding via `gguf_new_metadata.py` is sound and
already proven here — it writes a **copy**, leaving the validated original
untouched, then atomic-renames.

**Never rewrite `general.architecture`.** `qwen2` and `gpt-oss` are distinct and
`llama-server` exits 1 on a mismatch. Rewrite `general.name` only.

---

## Standing constraint

Every `measured` figure in the models register — 151 tok/s, 8.2 GiB @64K, 768² in
11.2 s, 14.26 GiB peak — was taken on a stack that no longer exists: a different
llama.cpp build, the host CUDA rather than an estate toolkit, and nothing under
`symoneural-pristine`.

They are **targets, not baselines**. Phase 14's GATE says *"within 20% of 11.2 s"*
against a number from a deleted estate. Re-measure; do not inherit. Same posture
as `offline-compile`, which is recorded RESOLVED-SCOPED for exactly this reason.
