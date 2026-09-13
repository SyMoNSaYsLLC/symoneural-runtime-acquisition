# PHASE 14 — Diffuse: Image and Sigils live, the lock under contention

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


Queued 2026-09-13 by Garrett with "QUEUED — do not start." Spec text is recorded
below verbatim so the phase is self-contained when it is picked up. Nothing in
this phase has been acquired, built, configured or run. No tree has been cloned
for it: A7 forbids acquiring ahead of the phase that builds the component.

Note on ordering: the spec's own "Start after" line says **Phase 12 gate
(independent of 13)**, while the queue instruction says **after phase 13 GATE
PASSED**. The queue instruction is the later and more restrictive of the two, so
it governs. Recorded rather than reconciled silently.

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
