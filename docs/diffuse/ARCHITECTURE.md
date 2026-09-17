# Diffuse — the image runtime

**Phase 14.** Two surfaces, `image` and `sigils`, one engine, one card shared with
everything else that wants it. Written 17 September 2026 alongside item 14a.

Status discipline first, because this document would otherwise read as a description of
something that exists: **14a is built and packaged; 14b, 14c, 14d and 14e are not.**
Section 10 says exactly which line of the checklist each claim below corresponds to.
What is in the repository is the recipe, this design, and whatever the evidence files in
`generated/evidence/phase-14/` show. Nothing else.

---

## 1. What Diffuse is

`image` renders a picture from a prompt.

**`sigils` is a name without a recorded definition**, and this document will not invent
one. It appears in `DECISIONS.md` §1's unit list, in the Phase 14 title, and in the
priority table at 90 — and nowhere else in the repository. What *is* recorded is its
rank: below `image` and `chat`, above `studio`. Everything in §8 below that names `sigils`
describes a second surface on the same engine at a lower claim on the card; what it
renders is Garrett's to say, and 14d is where it gets said.

They are two units, not one, because they have different claims on the card. The priority
table in `libsymoneural-api` (and its Python fallback in `gpulock.py`) already reflects
that — it was written with the API's C ABI (`docs/api/C-ABI.md`), before this engine
existed:

```
chat 100   image 100   sigils 90   studio 50   reinforce 50   miner 10
```

`image` ties with `chat`: a person waiting on a picture is as interactive as a person
waiting on a sentence. `sigils` sits one rank below both, because a badge can wait behind
a user and nothing breaks.

## 2. Why a C++ engine and not PyTorch

The estate already builds `symoneural-pytorch`, `symoneural-transformers` and
`symoneural-accelerate` for the `studio` unit, so "we have no PyTorch" is not the reason.
Three things are:

**One card, 15.92 GiB.** `nvidia-smi` on this host, 17 September: *NVIDIA GeForce
RTX 5070 Ti, 16303 MiB, compute_cap 12.0* — which is where both the 15.92 GiB in
`gpulock.py` and `SYMON_CUDA_ARCH = 120` come from.
The lock hands the GPU to exactly one unit at a time, which means
a renderer's cost is not only its peak VRAM but how fast it can *give the card back*. A
PyTorch process holds a CUDA context, a caching allocator and a loaded pipeline; tearing
that down and rebuilding it per handover is the expensive part. A `sd-cli` invocation is a
process: it starts, takes the lock, renders, exits, and the card is unambiguously free
when the PID is gone. `gpulock.py` already reaps by PID — the engine's process model and
the lock's staleness model are the same model.

**Quantised weights.** GGUF q4/q5 diffusion weights fit beside a chat model's working set
in a way an fp16 `diffusers` pipeline does not. The estate's image row is
`flux1-schnell-q4_k.gguf` for exactly this reason.

**Build posture.** sd.cpp is C++ with vendored dependencies and a CMake build. It fits the
estate's model — pinned source, pristine export, one CUDA authority — without a Python
dependency closure behind it. `diffusers` and `rembg` still arrive in 14b for the auxiliary
path (matting, cutouts); they are not on the render path.

## 3. The engine and its pin

| | |
|---|---|
| Component | `leejet/stable-diffusion.cpp` |
| Pin | `7f410a3793c5bba8eb198e962ce7a3d6095f9d89` |
| Tag at pin | `master-859-7f410a3` — a SNAPSHOT, not a release |
| Recipe | `meta-symoneural/recipes-diffuse/symoneural-stable-diffusion-cpp/symoneural-stable-diffusion-cpp_git.bb` |
| Tree | `Symoneural-Diffuse/src/image/source/stable-diffusion.cpp` |

Upstream has **no release line**. Its tags are `master-<N>-<sha>`, one per commit, so this
pin is a commit snapshot by construction and `tag_kind` in the register says `SNAPSHOT`.
`PV` is `0.0.859`: N is monotonic, so the version orders correctly against a later snapshot
and can be re-derived from the tag, which a date or a bare SHA could not.

Four submodules are committed as trees at the pin — `ggml` (`e20c3a14`, leejet's fork,
branch `sd.cpp`), `examples/server/frontend` (`c4bce3d6`), `thirdparty/libwebm`
(`5bf12267`), `thirdparty/libwebp` (`0c9546f7`).

On the day of acquisition upstream master was 13 commits further on, at `cc515a01`
(`master-872`), with an identical `SD_CUDA`/`GGML_CUDA` block. The checklist's Phase 14 S3
names `7f410a37`, so `7f410a37` is what was acquired. Bumping the pin stays a decision
someone makes, not a side effect of acquiring.

## 4. The ggml question, settled by the source rather than by preference

