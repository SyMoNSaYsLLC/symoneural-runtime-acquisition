# Common runtime — closure, clean-root and consumer proof

> **Status update 2026-09-14 (P7 C7).** The accelerate deferral below ended with the CUDA/
> distributed PyTorch build: `symoneural-accelerate` is back in `packagegroup-symoneural-common`,
> and `Accelerator.prepare()` + one SGD epoch PASS in both Common clean-root proof modes
> (CPU without the driver; S2 on the RTX 5070 Ti). Ruling `accelerate-torch-distributed`:
> RESOLVED BY EVIDENCE; component-state accelerate: TARGET. Evidence and the full C7 record:
> `docs/cuda/P7-CUDA-AUTHORITY.md` §C7, `generated/evidence/common/COMMON-CLEAN-ROOT-PROOF.txt`,
> `generated/evidence/cuda/COMMON-CLEAN-ROOT-PROOF-S2.txt`. The sections below are the P8
> record and are left as written.


Recorded 2026-09-14. Runtime: `Symoneural-Common` (Torch + Transformers foundation).
Proof harness: `tools/clean-root-proof Common symoneural-image-common` running
`tools/proofs/common.py`. Evidence files: `generated/evidence/common/`.

## Status at this checkpoint

| Stage | Result | Evidence |
| --- | --- | --- |
| SOURCE VERIFIED | PASS | `tools/ingest-tree verify --all`: 92/92, every Common tree VERIFIED (pytorch LISTING-VERIFIED, 65 submodules) |
| BUILD PASS | PASS | `symoneural-image-common` final: `rootfs-20260914101505`, 5832 tasks, 0 ERROR; every earlier run 0 ERROR too |
| PACKAGE PASS | PASS | every `symoneural-*` package in the image: `do_package_qa` 0 ERROR; buildpaths bytes absent from `packages-split` |
| CLEAN INSTALL PASS | PASS | rootfs assembled by opkg from the feed; extracted and run through the target loader with `env -i` |
| RUNTIME/IMPORT PASS | PASS | 29 distributions imported by the target interpreter; no host path on `sys.path` |
| MEANINGFUL CONSUMER PASS | PASS | tokenizers→transformers→torch→safetensors path, below |
| CLOSURE PASS | PASS | `tools/check-python-runtime-closures.py --runtime Common`: 59 PASS, 0 fatal, RESULT PASS |
| REPRODUCIBILITY PASS | NOT TESTED (partial evidence) | two independent `do_rootfs`+`do_image_tar` executions from the same recipe state produced byte-identical rootfs tarballs (`08fb05df…`, see below); package-level differing-root comparison not run |
| INTEGRATION PASS | NOT TESTED | Common is consumed by Adaptive-Fabric / Tune; those stages are P11 |

**accelerate is DEFERRED BY RECORDED RULING** (Garrett, 2026-09-14; see below) and is
not shipped. Common is PASS for the surface `packagegroup-symoneural-common` declares;
the audit counts accelerate as exempt by ruling.

## What changed to get here

The first Common image (`rootfs-20260914091329`, 5748 tasks, 0 ERROR) already
carried 13 newly owned providers — filelock, fsspec, hf-xet, markdown-it-py, mdurl,
packaging, pygments, pyyaml, regex, rich, shellingham, tqdm, typer — and closed the
huggingface-hub and transformers edges. Against it the closure checker still
reported **3 UNRESOLVED SOURCE OWNERSHIP**, all on `symoneural-pytorch`:

```
Requires-Dist: setuptools>=77.0.3
Requires-Dist: networkx>=2.5.1
Requires-Dist: jinja2
```

All three are **unconditional** in torch 2.14's wheel metadata (no marker), so under
"own what you ship" they are SyMoNeuRaL-owned acquisitions, not layer borrows. jinja2
brings `MarkupSafe>=2.0`. Four trees were acquired at their release tags — newest
stable, each equal to the layer's own version so the OE recipe mirrors exactly:

| component | tag | commit | licence (md5 from OUR tree) |
| --- | --- | --- | --- |
| setuptools | v84.0.0 | `72e919a8b10aaafc041205d4e3ae0e6a2e1e5f87` | MIT `141643e11c48898150daa83802dbc65f` |
| jinja2 | 3.1.6 | `15206881c006c79667fe5154fe80c01c65410679` | BSD-3-Clause `5dc88300786f1c214c1e9827a5229462` |
| markupsafe | 3.0.3 | `297fc8e356e6836a62087949245d09a28e9f1b13` | BSD-3-Clause `ffeffa59c90c9c4a033c7574f8f3fb75` |
| networkx | networkx-3.6.1 | `7530809bfa1ea7ed6fdf918a4d1431488953cb1f` | BSD-3-Clause `f7592b173aee2da0e062f9cfa0378e9d` |

Each: `HEAD == pin`, `git status --short` empty, zero submodules, ingested with
`tools/ingest-and-commit` (tree object, never `git add`), re-verified from the lock.

