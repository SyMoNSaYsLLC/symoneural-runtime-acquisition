# PHASE 13 — Common: torch with CUDA, and the Studio proof

## STATUS: NOT STARTED — blocked on the Phase 12 gate

**starts after: Phase 12 gate** (the phase's own line; authoritative per O1)

> **ORDERING (O1).** Each phase's own "Start after" line is authoritative; the
> QUEUED serial chain is withdrawn. Dependency graph:
>
> ```
> 10 → 11 → { 11-T, 18 }
> 11 → 12 → { 13, 14, 17 }
> 13 → 16          14 → 15          { 15, 16, 18 } → 19
> ```
>
> 13, 14 and 17 all unblock together at the Phase 12 gate and may build
> concurrently in separate build dirs (R3', R6'). **GPU PROOF steps serialise
> through the governor**: 13e/13f must finish before 14e's contention test starts —
> a training hold is never evicted, so a contention test begun during 13e would
> measure the wrong thing.

Authoritative body received 2026-09-13. **"Its own night"** — this phase is
expected to take a full session on its own.

Milestone: torch 2.14 CUDA imports on the 5070 Ti from an estate build; the 7B
QLoRA adapter is reproduced with estate-built peft and bitsandbytes and served
through Chat.

---

## SETTLED

- **S1** Common's torch **is** the estate torch.
- **S2** `vllm` and `triton` are **not built**; their trees are marked
  **REFERENCE-ONLY** in the manifest.
- **S3** Corpus: **path and sha256 only**.
- **S4** Acquire here (A7): `peft`, `trl`, `bitsandbytes`, `datasets`.

## ITEMS

- **13a** `symoneural-pytorch` under the pristine class (**record export time**):
  `USE_CUDA=1 TORCH_CUDA_ARCH_LIST="12.0" USE_CUDNN=1 USE_DISTRIBUTED=0
  BUILD_TEST=0`.
- **13b** `transformers`, `accelerate`, `huggingface-hub`; `safetensors` and
  `tokenizers` via `python_maturin` with **tracked crate closures**.
- **13c** Studio four per S4; bitsandbytes `COMPUTE_BACKEND=cuda
  COMPUTE_CAPABILITY=120`.
- **13d** Proof 1: `torch.cuda.is_available()` **True**;
  `get_device_capability()` **(12, 0)**.
- **13e** Proof 2: `Symoneural-Studio/app/train_lora.py` (NF4, r=16, alpha 32,
  `paged_adamw_8bit`, bf16, assistant-masked loss), smoke, **20 steps** on
  `train-7b` under `with train`; **peak VRAM measured**.
- **13f** Proof 3: adapter → GGUF f16 → `--lora`; **same prompt answers
  differently**.

## GATE

13d–13f from estate binaries; **one torch in `prod/`**; clean.

## COMMIT

`phase 13: torch 2.14 CUDA sm_120, HF stack, Studio four, QLoRA round-tripped`

## RETURN

- TORCH version, capability, wall time, **export time**
- STACK per package; QLORA steps, VRAM, sha256s, round-trip differs YES/NO
- ACQUIRED four: tag → SHA, licences, collisions
- DECISIONS FOR GARRETT: none

---

## READINESS — what earlier phases established

**13a's export time is a Phase 10 RETURN item still owed.** pytorch is the largest
tree in the estate — **37 submodules**, repo ~1.5 GB, submodules ~1.8 GB, so
~3.5 GB recursive. `symoneural-pristine` exports via `git archive HEAD` plus each
initialised submodule separately, so pytorch is the worst case for export cost and
the number worth recording. `symoneural-pytorch` is at PV **2.14.0** (derived from
the `v2.14.0` tag at its pinned SHA during the PV sweep, replacing `1.0+git`).

**13b's stack is already pinned and PV-corrected:** `symoneural-transformers`,
`symoneural-accelerate`, `symoneural-huggingface-hub` (PV **1.31.0**),
`symoneural-safetensors` (**0.8.0**), `symoneural-tokenizers` (**0.23.2**).

**13b's "tracked crate closures" has a working precedent.** `symoneural-stratum`
ships `symoneural-stratum-crates.inc` with 233 `crate://` entries, proven
AUTHORITATIVE in Phase 10: regenerating with `bitbake -c update_crates` from the
pristine export produced a **byte-identical** file. safetensors and tokenizers
should follow the same pattern.

**A live class defect affects 13b directly.** `do_fetch[noexec] = "1"` in the first
version of `symoneural-pristine` starved every `crate://` entry — the vendor
directory held **0 crates**. Fixed by stripping only the upstream `git://` URI at
parse and letting `do_fetch` run (vendored 0 → 183). `python_maturin` recipes with
crate closures would have hit exactly this. N3(c) now fails at unpack time if a
`crate://` recipe's vendor directory is empty.

**S2 matches what is already recorded.** `symoneural-vllm` (PV 0.29.0) and
`symoneural-triton` (3.8.0) exist as recipes but have never been built. Marking
their trees REFERENCE-ONLY in the manifest follows the pattern already used for
`mcp-typescript-sdk` and `workers-sdk` — tree stays acquired and pinned, only the
source build is declined.

**13e's model is a Phase 12 GATE-REQUIRED row.** `train-7b` =
`hf/ Qwen/Qwen2.5-7B-Instruct`, measured ~12 GB QLoRA, Apache-2.0. As of Phase 10
`/home/google/symoneural-models` is **empty (24 KB)**, so the weights arrive via
Phase 12's 12e sweep (`find / -xdev`, MOVE if found, fetch from the model card if a
gate needs it). **13 cannot start before 12 for this reason as well as CUDA.**

**Blackwell facts for 13a/13d:** RTX 5070 Ti, **sm_120**, driver 615.71.09. 13d's
expected `get_device_capability() == (12, 0)` is the numeric form of sm_120.
Phase 12's S1 builds CUDA **13.3** as an estate binary recipe while the host runs
**13.4** — a useful accident, since the version string alone distinguishes estate
nvcc from host nvcc in `run.do_compile`.