Phase 14 S1 says each ggml carrier builds its own vendored ggml and the three-way collision
stays recorded UNRESOLVED. That is often read as "we did not get round to unifying them".
It is not. Two facts in this tree make unification **wrong**, not merely deferred:

1. **Different trees.** The estate's `symoneural-ggml` is canonical `ggml-org/ggml` 0.23.0,
   linked by llama.cpp because `tools/map-llama-upstreams.py` proved the embedded copy
   byte-identical at `e91ded11bdcd`. sd.cpp's submodule is `leejet/ggml` — a personal fork
   — on branch `sd.cpp`, declaring `GGML_VERSION 0.19.0`.
2. **Different ABI.** `CMakeLists.txt` does
   `if (NOT SD_USE_SYSTEM_GGML) add_definitions(-DGGML_MAX_NAME=160)`. Upstream's default is
   64. `GGML_MAX_NAME` sizes the `name` array *inside* `struct ggml_tensor`, so a system
   ggml compiled at 64 and an sd.cpp compiled at 160 disagree on
   `sizeof(struct ggml_tensor)`. That is not a link error. It is silent memory corruption.

So `SD_USE_SYSTEM_GGML` stays `OFF`. The estate carries two libggml codebases and neither
is ever loaded into the other's process: llama.cpp's is a shared `libggml.so.0` with
dlopen'ed backend modules; sd.cpp's is compiled **static, inside** `libstable-diffusion.so`
and never appears as a loadable `libggml`. Nothing can confuse them **at run time**,
because only one of them has a file name.

**At BUILD time they could**, and the first build proved it. `ggml/CMakeLists.txt` installs
its CMake package config and its public headers unconditionally — line 347
`install(TARGETS ggml LIBRARY PUBLIC_HEADER)` and line 416 `install(FILES ggml-config.cmake
ggml-config-version.cmake …)`, neither inside a `GGML_STANDALONE` guard. Listing `${D}`
after that build found 19 `ggml*.h` plus `gguf.h` in `${includedir}`,
`ggml-config{,-version}.cmake` in `${libdir}/cmake/ggml`, and four `libggml*.a` — every one
of them at a path `symoneural-ggml-dev` owns for canonical 0.23.0. A third consumer's
`find_package(ggml)` could then compile against `GGML_MAX_NAME=160` headers and link a
0.23.0 library built at 64: the same corruption, arriving through the include path instead
of the loader.

`do_install:append` removes them. Nothing in the estate consumes this fork's ggml — it is
static inside one `.so` and has no separate consumer by design — so the honest fix is not
to ship its development interface at all. `rm -f` rather than a `FILES` exclusion: an
excluded file still sits in `${D}` and OE reports it as installed-but-not-shipped.

whisper.cpp (14b, CPU, `GGML_CUDA=OFF`) is the third carrier and re-checks the same pairing
when it is acquired.

## 5. CUDA posture

CUDA reaches this recipe only through `symoneural-cuda.bbclass` — the P7 authority, CUDA
13.4.1, `SYMON_CUDA_ARCH = 120` for Blackwell. The recipe sets `SD_CUDA=ON` and nothing
else about CUDA: `CMakeLists.txt` turns `SD_CUDA` into `GGML_CUDA=ON`, and the class writes
`CMAKE_CUDA_COMPILER`, `CMAKE_CUDA_HOST_COMPILER`, `CMAKE_CUDA_ARCHITECTURES` and
`CUDAToolkit_ROOT` into the generated toolchain file. Setting the architecture twice would
let the two disagree, so the recipe does not.

ggml then rewrites `120` to `120a-real` (`src/ggml-cuda/CMakeLists.txt`) because Blackwell's
FP4 tensor-core instructions are not forwards compatible — `12X` is, `12Xa` is not.

**S2 boundary.** `libcuda.so.1` and `libnvidia-ml.so.1` come from the host driver; the
toolkit ships only the link-time stub. The class exempts those two names from OE's
`file-rdeps` check and replaces it with `symon_cuda_qa_s2`, which walks every ELF in every
package and fails the build if any *other* `NEEDED` library has no provider. Nothing else
is hidden — that is the point of replacing the check rather than widening it.

`GGML_CUDA_NO_VMM` is left at its default `OFF`, so `ggml-cuda` links `CUDA::cuda_driver`
and `libstable-diffusion.so` legitimately carries `NEEDED libcuda.so.1`. That is the S2
boundary appearing exactly where it should.

### Two build-time network paths, both closed

- `GGML_CUDA_CUB_3DOT2` is the one `FetchContent` in the tree: it clones `nvidia/cccl`
  v3.2.0 from GitHub at configure time. CUDA 13.4 already bundles CCCL. It is never declared
  with `option()`, so it is an undefined → false variable and would not have fired by
  default; it is pinned `OFF` so a future default flip cannot turn a configure into a clone.
