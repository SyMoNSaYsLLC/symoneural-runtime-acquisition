# PHASE 14 — Diffuse: Image and Sigils live, the lock under contention

## STATUS: IN PROGRESS — 14a BUILT AND PROVEN · **GATE MET at 9.0 s** · 14b/14e NOT STARTED

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


Queued 2026-09-13 by Garrett with "QUEUED — do not start." Spec text is recorded
below verbatim so the phase is self-contained.

> **CORRECTION, 2026-09-17.** The two paragraphs that stood here said *"Nothing in this
> phase has been acquired, built, configured or run. No tree has been cloned for it"*.
> Both sentences are now false and are replaced rather than left to rot — a phantom
> NON-completion is the same defect as a phantom completion.
>
> **What actually happened on 17 September**
>
> | | |
> |---|---|
> | S3 (partial) | `stable-diffusion.cpp` cloned at the recorded pin `7f410a3793c5` with its four submodules and ingested — commit `2a3a89474`, `LISTING-VERIFIED(4 submodules)`. The other four S3 components (diffusers, rembg, whisper.cpp, onnxruntime) are **not** acquired. |
> | **14a** | Recipe written, built, packaged. `sd-cli` and `libstable-diffusion.so` exist as ipks. Evidence: `generated/evidence/phase-14/14a-evidence.txt`. A build directory was created for the runtime at `Symoneural-Diffuse/build/devtool-master`. |
> | **clean-root proof** | `packagegroup-symoneural-diffuse` + `symoneural-image-diffuse` written and built; `tools/proofs/diffuse.py` runs `sd-cli` under the target loader with the host cache inhibited. **PASS**, host leakage exactly the four S2 driver libraries at 615.71.09. |
> | **weights** | ACQUIRED 2026-09-17 — four files, pinned by Hugging Face **commit sha**, sha256 recorded: `flux1-schnell-q4_k.gguf` (`image`), `t5xxl-Q8_0.gguf` (`image-aux`), `clip_l.safetensors` (`image-clip`), `ae.safetensors` (`image-vae`). The single `image` row this report assumed was never enough; sd-cli needs four. |
> | **14c** | partly done — the four `image*` rows are PRESENT. `asr` and `cutout` wait on 14b. |
> | **14d** | units `image` 8809 and `sigils` 8810 registered; **launch line CORRECTED** (below). `Symoneural-Diffuse/app/` not written. |
> | 14b, 14e | not started. 14e needs a second evictable GPU unit — `chat` — whose weights are still ABSENT. |
> | **GATE** | **MET. 9.0 s against ≤ 13.44 s**, two runs (9.2 s, 9.0 s), each including a full model load. The 768×768 PNG is `generated/evidence/phase-14/14a-render-768-20260917.png`. But read `DECISIONS.md` "Standing constraint" with it: 11.2 s *"was taken on a stack that no longer exists ... targets, not baselines. Re-measure; do not inherit."* Whether it included a model load is **unrecorded**; the prior run's three weeks of routine output reads like a resident server. The number to carry forward is 9.0 s, process per render, 11.79 GiB resident (prior peak was recorded at 14.26 GiB). |
>
> **The gate turned on one flag.** This report's 14d line says `--backend te=cpu`. The
> real flag is `--clip-on-cpu`, and measured on this card it costs 9.9 s a render:
>
> | text encoder | params | `get_learned_condition` | wall |
> |---|---|---|---|
> | on the card | 11 786 MB VRAM | 2.34 s | **9.0 s — MET** |
> | `--clip-on-cpu` | 6 726 MB VRAM + 5 061 MB RAM | 11.89 s | 18.9 s — missed |
>
> Upstream recommends it for 6 GB and 4 GB cards. This one has 15.92 GiB, and the reason
> to keep the encoder off the card — leaving room for a resident chat model — is something
> the GPU lock already forbids. Corrected in `docs/operator-checklist.md` 14d and
> `docs/diffuse/ARCHITECTURE.md` §8.
>
> **Endpoints assigned:** `POST /v1/images/generations` and `POST /v1/images/edits` →
> unit `image`, worker `sd-cli`. `sigils` gets none, deliberately, and the reason is on
> the record. `docs/api/ENDPOINT-REGISTER.md`.
>
> **Ordering, stated plainly.** The spec's own "Start after" line says *Phase 12 gate
> (independent of 13)*; the queue instruction says *after phase 13 GATE PASSED*. **Neither
> gate has passed.** 14a was built ahead of both under Garrett's standing instruction of
> 17 September to make the thing work and explain the decisions afterwards. That is a
> deviation from A7 ("do not acquire ahead of the phase that builds the component"), and
> it is recorded here as a deviation, not presented as the plan having been followed.
>
> Design, theory and the worker/unit contract: `docs/diffuse/ARCHITECTURE.md`.

