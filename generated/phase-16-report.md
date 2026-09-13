# PHASE 16 — Studio and Reinforce as a live unit

## STATUS: PENDING — NOT STARTED

**starts after: Phase 13 gate**

> **ORDERING (O1).** Each phase's own "Start after" line is authoritative. The
> QUEUED headers' serial chain was a paste convenience and is **WITHDRAWN**.
> Dependency graph:
>
> ```
> 10 → 11 → { 11-T, 18 }
> 11 → 12 → { 13, 14, 17 }
> 13 → 16          14 → 15          { 15, 16, 18 } → 19
> ```
>
> Builds run **concurrently in separate build dirs** when dependencies are met
> (R3', R6'). GPU PROOF steps (12f, 13e/13f, 14e, 16 runs, 17e) execute **one at a
> time through the governor** — train is never evicted, so a 13e run finishes
> before 14e's contention test starts.


Queued 2026-09-13 by Garrett with "QUEUED — do not start." Spec verbatim below.
Nothing built, trained, evaluated or promoted.


Milestone: a full `sft` preset runs from the rack, passes evaluation, and is
promoted to serving by configuration.

---

## SETTLED

- **S1** `train` is never evicted.
- **S2** Promotion by `units.json`, **never** by copying into a source tree.
- **S3** MCP server is **python-sdk**; `fastmcp` not acquired.
- **S4** Corpus: path and sha256 only.
- **S5** The 27B adapter **IS** evaluated on the Q2_K_XL base; an unevaluated
  adapter is never served (**label measured, never projected**).

## ITEMS

- **16a** `Symoneural-Studio/app/`: registry (HF cache + GGUF dir), presets
  (smoke, voice, recall, longform, prefer=DPO, reward=GRPO, probe), VRAM planner
  validated against measured **7B ~12 GB** and **27B 14.26 GiB**, job runner under
  `with train`, outputs `run/reinforce/adapters/<job>`.
- **16b** Evaluation harness: held-out prompts by corpus path, perplexity and
  behaviour probes, thresholds as **measured** baselines.
- **16c** Export to GGUF; promote via `units.json`; Chat reloads.
- **16d** Agent loop on python-sdk; `run_command` and `write_file` confined to
  `Symoneural-Studio/work/`; token-gated (user level or above).
- **16e** Exp plugin runtime packaged; hot-reload double-run fixed with a test.
- **16f** `studio` unit with `reinforce` (gpu) and `exp` (cpu) sub-units; page.
- **16g** Evaluate the 27B adapter with 16b; serve only if it passes; record
  either way.

## GATE

One `sft` run from the UI produces an adapter that passes 16b and is served; a
chat request during training reports **queued, never evicts**; 16g recorded.

## COMMIT

`phase 16: Studio live — training bay, eval harness, promotion by config, MCP on python-sdk`

## RETURN

- RUN preset, steps, wall time, peak VRAM; EVAL metrics vs baseline
- PROMOTE adapter sha256 served YES/NO; AGENT tools, confinement test
- 27B evaluated: PASS / FAIL with numbers

---

## NOTES CARRIED IN FROM EARLIER PHASES

**S3 is already satisfied and proven.** `symoneural-mcp-python-sdk` builds clean
(`rc=0`) at PV **2.2.0**. Its TypeScript sibling was recorded **REFERENCE-ONLY**
in Phase 10 — *"pnpm catalog: protocol unsupported by npm / OE npm class"* — and
S3's choice of the Python SDK is exactly the decision that makes that harmless.
`fastmcp` is not acquired and, per A7, must not be cloned ahead of a phase that
builds it.

**S4's "path and sha256 only" matches the model register posture.**
`SYMON_MODELS_DIR = /home/google/symoneural-models` exists with `hf/ image/ llm/
rembg/ whisper/` — **all empty, 24K total** as of Phase 10. Weights never enter
git.

**S1 aligns with PRECEDENCE in COMMON:** *train is never evicted; miner yields to
everything; CPU and NET units never take the lock.*
