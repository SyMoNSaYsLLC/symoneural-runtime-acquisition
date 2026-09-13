# SyMoNeuRaL Phase 10 Report

## DECISIONS CLEARED — actioned

| # | Decision | Action taken |
|---|---|---|
| 1 | FORTRAN estate-wide | `FORTRAN:forcevariable = ",fortran"` + `RUNTIMETARGET:append:pn-gcc-runtime = " libquadmath"` in Ravencalc `local.conf` (moves to `meta-symoneural/conf/distro/symoneural.conf` in 10a). **gcc-cross-x86_64 + gcc-runtime rebuilding now**; sstate rsync to `/home/google/sstate-backup` is chained to completion (R10). |
| 2 | TypeScript SDKs + hls.js | Deferred to Phase 10e as instructed. Old Phase 6 dissolved, not started. |
| 3 | Models register | **All three probes ABSENT.** Search run, nothing found, consolidation NOT performed, stopped looking. |
| 4 | Rust / LLVM 23 | Allowed to finish; paid once. sstate treated as protected (R10) — never deleted to recover disk. |
| 5 | Pristine policy | Noted: externalsrc retired in Phase 10 via `symoneural-pristine.bbclass`. Awaiting the pasted spec. |
| 6 | Acquisition pace | `acquisition/pending-acquisitions.json` written — **14 rows, 13 RELEASE + 1 SNAPSHOT**, CURATED, none acquired. |
| 7 | Sequence | Phase 5 and the Fortran rebuild are running; old Phase 6 and Phase 9 NOT started. |

## TWO PREMISE CORRECTIONS

**R6 says "the box has 0 swap".** It has **31 GB**, with 16/94 GB RAM in use.
The hard-freeze hazard R6 guards against is not present, which is why the Fortran
rebuild could safely start alongside a nearly-finished Phase 5.
`BB_NUMBER_THREADS = "10"` retained regardless — the setting is cheap and harmless.

**A1 asks for the latest STABLE release tag; stable-diffusion.cpp has none.**
Its tags are `master-<N>-<sha>`, generated per commit. Recorded as
`tag_kind: SNAPSHOT`, `master-859-7f410a3` → `7f410a37` — a commit snapshot, not a release.

## MODELS — ABSENT

| File | Runtime | State |
|---|---|---|
| `flux1-schnell-q4_k.gguf` | Diffuse | **ABSENT** |
| `Qwen2.5-7B-Instruct-Q4_K_M.gguf` | LLM | **ABSENT** |
| `ggml-base.en.bin` | Diffuse | **ABSENT** |

`find /home/google -xdev` returned no matches. The old deployment's `backend/models`
is not on this host. Nothing moved, nothing copied. **Garrett answers where they are.**

## COLLISIONS RECORDED BEFORE ACQUIRING (A3)

**ggml will exist three times** once Diffuse is acquired — llama.cpp (LLM, ggml-org),
whisper.cpp (Diffuse, ggml-org), stable-diffusion.cpp (Diffuse, **leejet/ggml, a personal
fork**). Two upstreams, three copies. `CROSS-RUNTIME-DUPLICATE`, decision `UNRESOLVED`.

**ComfyUI: NOT ACQUIRED** — GPL-3.0-or-later, replaced by diffusers (Apache-2.0).

## AWAITING

Phase 10's specification has not been pasted. `symoneural-pristine.bbclass`,
`meta-symoneural`, and 10a–10e are not started.