- `SD_SERVER_BUILD_FRONTEND` runs `pnpm install` and `pnpm run build` in
  `examples/server/frontend`. `pnpm` is not in the native sysroot and
  `examples/server/frontend/dist` does not exist at this pin, so the build would take the
  "pnpm not found" branch anyway. `OFF` makes that a decision instead of an accident of
  `PATH`.

`GGML_CUDA_NCCL` defaults ON and calls `find_package(NCCL)`. NCCL is not part of
`cuda-toolkit-bin`, so the probe can only miss — or, worse, hit a copy on the build host
outside the sysroot. One GPU: `OFF`.

## 6. The version stamp, and a trap worth naming

`CMakeLists.txt` runs `git describe --tags` and `git rev-parse --short HEAD` in
`CMAKE_CURRENT_SOURCE_DIR` and compiles the answers into `src/version.cpp`.

Under `symoneural-pristine`, `${S}` is a `git archive` export with **no `.git`** — but
`${WORKDIR}` lives under `Symoneural-Diffuse/build/`, which is **inside the estate
repository**. So git would walk upward and stamp `sd-cli` with the *estate's* commit. That
is precisely the failure the pristine class's own header warns about for `SYMON_TREE`, and
it would make the binary non-reproducible as a bonus.

`GIT_EXE` is a `find_program` cache variable, so the recipe points it at a six-line stub
written at `do_configure` time which answers `describe` with `master-859-7f410a3` and
`rev-parse` with `7f410a3`. Those two values **are** the pin. The alternative — letting it
fail to `unknown` — was rejected: an operator reading `sd-cli --version` should see what
was built, and the truthful answer was available.

## 7. Packaging

| Package | Contents | Shipped in an image? |
|---|---|---|
| `symoneural-stable-diffusion-cpp` | `sd-cli`, `libstable-diffusion.so` | yes — this is the unit's engine |
| `symoneural-stable-diffusion-cpp-server` | `sd-server` | **no** |
| `symoneural-stable-diffusion-cpp-dev` | **one file: `stable-diffusion.h`** | no |

`-staticdev` ends up **empty** and no `-staticdev` ipk is produced: the four `libggml*.a`
that would have filled it are the vendored fork's, removed at install (§4).

**`-dev` ships a header and nothing else, deliberately.** sd.cpp generates two files for
consumers and both point at the ggml that §4 removed:

```
cmake/stable-diffusion-config.cmake.in:12   find_dependency(ggml REQUIRED HINTS "${SD_LIB_DIR}/cmake")
cmake/stable-diffusion.pc.in                Libs.private: -lggml -lggml-base
```

With `${libdir}/cmake/ggml` gone the CMake config cannot resolve — and if
`symoneural-ggml-dev` happens to be installed, it resolves to **canonical 0.23.0**, handing
the consumer 0.23.0 headers for a library compiled at `GGML_MAX_NAME=160`. The `.pc` does
the same thing through `-lggml`. **A config that silently finds the wrong ggml is worse
than no config**, so both are removed too.

What is left is honest and usable: `stable-diffusion.h` includes only `stdbool.h`,
`stddef.h`, `stdint.h` and `string.h`, so a consumer compiles against it and links
`-lstable-diffusion`. There is no `find_package(stable-diffusion)` on this runtime, by
decision rather than by omission.

`libstable-diffusion.so` has no `VERSION`/`SOVERSION` upstream, so OE's default rules would
file the unversioned `.so` into `-dev` and leave `sd-cli` in the main package with an
unsatisfiable `NEEDED`. `FILES_SOLIBSDEV = ""` plus an explicit `FILES` entry puts the
runtime library where its consumers are; `INSANE_SKIP dev-so` acknowledges that the
unversioned name is upstream's choice, not a packaging mistake.

**Why `sd-server` is built at all.** `examples/CMakeLists.txt` adds `cli` **and** `server`
unconditionally — upstream's `SD_BUILD_SERVER` option is commented out, so the server cannot
be switched off without editing the source, and R1 forbids that. It is therefore built and
packaged **separately**, and no image installs it. The estate's HTTP surface is the FastAPI
gateway with its five route classes; a second, unauthenticated listener inside a runtime
image is not something to ship by accident. Packaging it apart makes that an explicit
choice rather than a silent inclusion.

## 8. The unit contract (14d — designed, not implemented)

Neither unit is in `REGISTRY` yet. When 14d adds them:

```python
Unit(name="image",  resource=Resource.GPU, port=8809,
     backed_by=("symoneural-stable-diffusion-cpp",), token_env="SYM_IMAGE_TOKEN")
Unit(name="sigils", resource=Resource.GPU, port=8810,
     backed_by=("symoneural-stable-diffusion-cpp",), token_env="SYM_SIGILS_TOKEN")
```

