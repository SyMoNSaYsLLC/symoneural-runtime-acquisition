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

## PRIOR-RUN EVIDENCE — recovered from Claude history 2026-09-13

Reconstructed from `~/.claude/projects/-home-google-Symoneural/1889a362-...jsonl`
(62 MB, 8,856 entries, all of 2026-09-11) plus 19 other sessions spanning
2026-08-24 → 2026-09-13. **This model set was built once and then lost when
`/home/google/Symoneural/` was deleted.** None of it is on disk today.

### The model set as it existed, with sizes

Sizes are the reliable identifier — the files were rebranded, so upstream names
do not match.

| Sept-11 name | Bytes | Size | Built | Source repo | Register row |
|---|---:|---:|---|---|---|
| `symon-1.0-32b-q2_k_xl.gguf` | 12,797,352,608 | 11.9 GB | Sep 8 | `unsloth/Qwen3-32B-GGUF` | **absent** |
| `symon-1.0-27b-q2_k_xl.gguf` | 11,849,779,424 | 11.0 GB | Sep 8 | `unsloth/Qwen3.6-27B-GGUF` | `chat-27b` |
| `symon-1.0-30b-a3b-q2_k_l.gguf` | 11,331,539,360 | 10.6 GB | **Sep 11** | `unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF` | **absent** |
| `symon-1.0-14b-q4_k_m.gguf` | 8,988,110,976 | 8.4 GB | Sep 8 | `bartowski/Qwen2.5-14B-Instruct-GGUF` | `chat-14b` |
| `symon-1.0-7b-q4_k_m.gguf` | 4,683,074,240 | 4.4 GB | Sep 2 | `bartowski/Qwen2.5-7B-Instruct-GGUF` | `chat` |
| `symon-1.0-27b-vision-f16.gguf` | 927,607,360 | 885 MB | Sep 8 | `unsloth/Qwen3.6-27B-GGUF` (`mmproj-F16`) | `chat-27b` pair |
| `symon-1.0-draft-0.5b-q4_k_m.gguf` | 397,808,192 | 379 MB | Sep 2 | `bartowski/Qwen2.5-0.5B-Instruct-GGUF` | `draft` |
| `symoneural-lora.gguf` | 80,767,680 | 77 MB | **Aug 16** | trained here | `adapter` |
| `symoneural-image-unet-q4_k.gguf` | — | — | — | `leejet/FLUX.1-schnell-gguf` | `image` |
| `symoneural-image-t5-q8_0.gguf` | — | — | — | `second-state/FLUX.1-schnell-GGUF` | `image-aux` |

**≈ 51 GB**, formerly at `/home/google/Symoneural/backend/models/{llm,image}/`.

**Seven of ten rows already match this register.** The register names them upstream;
the prior run renamed them. Same files.

**Three are NOT in the register** — `Qwen3-32B`, `Qwen3-30B-A3B`, `gpt-oss-20b`.
They exist only in a transcript. **DECISION FOR GARRETT: add or drop.** Recorded
rather than added, because a models register that lists what nothing consumes is
the same defect as a licence file that names a path the export never contains.

`symoneural-lora.gguf` is dated **2026-08-16** and therefore excluded by Garrett's
standing instruction to use nothing from August. Phase 16 retrains it; an adapter
trained against the current stack is preferable to restoring one from a
superseded run.

### The rebrand step — 12e must record this

Renaming a GGUF is not enough: `general.name` is embedded in the file. The prior
run used llama.cpp's `gguf-py/gguf/scripts/gguf_new_metadata.py`, and the method
was sound — recorded verbatim from the session:

> *"`gguf_new_metadata.py` wrote a **copy** so the validated original was never
> edited, then atomic-renamed."*

Non-destructive by construction: validate the download, write a renamed copy,
atomic-rename into place. The original is never mutated, so a failed rebrand
cannot destroy a 12 GB download.

**Hazard found in that run:** `general.architecture` must not be touched.
`qwen2` and `gpt-oss` are distinct architectures and **`llama-server` exits 1 on a
mismatch**. Rewrite `general.name` only.

### VRAM was the real constraint, not model quality

Across all 20 sessions:

| Pattern | Hits |
|---|---:|
| VRAM | 5,365 |
| out-of-memory / CUDA error | 5,319 |
| corrupt / truncated / incomplete | 2,085 |
| gguf not found | 1,677 |
| llama-server exit | 292 |
| unknown model architecture | 14 |

Raw grep counts overstate — one long planning discussion inflates a total — but
the **ratio** is informative: ~380 VRAM/OOM hits for every architecture error. The
prior run was not fighting broken models. It was repeatedly rediscovering that a
16 GB card cannot hold a 51 GB set, by crashing into it.

This is why Phase 16a specifies a **VRAM planner validated against measured
figures** (7B ~12 GB, 27B 14.26 GiB) rather than trial and error, and why S4 keeps
the 27B opt-in until evaluated.

### What actually protects this now

The structural failure was not losing models — they are re-downloadable. It was
that `/home/google/Symoneural/` held models, training adapters, generated outputs
and the backend **in one tree**, so a single deletion took the reproducible and
the irreplaceable together.

