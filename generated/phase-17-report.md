# PHASE 17 — Crypto and Miner: Stratum V2 on the LAN, a GPU miner that yields

## STATUS: PENDING — NOT STARTED

**starts after: Phase 12 gate**

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
Nothing acquired, built, started or mined. Per A7, `kawpowminer` and `pyasic` have
NOT been cloned.


Milestone: pool and translator run from estate binaries, an SV1 miner connects
through the translator, and the GPU miner yields the card to Chat within seconds.

---

## SETTLED

- **S1** GPL-3 miners are **separate processes, never linked**.
- **S2** Pool and wallet come from `miner.env` (`SYM_MINER_POOL` /
  `SYM_MINER_WALLET`). Unset → **benchmark only**; mining stays off; **no question
  returns**.
- **S3** The governor becomes a **daemon**: UNIX socket API, holder registry,
  eviction hooks, drain, the yield protocol from `docs/specs/miner-preemption.md`.
- **S4** Acquire here (A7): `kawpowminer` (GPL-3, own `src/gpu`), `pyasic`
  (licence characterised from the tree).

## ITEMS

- **17a** sv2-apps pool, translator, JD as LAN-bound services from templates.
- **17b** `kawpowminer` against the **estate** CUDA for sm_120; process boundary
  recorded.
- **17c** `pyasic` control service; scan **opt-in, private ranges only**.
- **17d** `symoneural-governor` daemon per S3; dispatch and launch paths switch to
  the socket; the mkdir mutex stays as **crash-safe fallback**.
- **17e** Yield test: kawpowminer in benchmark under `with miner`; request
  `/api/chat`; measure request-to-chat-holds-the-card.

## GATE

SV1 test miner (or the QEMU Antminer board) authenticates through the translator;
kawpowminer hashes and **yields in under 15 s measured**; **no wallet string in
the tree**.

## COMMIT

`phase 17: Stratum V2 services; governor daemon with yield; GPU miner as separate process`

## RETURN

- ACQUIRED two: tag → SHA, licences as read
- SV2 up / SV1 accepted; MINER MH/s and yield time measured
- GOVERNOR socket calls served, fallback exercised
- DECISIONS FOR GARRETT: none

---

## NOTES CARRIED IN FROM EARLIER PHASES

**S2's keys are the four that are UNSET.** `/etc/symoneural/manifest.json` records
`SYM_MINER_POOL` and `SYM_MINER_WALLET` as `status: unset`, with
`units_that_stay_off_until_set` naming them *"real mining (benchmark still works)"*
and *"real mining"*. So **by R13 this phase's mining path is configured OFF from
the start**, and S2's "benchmark only, no question returns" is the already-correct
state — not something to be worked around. `SYM_MINER_ENABLED` and
`SYM_MINING_ENABLED` exist; `SYM_MINER_TOKEN` is set.

**17a's dependency is already built.** `symoneural-stratum` builds clean at PV
**1.11.1** and installs **16 rlibs** into `${PN}-staticdev` per R12' — the SV2
protocol libraries (codec, framing, mining, noise, channels, handlers, parsers,
job_declaration, template_distribution, sv1_api, binary, buffer, common_messages,
extensions) plus `stratum_core` and `stratum_translation`. Its crate closure was
confirmed AUTHORITATIVE in Phase 10: regenerating it produced a byte-identical
233-entry `.inc`, and every entry traces to one of the tree's two lockfiles.

**`symoneural-sv2-apps` is NOT yet split.** It is one recipe; the layout is two
cargo workspaces holding four binary packages — `miner-apps/{jd-client,
translator}` and `pool-apps/{jd-server, pool}`. Advisor Item 2 said both "one
recipe per workspace" (2) and "four recipes" (4); the conflict is recorded under
DECISIONS FOR GARRETT in the Phase 10 report and is **17a's first task**.

**S1 is consistent with the licensing posture**: GPL-3 is quarantined and never
linked — the same rule that dropped nvidia-settings and ComfyUI from the baseline.
