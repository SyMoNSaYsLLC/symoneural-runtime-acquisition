# PHASE 12 — CUDA inside the estate: Chat live under the lock; the models register

## STATUS: NOT STARTED — blocked on the Phase 11 gate

**starts after: Phase 11 gate** (the phase's own line; authoritative per O1)

Authoritative body re-pasted 2026-09-13 after compaction, including the models
register; supersedes any summary. Nothing started, acquired, fetched or moved.

Milestone: `llama-server` built by OE-Core with CUDA for **sm_120** streams tokens
on the 5070 Ti through the governor.

---

## SETTLED

- **S1** CUDA Toolkit as a **BINARY recipe in the estate**, EULA recorded, **never
  the host's nvcc**. `LICENSE_FLAGS_ACCEPTED` is **Garrett's acceptance, written by
  you**.
- **S2** `libcuda.so` from the **host driver** at runtime; the toolkit stub links.
- **S3** Weights live at `SYMON_MODELS_DIR=/home/google/symoneural-models`. Search
  the whole disk (`find / -xdev`) for each register filename; **MOVE** found files
  there keeping `llm/ image/ whisper/ rembg/ hf/`; if a file a GATE needs is
  absent, fetch it from its model-card repo
  (`https://huggingface.co/<repo>/resolve/main/<file>`, public) and **record the
  sha256**. Non-gate files stay **ABSENT** if not found. **No question returns.**
- **S4** Chat serves the **7B by default**; 27B stays **opt-in until evaluated**.

## MODELS REGISTER — `acquisition/model-register.json` (CURATED)

| row | file | repo | format | consumer | measured | licence | gate |
|---|---|---|---|---|---|---|---|
| `chat` | `llm/Qwen2.5-7B-Instruct-Q4_K_M.gguf` | `bartowski/Qwen2.5-7B-Instruct-GGUF` | GGUF Q4_K_M | llama-server | 8.2 GiB @64K; **151 tok/s bare** | Apache-2.0 | **GATE-REQUIRED** |
| `chat-14b` | `llm/Qwen2.5-14B-Instruct-Q4_K_M.gguf` | `bartowski/Qwen2.5-14B-Instruct-GGUF` | GGUF Q4_K_M | llama-server | 98 tok/s | Apache-2.0 | |
| `draft` | `llm/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf` | `bartowski/Qwen2.5-0.5B-Instruct-GGUF` | GGUF | `-md` | +5% | Apache-2.0 | |
| `adapter` | `adapters/symoneural-lora.gguf` | **trained here** (PEFT r=16 → f16 GGUF) | GGUF LoRA | `--lora` | — | **owner; corpus trade secret** | |
| `chat-27b` | `llm/Qwen3.6-27B-UD-Q2_K_XL.gguf` + `mmproj-F16.gguf` | `unsloth/Qwen3.6-27B-GGUF` | GGUF 11.03 GiB | llama.cpp ≥`4df29be` | 12.4–14.3 GiB | **VERIFY on card** | |
| `image` | `image/flux1-schnell-q4_k.gguf` | `leejet/FLUX.1-schnell-gguf` | GGUF q4_k | sd-cli | ~7 GB; 768² **11.2 s** | Apache-2.0 (**never dev**) | **GATE-REQUIRED (14)** |
| `image-aux` | `image/ae.safetensors`, `clip_l.safetensors`, `t5xxl-Q8_0.gguf` | `second-state/FLUX.1-schnell-GGUF` | — | sd-cli, T5 on CPU | 12 GB disk | Apache-2.0 | **GATE-REQUIRED (14)** |
| `asr` | `whisper/ggml-base.en.bin` | `ggerganov/whisper.cpp` | ggml | whisper-cli | 0 VRAM, 284 MiB RSS | MIT | **GATE-REQUIRED (14)** |
| `cutout` | `rembg/u2net.onnx` | `github.com/danielgatis/rembg` releases | ONNX | rembg | — | Apache-2.0 | **GATE-REQUIRED (14)** |
| `train-7b` | `hf/ Qwen/Qwen2.5-7B-Instruct` | `huggingface.co/Qwen/Qwen2.5-7B-Instruct` | bf16→NF4 | PEFT | ~12 GB QLoRA | Apache-2.0 | **GATE-REQUIRED (13)** |
| `train-27b` | `hf/ Qwen/Qwen3.6-27B` | `huggingface.co/Qwen/Qwen3.6-27B` | bf16→NF4 | PEFT | **14.26 GiB peak** | **VERIFY on card** | |

## ITEMS

- **12a** `cuda-toolkit-bin_13.3.bb` (+ `-native`): NVIDIA public local installer;
  `LICENSE "Proprietary"`; `LIC_FILES_CHKSUM` on the EULA; `LICENSE_FLAGS
  "commercial"` accepted in `symoneural.conf` with the EULA named; install
  `/usr/local/cuda-13.3`; `INSANE_SKIP` already-stripped/ldflags; licence inventory
  row **BINARY/REFERENCE** with **EULA sha256**.
- **12b** `cudnn-bin_9.x.bb` from the public cudnn redist for cuda13.
- **12c** `symoneural-llama-cpp` (cmake): DEPENDS the toolkit `-native` and target;
  `-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120 -DGGML_NATIVE=OFF`.
- **12d** `symoneural-governor`: script packaged with tests; `GpuQueue` wired; chat
  unit registered (`-ngl 99 -c 65536 -np 2`, draft if present, `--lora` if present).
- **12e** Weights per S3; write the register with **FOUND/FETCHED/ABSENT** and sha256.
- **12f** Prove: `POST /api/chat` streams on `:8801`; `nvidia-smi` shows
  llama-server's VRAM; holder names `chat`; release clears; queued→ready on a
  second request.

## GATE

**Five sequential completions** with lock acquired/released and drain logged;
`run.do_compile` shows **the estate's nvcc**; register written; clean.

**FALLBACK GATE:** toolkit cannot become a recipe → **stop with the failing step
and log**.

## COMMIT

`phase 12: CUDA toolkit as estate recipe; llama-server sm_120; Chat live; models register`

## RETURN

- CUDA built YES/NO; EULA sha256; failing step if NO
- LLAMA **nvcc path verbatim**; VRAM measured; tok/s bare and with `--lora`
- LOCK acquisitions / releases / stale / max drain
- MODELS rows: FOUND / FETCHED / ABSENT with sha256
- DECISIONS FOR GARRETT: none

---

## READINESS — what Phase 10 established

**S3's destination exists and is EMPTY.** `/home/google/symoneural-models` has
`hf/ image/ llm/ rembg/ whisper/` — **all empty, 24 KB total**. So every register
row is currently **ABSENT on disk**, and 12e's `find / -xdev` sweep is the first
real step. Nothing has been searched, moved or fetched. `SYMON_MODELS_DIR` is
`status: set` in `api.env`. Weights never enter git.

**12c's recipe exists but is NOT yet CUDA.** `symoneural-llama-cpp` is at PV
**b10809** (corrected from `0.4.0` under E4 — `b10809` and `v0.4.0` both point at
SRCREV, and PV follows the package the recipe builds). It currently carries
`-DBUILD_SHARED_LIBS=ON -DGGML_NATIVE=OFF -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF`
and `inherit cmake`. 12c adds `-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120` and
the toolkit DEPENDS.

**The register's `chat-27b` requirement is ALREADY VERIFIED — llama.cpp ≥ `4df29be`
is satisfied.** Checked read-only against the acquired tree:

```
pinned SRCREV  5266f24da75dc449bd56cbed7addb9c8e4a6a73e   2026-09-04 15:22:38 +0300
required       4df29be                                    2026-08-16 14:53:13 +0200
git merge-base --is-ancestor 4df29be <pin>  ->  TRUE
```

`4df29be` is an ancestor of the pin with ~3 weeks of margin, so the 27B is
supported by the pinned llama.cpp. Same containment check that caught seven tag
traps during acquisition. **Phase 12 does not need to re-derive this.**

**S1's "never the host's nvcc" has a ready-made check.** The GATE requires
`run.do_compile` to show the estate's nvcc; the host has CUDA 13.4 while 12a pins
**13.3**, so the two are distinguishable by version string alone — a useful
accident worth exploiting in the proof.

**Host facts for 12c/12f:** RTX 5070 Ti (Blackwell, **sm_120**), driver
**615.71.09**, CUDA **13.4** on the host. S2's `libcuda.so`-from-driver posture is
what makes an estate-built 13.3 toolkit viable against that driver.

**12a's `LICENSE_FLAGS "commercial"` is the first non-permissive thing in the
estate.** Everything acquired so far is MIT/BSD/Apache-2.0 by deliberate policy,
with copyleft quarantined and never linked. The CUDA EULA is proprietary and
enters as **BINARY/REFERENCE** with its sha256 recorded — consistent with the
standing position that the CUDA Toolkit can never be fully source-built, which is
a property of the platform rather than a gap to close.