| Prior run | Current design |
|---|---|
| models inside the project tree | `SYMON_MODELS_DIR=/home/google/symoneural-models`, outside the repo |
| no inventory | `model-register.json`, FOUND/FETCHED/ABSENT **by sha256** |
| outputs beside source | `run/reinforce/adapters/<job>` + run manifest |
| VRAM found by crashing | 16a VRAM planner against measured figures |
| one tree, one `rm` | weights never in git; repo is 12 MB of recipes |

12e's `find / -xdev` sweep will find **nothing** — confirmed by search of `/home`,
`/yocto` and `/`. Every row is a FETCH, not a MOVE.

## PRIOR-ESTATE EVIDENCE — /yocto, a second OE estate that DID build

`/yocto` is a complete, separate OpenEmbedded estate (492 GB partition, 112 GB
used) with its own `bitbake`, `openembedded-core`, `meta-openembedded`, a 41 GB
sstate-cache, and **three custom layers**: `meta-symoneural`,
`meta-symoneural-bsp`, `meta-cryptocurrency`. Last built 2026-08-25.

It is not a failed experiment. `build-ai6.log` ends:

```
NOTE: Tasks Summary: Attempted 9334 tasks of which 9313 didn't need to be rerun
      and all succeeded.
```

**It reached a working state, then was abandoned** — the work moved to
`/home/google/Symoneural`, then to `SymonSaysLLC`. Read-only; nothing imported.

### Five failures before it worked — and four are defect classes we have hit

| Build | Failure | Our equivalent |
|---|---|---|
| `build-ai` | `do_unpack` failed on `python3-safetensors`, `python3-huggingface-hub` | the `python_maturin` / Rust-closure recipes, Phase 13b |
| `build-ai2` | `do_create_spdx: Cannot find any text for license LicenseRef-NVIDIA-Proprietary` | **identical** to `LicenseRef-netlib-BLAS` needing a text file under `meta-symoneural/files/custom-licenses/` (O4) |
| `build-ai3` | `do_package_qa: non -staticdev package contains static .a library` | **identical** to numpy's `FILES:${PN}-staticdev` and stratum's rlibs → `-staticdev` (R12') |
| `build-ai4` | `do_package_qa: Architecture did not match (Unknown (243), expected x86-64) in /usr/lib/firmware` | what 12a's `INSANE_SKIP` exists for |
| `build-ai5` | `do_rootfs: Unable to install packages` | no equivalent yet — we build no image |

**`build-ai2` is the one to act on.** 12a specifies `LICENSE "Proprietary"` with
`LIC_FILES_CHKSUM` on the EULA. The prior estate proves that is not sufficient on
its own: a `LicenseRef-*` token with **no corresponding text file** fails
`do_create_spdx` outright. The NVIDIA EULA text must be placed under
`meta-symoneural/files/custom-licenses/` exactly as O4 requires for netlib-BLAS —
same mechanism, same failure if skipped.

### A different CUDA strategy, already proven to build

12a specifies the CUDA Toolkit as **one binary recipe** from NVIDIA's local
installer. The prior estate did something else: **CUDA as PyPI wheels at 13.0.48**,
one recipe per component —

```
python3-nvidia-cuda-runtime   cuda-nvrtc   cuda-cupti   cublas   cudnn-cu13
cufft   cufile   curand   cusolver   cusparse   cusparselt-cu13
nccl-cu13   nvjitlink   nvshmem-cu13   nvtx
```

That is how PyTorch itself ships CUDA. Trade-off, stated plainly:

* **Wheels**: no EULA acceptance for the toolkit, each component versioned and
  licensed separately, proven to build here — but it is a *runtime* set. It gives
  no `nvcc`, so 12c's `-DGGML_CUDA=ON` compile has nothing to compile with, and
  12's GATE (`run.do_compile shows the estate's nvcc`) cannot be satisfied.
* **Local installer (12a as written)**: provides `nvcc`, satisfies the GATE,
  requires `LICENSE_FLAGS "commercial"` and the EULA text file.

**They are not alternatives — llama.cpp needs `nvcc`, PyTorch needs the runtime
wheels.** Phase 12 needs 12a; Phase 13 may want the wheel set. Recorded so 13
does not rebuild from scratch what already exists at `/yocto/meta-symoneural`.

### A packagegroup and an image already exist there

```
packagegroup-symoneural-ai
  ├── ${PN}-cuda        11 nvidia wheel packages
  ├── ${PN}-torch       python3-torch
  └── ${PN}-diffusion

core-image-symoneural   inherit symoneural-core-image
COMPATIBLE_MACHINE = "symoneural-x86-64"
```

The prior estate had a **custom MACHINE and a bootable image**. The current estate
has neither — it builds individual recipes into `tmp/deploy/ipk`. That is the
single largest structural difference between the two, and it is what Phase 11d
(`packagegroup-symoneural-rack`) begins to close.

`/yocto/meta-symoneural` also carries recipes for `python3-torch`,
`transformers`, `peft`, `accelerate`, `diffusers`, `safetensors`, `tokenizers` —
the whole Phase 13 stack, already written once. **Reference, not import**: they
predate `symoneural-pristine`, so they will carry externalsrc-era assumptions.
Worth reading before writing 13b; worth not copying.