8809 and 8810 are the next free ports after `miner` at 8808; `tools/proofs/api.py` already
asserts no two units share a port, so a collision fails a proof rather than a request.

**Launch line** (checklist 14d):

```
sd-cli --backend te=cpu --vae-tiling --diffusion-fa   # 4 steps, cfg 1.0, euler
```

Each flag is a VRAM or latency decision, not a default someone liked:

- `te=cpu` — run the **text encoder on the CPU**. It is small, it runs once per prompt, and
  keeping it off the card leaves that VRAM for the UNet. This is also what lets a render
  begin while the card is still draining from the previous holder.
- `--vae-tiling` — decode the latent in tiles. VAE decode is the peak-VRAM moment of a
  768² render; tiling trades a little time for a much lower peak, which is what decides
  whether `image` and a resident chat model can ever overlap.
- `--diffusion-fa` — FlashAttention in the diffusion model. `GGML_CUDA_FA` is ON by default
  in the vendored ggml, so the kernels are compiled; this turns them on at run time.
- 4 steps, cfg 1.0, euler — the schnell-family configuration. A distilled model at 4 steps
  with guidance disabled; more steps and a higher cfg would cost time and change nothing.

**Worker contract.** `Symoneural-Diffuse/app/` (14d) holds the matte and PNG encoder and
wraps the engine. The shape the rest of the estate depends on:

1. Take `gpulock.hold("image")` (or `"sigils"`) with a bounded timeout. Never `os.kill` a
   holder — a cooperative yield is the only eviction; killing mid-inference corrupts output
   *and* leaves VRAM allocated, which is the worst of both.
2. `exec` `sd-cli` as a child and **wait**. The lock records the PID of the process that
   took it; the worker's own PID is the right one, since it outlives the child.
3. On exit, release in a `finally` — `gpulock.hold` is a context manager for this reason.
4. Report the render's wall time and the peak VRAM with the result. 14e's gate is measured,
   not asserted, and the numbers have to come from the unit rather than from a separate
   benchmark run.

A crash anywhere in that sequence is survivable: the lock is a file recording a PID, and
`current()` reaps a holder whose PID is gone rather than reporting it.

## 9. Weights

**No weight enters git, in any format, at any size.** `acquisition/model-register.json`
carries the row and its state; `SYMON_MODELS_DIR` is `/home/google/symoneural-models`.

The image row — `flux1-schnell-q4_k.gguf` — is **ABSENT**, and the register's search result
records why: the old deployment's `backend/models` is not on this host. It stays ABSENT
until a measured run registers one by sha256 (Phase 12 S3 / 14c). The recipe deliberately
knows nothing about weights: it builds an engine, and an engine with no model is a correct
intermediate state, not a broken one.

**A gap, named and not filled.** `--backend te=cpu` means the text encoder is a *separate
file* from the UNet, and `generated/phase-14-report.md` records the prior run using two:
`symoneural-image-unet-q4_k.gguf` (`leejet/FLUX.1-schnell-gguf`) and
`symoneural-image-t5-q8_0.gguf` (`second-state/FLUX.1-schnell-GGUF`). The register today
has **one** Diffuse/image row and no `image-aux` row at all. Adding it is checklist item
14c, which has not been done; recording the gap here is not the same as closing it.

## 10. What is done, and what is not

| Checklist item | State |
|---|---|
| S3 acquire sd.cpp at `7f410a37` | **done** — ingested, LISTING-VERIFIED with 4 submodules |
| **14a** recipe, `SD_CUDA`, package `sd-cli` | **built.** bitbake rc=0; `sd-cli` 1.7 MB and `libstable-diffusion.so` 114 MB, packaged as a 63.7 MB ipk. S2 check: *"19 NEEDED entries resolved by providers; host-driver libraries used: libcuda.so.1"*. Evidence: `generated/evidence/phase-14/14a-evidence.txt`. **The binary has never been executed** — see the last row. |
| 14b onnxruntime CPU → rembg; whisper.cpp CPU | not started |
| 14c register rows `image`, `image-aux`, `asr`, `cutout` | not started |
| 14d units, launch lines, `Symoneural-Diffuse/app/` | **designed in §8 above; no code** |
| 14e contention test, ten alternations | not started |
| GATE: 768² within 20% of 11.2 s | **not measured — no weights on this host, so `sd-cli` has never been run.** Building an engine is not rendering an image, and this table will not blur the two. |

**Ordering, stated rather than glossed.** The phase's own line says *start after the
Phase 12 gate*; the queue instruction says *after phase 13 GATE PASSED*. Neither gate has
passed. 14a was built ahead of both under Garrett's standing instruction to make the thing
work and explain afterwards. That is a deviation from A7 ("do not acquire ahead of the
phase that builds the component") and it is recorded here as one, not presented as the
plan having been followed.
