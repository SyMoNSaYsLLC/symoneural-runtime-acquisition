# PHASE INDEX — SyMoNeuRaL estate

Generated from the report files on disk. **Each phase's own "Start after" line is
authoritative (O1); the QUEUED headers' serial chain is withdrawn.**

## Dependency graph

```
10 ──► 11 ──┬──► 11-T
            ├──► 18 ─────────────────┐
            └──► 12 ──┬──► 13 ──► 16 ─┤
                      ├──► 14 ──► 15 ─┼──► 19
                      └──► 17         │
                                      (19 needs 15, 16 AND 18)
```

Builds run **concurrently in separate build dirs** (R3', R6') once dependencies
are met. **GPU PROOF steps serialise through the governor** — 12f, 13e/13f, 14e,
16's runs, 17e — because a training hold is never evicted, so a contention test
begun during 13e would measure the wrong thing.

## Status

| Phase | Title | Starts after | Status |
|---|---|---|---|
| **10** | Curation and pristine by construction | — | **CLOSED** `1f007af` |
| **11** | RavenCalc 6/6 live; deployment located | Phase 10 gate | **READY — next** |
| **11-T** | DispatchOS as a template instance (+ accounts) | Phase 11 gate | PENDING |
| **12** | CUDA in the estate; Chat live; models register | Phase 11 gate | PENDING |
| **13** | Common: torch with CUDA, Studio proof | Phase 12 gate | PENDING ("its own night") |
| **14** | Diffuse: Image and Sigils; lock under contention | Phase 12 gate | **IN PROGRESS — GATE MET (9.0 s ≤ 13.44 s)**. 14a built and proven in the clean-root harness; weights acquired and pinned; units `image`/`sigils` registered; 14b and 14e not started. Built ahead of its gate, 17 Sep — see the CORRECTION in `phase-14-report.md`. |
| **15** | Gateway and cutover; symoneural.com from the estate | Phase 14 gate | PENDING |
| **16** | Studio and Reinforce as a live unit | Phase 13 gate | PENDING |
| **17** | Crypto and Miner: Stratum V2; GPU miner yields | Phase 12 gate | PENDING |
| **18** | Live, Streamer, Voice: NET and CPU units | Phase 11 gate | PENDING |
| **19** | Tune, Remix, Adaptive-Fabric, contract freeze, closure | 15 + 16 + 18 | PENDING |

**Phase 11 unblocks two phases at once** (11-T and 18); **Phase 12 unblocks three**
(13, 14, 17). After 12 the estate widens considerably and can build in parallel.

## Cross-phase obligations carried forward

| Owed | Phase | Note |
|---|---|---|
| Re-prove offline compile under the shipped class | 19e | `offline-compile` is **RESOLVED-SCOPED**: the Phase 5 proof (102 rlibs, 0 denials) predates `symoneural-pristine`, and `do_fetch[noexec]` meant it was never reproduced under it. **Do not cite those figures as current.** |
| FreeToken on torch 2.14 | 19 S3 | The single open decision. Runs → Adaptive-Fabric proceeds; doesn't → DEFERRED with evidence |
| Split `symoneural-sv2-apps` | 17a | One recipe per cargo **workspace**, packages per binary: `miner-apps/{jd-client,translator}`, `pool-apps/{jd-server,pool}` |
| Retire the five build-tool recipes | 11h | D2: resolve to OE-Core; trees stay pinned REFERENCE-ONLY, **nothing deleted** |
| SBOM scope for hls.js | 15e | Its 1,072-package closure is **BUILD-ONLY**; the shipped artifact is `dist/hls.min.js`. Never claim 1,072 shipped |
| Negative-test the three untested guards | any | cargo closure, licence-files-present, export-non-empty are trusted on "no error appeared" — the reasoning that failed for 31 builds |

## Reference-only components

Acquired and pinned; **not built**. Nothing deleted.

| Component | Reason recorded |
|---|---|
| `mcp typescript-sdk` | "pnpm catalog: protocol unsupported by npm / OE npm class" |
| `workers-sdk` | same; wrangler consumed as the published `wrangler@4.131.1` package (kind PACKAGE) in 15 |
| `anthropic-sdk-typescript` | no consumer; building it forces Node onto the target. Recipe in `meta-symoneural/retired/` |
| `vllm`, `triton` | Phase 13 S2 |