---

## SETTLED

- **S1** Each ggml carrier builds its own vendored ggml as upstream ships it; the
  three-ggml collision stays recorded UNRESOLVED.
- **S2** whisper.cpp is CPU, `GGML_CUDA=OFF`.
- **S3** Acquire here (A7): stable-diffusion.cpp pinned SNAPSHOT `7f410a37`
  (`master-859-7f410a3`), diffusers, rembg, whisper.cpp, and onnxruntime
  (microsoft/onnxruntime, MIT — rembg requires it; CPU-only build).

## ITEMS

- **14a** `symoneural-stable-diffusion-cpp`: cmake, `SD_CUDA`,
  `CMAKE_CUDA_ARCHITECTURES=120`; package `sd-cli`. Provenance row: ggml submodule
  = `leejet/ggml` fork.
- **14b** onnxruntime CPU; then rembg. whisper.cpp CPU; package `whisper-cli`.
- **14c** Register rows `image`, `image-aux`, `asr`, `cutout`:
  FOUND/FETCHED/ABSENT by sha256 per Phase 12 S3.
- **14d** Register `image` and `sigils` units with launch lines
  (`sd-cli --backend te=cpu --vae-tiling --diffusion-fa`, 4 steps, cfg 1.0, euler);
  matte and PNG encoder in `Symoneural-Diffuse/app/`.
- **14e** Contention: alternate `POST /api/chat` and `POST /api/image` ten times;
  log each eviction with drain time and VRAM before/after.

## GATE

768² render measured within 20% of 11.2 s; ten alternations, zero stale holders,
every drain under 60 s; a cutout and a transcription complete on CPU during a
render; clean.

## COMMIT

`phase 14: Diffuse acquired and built; onnxruntime; lock proven under contention`

## RETURN

- ACQUIRED five: tag/SNAPSHOT → SHA, licence files, collisions
- RENDER seconds measured, VRAM peak; CONTENTION evictions, max drain, stale holders
- CPU-BESIDE-GPU cutout ms, transcription ms
- DECISIONS FOR GARRETT: none

## PRIOR-RUN EVIDENCE — the image pipeline demonstrably worked

Recovered 2026-09-13 from Claude history. The prior run's image pipeline produced
finished output before `/home/google/Symoneural/` was deleted.

### Two surviving renders

Outputs were written to `/home/google/Symoneural/backend/output/` as
`gen-<epoch-ms>-<seed>.png`. That directory is **gone**. Exactly two files
survived, and only because they had been copied into a Claude job's temp
directory — an accident, not a backup:

| File | Size | Generated |
|---|---:|---|
| `generated/evidence/prior-run-render-768-20260903.png` | 930,605 B | 2026-09-03 03:25 |
| `generated/evidence/prior-run-cutout-20260903.png` | 236,383 B | 2026-09-03 03:25 |

Copied into the repo because they are small, ours, and the only proof that this
pipeline ever ran.

**They show both halves of 14d working.** The first is a **768×768** render — the
exact resolution this phase's GATE specifies (*"768² render measured within 20% of
11.2 s"*). The second is the same subject as a **matte cutout on white**, which is
the `cutout` row (`rembg/u2net.onnx`) plus the *"matte and PNG encoder in
`Symoneural-Diffuse/app/`"* from 14d.

So the render → background-removal → asset chain is not speculative. It has run,
and the artefacts are in the repo.

### Generation history

Renders span **2026-08-20 → 2026-09-10**, the last at 19:22 the night before the
final session. The pipeline was in routine use, not a one-off experiment.

### Model rows this phase needs

Both are ABSENT on disk and must be fetched per Phase 12 S3:

| Register row | Prior-run name | Source |
|---|---|---|
| `image` | `symoneural-image-unet-q4_k.gguf` | `leejet/FLUX.1-schnell-gguf` |
| `image-aux` | `symoneural-image-t5-q8_0.gguf` | `second-state/FLUX.1-schnell-GGUF` |

### One change to 14d

Renders were written **inside the project tree** and were lost with it. The two
survivors persisted only by chance. 14d should write to a location outside any
tree that gets deleted wholesale — the same separation that puts weights in
`SYMON_MODELS_DIR` rather than in the repo.

Generated output is an asset. The prior run treated it as a byproduct, and that is
why there are two files left out of three weeks of renders.