Two deliberate deviations from the mirrored OE recipes, both recorded in the recipes:
oe-core's setuptools applies a cross-sysconfig `.patch` — not carried, the estate
builds pristine source and this copy is a runtime library for torch, never a build
tool; meta-python's networkx still lists `python3-decorator` — networkx 3.6.1's
`pyproject` declares `dependencies = []`, so no such edge exists.

`symoneural-pytorch` now declares all seven of its runtime edges on estate providers.

After the rebuild (`rootfs-20260914095335`, 5832 tasks, 0 ERROR):

```
Common: 43 direct wheels, 39 distinct runtime requirements -> 43 upstream runtime sources
  PASS  59
RESULT: PASS
```

## The clean-root / consumer proof

`tools/proofs/common.py`, run inside the extracted image by the target interpreter
through the target `ld.so`, with an empty environment. What it establishes:

- **Install record.** The image sets `IMAGE_FEATURES = ""`, so OE removes
  `/var/lib/opkg` from the rootfs; the deploy manifest is the install record and the
  harness now hands it to the proof (`SYM_IMAGE_MANIFEST`). Every `symoneural-*`
  package the closure needs is present.
- **No build frontend shipped.** Checked before anything imports setuptools, because
  setuptools 84 puts its own `_vendor/` on `sys.path` once imported — after that,
  `import wheel` resolves to `setuptools/_vendor/wheel`, which the proof asserts is
  the *only* place a `wheel` resolves from. No top-level `wheel`, `pip`, `maturin`,
  `hatchling` or `flit_core` in site-packages. setuptools itself is deliberately not
  on the refused list: torch declares it as a runtime requirement.
- **The declared closure is the gate.** Every `Requires-Dist` of torch, transformers,
  huggingface-hub, tokenizers, typer, rich, markdown-it-py, Jinja2, sympy and
  safetensors, with markers evaluated for the target, is checked against the version
  actually installed (34 requirements).
- **torch's runtime edges are live imports, not metadata.**
  `import torch.utils.cpp_extension` imports setuptools at module load; `torch.fx`
  traces a module.
- **Consumer path.** tokenizers trains a BPE tokenizer *in-process* from an iterator
  (Rust) and round-trips text; transformers wraps it as `PreTrainedTokenizerFast`,
  builds `BertModel` from a `BertConfig` (no weights, no hub) and runs a forward pass
  on torch → `(2, 6, 32)` finite hidden states; safetensors round-trips the
  `state_dict`; huggingface_hub, under `HF_HUB_OFFLINE=1` set before import, is asked
  for one download and the proof asserts the exception's **cause** is
  `OfflineModeIsEnabled` — refused before any connection, not failed after one.
- **Every other provider does one real thing**: hf_xet loads (Rust); PyYAML through
  libyaml (`CLoader`/`CDumper`); `regex \p{Greek}`; filelock acquire/release; fsspec
  local fs; tqdm; packaging parses `2.14.0a0+gitunknown`; typer `CliRunner` exit 0;
  rich renders a table; pygments highlights; markdown-it-py renders a link (mdurl);
  shellingham detects or raises `ShellDetectionFailure`; jinja2 escapes through
  `markupsafe._speedups` (the C extension, asserted via `_escape_inner.__module__`);
  networkx `shortest_path`.
- **NO NETWORK.** No model weights fetched or present.

The proof transcript, install manifest and checksums are in
`generated/evidence/common/`.

Final image proven: `symoneural-image-common-qemux86-64.rootfs-20260914101505.tar.gz`,
247566972 bytes, sha256 `08fb05df1dfc5a87f644f5e19b95c1c2ad9ab7c30ad3c52b9927701a836d671e`,
127 packages / 45 `symoneural-*`. Transcript ends `COMMON CLEAN ROOT PROOF: PASS`.

**Reproducibility datapoint.** `rootfs-20260914095335` (built 05:56) had the same
sha256 `08fb05df…` and the same size. Between them the packagegroup was changed and
changed back, so the final run's `do_rootfs`, `do_image`, `do_image_tar` and
`do_image_complete` all *executed* (task `Started` lines in the log, not setscene).
Two independent assemblies of the same declared input produced a byte-identical
tarball. This is evidence for the image-assembly stage only; it is not the
differing-build-root, package-level comparison the reproducibility gate requires.

## accelerate — DEFERRED BY RECORDED RULING, not shipped

`symoneural-accelerate` was the one Common TARGET component `tools/audit-workscope.sh`
reported as `RECIPE, NEVER PACKAGED`. Its recipe borrowed three runtime providers from
the layer (`python3-packaging python3-psutil python3-pyyaml`). To close it under
policy: psutil was acquired (`release-7.2.2`, `9eea97dd6f1d16ea33f5144c8925f1ce7a0688e1`,
BSD-3-Clause `a9c72113a843d0d732a0ac1c200d81b1`; the objective document had already
tabled it), the recipe's edges were moved to `symoneural-packaging symoneural-psutil
symoneural-pyyaml`, and it was added to the packagegroup. It **builds and packages
cleanly** (QA 0 ERROR, buildpaths clean, ipk emitted) and the closure checker shows all
seven of its edges PASS on estate providers.

It is **not usable on this torch**. In the clean-root proof, with the image that
carried it (`rootfs-20260914100830`, 5875 tasks, 0 ERROR):

```
common.py:202  acc.prepare(net, opt, data)
accelerate/accelerator.py:1558  prepare
accelerate/accelerator.py:1404  _prepare_one
accelerate/accelerator.py:1802  prepare_model
accelerate/utils/other.py:243   model_has_dtensor
    from torch.distributed.tensor import DTensor
ModuleNotFoundError: No module named 'torch._C._distributed_c10d'; 'torch._C' is not a package
```

`torch.distributed.is_available()` is `False` on the target: `symoneural-pytorch` is
built `USE_DISTRIBUTED=0`. Upstream accelerate guards that import on torch *version*
only (`is_torch_version(">=", "2.5.0")`), never on `is_available()`, because torch's
own Linux default is `USE_DISTRIBUTED=1`. `import accelerate` itself succeeds; the
core API does not. Pristine source is not patched.

So accelerate was **removed from the packagegroup again** and the finding recorded in
its recipe and the packagegroup. The audit will still print it as DONE because an ipk
exists — that DONE is not a usable component and this record says so.

**Ruling (Garrett, 2026-09-14): DEFERRED BY RECORDED RULING** to the final PyTorch
feature-set/CUDA phase. Torch is **not** rebuilt now. The alternative considered —
rebuilding torch with `USE_DISTRIBUTED=1` (upstream's Linux default; gloo on CPU) —
would have reversed the recipe's recorded CPU-only decision at a cost of hours; that
decision's stated purpose, "unblocks Common's chain (accelerate RDEPENDS on
pytorch)", is noted here as not achieved, for the phase that revisits it.

Recorded in `acquisition/component-state.json` (Common/accelerate → `DEFERRED`, with
reason and ruling) and `acquisition/unresolved.json` (`accelerate-torch-distributed`,
BUILD-DESIGN, resolved DEFERRED). accelerate stays acquired, pinned, recipe'd with
estate-owned edges and packaged in the feed. `tools/audit-workscope.sh` now prints the row
as `DEFERRED`, lists accelerate among the 15 exemptions, and prints Common
`sources committed 24/24 · packaged 24/23` — the numerator still counts the exempt
package because its ipk exists while the denominator excludes it; read it as 23 owed,
23 packaged, 1 deferred.

## Records

- `acquisition/provider-decisions.json` `python_runtime_providers`: rulings added for
  the 13 providers' shipped neighbours that had recipes but no recorded ruling
  (fastapi, pydantic, uvicorn, starlette, httpcore, httpx, sympy, mpmath,
  huggingface-hub, tokenizers, safetensors — flagged by the checker as "recipe exists;
  record the decision") and for setuptools, jinja2, markupsafe, networkx, psutil,
  accelerate. All SYMONEURAL-OWNED under the recorded rule.
- `acquisition/component-state.json`: 18 Common rows added, all TARGET (curated; read
  by `tools/audit-workscope.sh`).
- `acquisition/source-manifest.json`, `acquisition/pending-acquisitions.json`: the
  five new sources; pending rows say plainly they were not pre-queued.
- Derived records regenerated by the scanner suite (`scan-dependencies`,
  `scan-oe-providers`, `scan-source-collisions`, `generate-runtime-acquisition`);
  `check-determinism.py` byte-identical across two runs; `verify-acquisition.py`
  CONTROL-PLANE PASS, ESTATE-COMPLETENESS PASS, 0 WARN (it had been FAIL on
  `LICENCE-EVIDENCE-ABSENT` for every new Common tree — the licence inventory was
  stale, not missing).
- The `do_create_image_sbom_spdx` warning about `libsymoneural-api1` /
  `libsymoneural-api-util` was a stale sstate artefact: the packagegroup's SPDX doc
  (00:13) predated commit `6d3ec77ed` (00:19) that pinned the names with
  `DEBIAN_NOAUTONAME`. Forced `-C create_spdx packagegroup-symoneural-api`; the
  warning is gone from every later image build.

## Estate-wide, unchanged by this work

`ACQUISITION-STATE VERDICT: FAIL` — 86 provider collisions unresolved (56
direct-vs-OE-Core), 366 vendored decisions, 429 licence files without an identifier,
1 explicit decision open (FreeToken/torch). Other unpackaged TARGET rows: FreeToken
(Adaptive-Fabric), stratum (Crypto), cython (Ravencalc); sv2-apps and gstreamer have no
class build. Named, not acted on.

The image pulls the whole stdlib split (`python3-modules`: idle, tkinter, ensurepip
with a bundled `pip-26.2.1` wheel) through `packagegroup-symoneural-api`'s `python3`
edge — a runtime-surface question inherited from API, not a Common regression. Named,
not acted on.
