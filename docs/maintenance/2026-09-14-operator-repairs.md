# Operator and verification repair record — 2026-09-14

Authority: Garrett explicitly stopped the other coder and authorized patches, updates and repairs. Reviewed repository HEAD: `eb5fbad94ce3abf7cd173c76df632855af77bd5e`. Existing uncommitted C7 work was preserved. This record describes this repair pass, not completion of every estate runtime.

## Current handoff state

**TRANSFER FOR CONTINUATION, 13:40 EDT:** Garrett requested a replacement-coder prompt because Codex credits are low. The controlled PyTorch rebuild with the Gloo prefix-map repair is still running (84%; host guard exit 1). A replacement coder may observe it now, but must not edit metadata or launch another build while it is live. Installation/package QA and consumer proof for that final result are not yet established. Do not mistake an `.ipk` written before a failed QA task for an accepted package.

Full handoff: `/home/google/Desktop/claude/SyMoNeuRaL-next-coder-repair-handoff.md`. One additional defect was reproduced after the 39-test run: `symon_cuda_qa_s2` discards a failed ELF-inspector status; its driver-entry summary count is also incorrect for repeated names. Four regressions were added; two currently fail against the still-unmodified function, while all four pass against the proposed minimal fix evaluated in memory. The actual class repair is **not applied**, because the cooker remains live. The final expected suite is 43 passing tests after that repair and normal BitBake QA verification.

The previous repair verification run reused the completed compilation and passed `do_install`, `do_package` and package writing, but correctly failed `do_package_qa`: four Gloo source/header paths remained in `libtorch_cuda.so`. No QA exemption was added.

## Repairs applied

| Surface | Repair and exercised evidence |
| --- | --- |
| `tools/symonbake` | Top-level help, runtime listing, build-path lookup and argument validation. Environment-setup and child failures propagate. Same-directory wrapper lock; host process check uses actual process identity and working directory. Removed global priority polling. Real help/list/path and isolated failure/lock tests pass. |
| `tools/edit-guard`, `tools/estate_processes.py` | Fail closed on a failed/unsupported process view; no “safe” result from Codex's private PID namespace. Actual host check returned 0 while quiescent and 1 while our BitBake run was live. This is a same-user, point-in-time check, not an atomic edit lock or protection from every possible process namespace. |
| `tools/nice-builds` | Select estate BitBake processes and descendants only. Unrelated Node/compiler processes are not selected by name. Dry-run supported; actual idle dry-run selected zero processes. No real priority changes were made by this repair audit. |
| `tools/build-all` | Aggregate all child failures, fresh per-run logs, validated concurrency, all 12 runtime directories, no stale success records. Real dry-run enumerated all 12; mocked failed builds return nonzero. No whole-estate build sweep was launched. |
| Four clean-root launchers | Generic, API, LLM and CUDA launchers now use new private roots. Existing destinations are rejected, never recursively removed. Image proofs require the corresponding manifest and fail on extraction errors. |
| Driver boundary checks | Empty driver versions cannot accept arbitrary packages. Driver-owned library/package names and exact upstream driver version are required. No prefix acceptance such as `615.71.090` matching `615.71.09`. |
| Generic clean-root tracing | Fail without target loader evidence; classify paths literally, including spaces/metacharacters. Distinguish the pre-target shell launcher from subsequent driver initialization. An independent review found the mixed shell/driver child case; it was corrected and regression-tested. Scope is loader **initialization records**, not proof of every memory mapping or an OS sandbox. |
| `tools/ingest-tree`, `tools/lib_acq.py`, `tools/git_tree_identity.py` | Nested Git tree verification now reconstructs and hashes tree bytes in memory. It no longer writes Git objects or temporary indexes. Genuine inspection failures propagate instead of becoming unexplained content mismatches. All current locked trees passed. |
| `tools/verify-acquisition.py` | Acquisition completeness failures return nonzero. Source comparisons include upstream URL, tree, recipe pin/path and lock state. Equally invalid records do not pass just because they agree. Actual full scanner reconciliation passes. |
| `tools/audit-workscope.sh` | Required subprocess failures propagate. Existing pkgdata is labelled historical package evidence, **not DONE or package QA**. Empty/unreadable authority fails. Current nonzero result identifies the existing GStreamer and `sv2-apps` placeholder recipes. |
| Python dependency checker | Reject unknown runtimes, absent/ambiguous target Python and zero-wheel coverage. `implementation_version` now reflects target Python. Check the selected runtime's package feed, not another runtime's feed; reject ambiguous/unverifiable package versions. Explicitly describes direct-wheel coverage rather than a complete runtime proof. |
| Native linkage checker | Strict subprocess status, fresh private package extractions, no shared timestamp cache/deletion or shell-interpolated package paths. Distinguishes the Python command from ELF libraries. Missing artifact coverage is nonzero. Actual seven-artifact package audit passes. |
| Saved-evidence checker | New `tools/check-evidence-hashes.py` checks original expected hashes, missing files and empty/malformed manifests. It does not regenerate expected hashes. Current old Common/LLM records fail visibly. |
| PyTorch recipe | RPATH verification examines ELF dynamic-tag values, not `chrpath`'s absolute filename. Real install passed. Gloo project hook supplies host prefix maps before Gloo snapshots its CUDA flags; no acquired-source patch or pin change. Final linked-library/package verification is still running. |

## Source and artifact evidence

The independent static source audit found:

- 92/92 top-level committed trees match their locks; 92/92 pin HEADs, pin trees and upstream remote identities match.
- 86/86 recorded submodule trees and parent gitlinks match.
- 110 recipe files inspected, including six retired recipes. All 1,638 recognized archive inputs have SHA-256 declarations. This is declaration coverage, not a fresh byte verification of 1,638 downloads.
- Manifest count 95 is not a missing-source count: it includes one separately managed build-stack entry and two explicit deferrals. Multiple static recipe mappings include retired provider recipes; two acquired sources are explicitly reference-only. The heuristic scan's mapping exceptions are not silently converted into acquisition failures.
- Full acquisition reconciliation: 92 source identities, 86 submodules, 16,247 dependency identities, 395 vendor identities, 551 licence-file identities, 94 provider identities, 92 artifact-capability identities and 387 source-collision identities agree with the current records. Zero acquired trees carry ignored residue in this audit.

The rewritten committed-tree verifier reports 85 ordinary VERIFIED entries plus seven LISTING-VERIFIED entries, covering 92 components and their 86 submodules.

Saved evidence is historical, not automatically current. The checked manifests contained 117 hash rows. At the post-package-attempt check: 109 match, four referenced LLM files are missing, and three same-named packages differ (Common PyTorch; LLM Python; ggml). These expected hashes were left intact. They require new, separately identified checkpoint evidence after the corresponding package/image/consumer proofs; rehashing current files is not proof that the old checkpoint passed.

## Tests actually run

- `python3 -B tools/test-estate-operators.py`: **39 tests PASS**. Temporary fixtures preserved. Covers failure exits, process detection/scope, wrapper lock, safe roots, missing/incorrect driver identities, trace absence/order, mixed S2 child traces, Git tree reconstruction, evidence mismatch preservation, package-path quoting, CMake hook scope and actual ELF RPATH rewriting.
- `tools/ingest-tree verify --all`: **exit 0**, all 92 locked sources verified.
- `python3 -B tools/verify-acquisition.py`: **exit 0**, control-plane and acquisition-completeness PASS. These are not all-runtime completion claims.
- `tools/build-all --dry-run`: **exit 0**, 12 runtime plans, no builds launched by the dry-run.
- `tools/clean-root-proof Ravencalc symoneural-image-ravencalc`: **exit 0**. Actual target Python and numerical/symbolic consumers, including two separate loky workers. 173 distinct target-library initialization paths across six traced processes, four verified shell transitions, no remaining external initialization paths.
- `tools/api-clean-root-proof` on the host with a 90-second timeout: **exit 0**. Upstream imports, native library/utility, packaged source-tree identity, native lock, app registry and in-process HTTP consumers pass. The sandbox attempt stalled in the in-process HTTP test and was stopped narrowly; its failed transcript is preserved, not reported as a pass. No live API server was used or changed.
- `python3 -B tools/check-native-linkage.py`: **exit 0**, seven packaged native/script artifacts checked. `libllama` imports 243 `ggml_*` symbols and defines zero; first-party API/LLM linkage remains independent.
- Full Python direct-dependency audit: correctly nonzero while Torch is unaccepted/missing and seven runtime selections have no built wheels. No wheel evidence in a native-only/unfinished runtime is **not** evidence that its native code fails.
- Full saved-evidence hash audit: correctly nonzero for the historical stale/missing artifacts above.
- PyTorch first repair attempt: actual `do_install` PASS, package QA FAIL on four Gloo paths. The repaired `libgloo_cuda.a` later rebuilt with zero build-directory strings; this is a component result, not final PyTorch QA.
- Shell syntax and `git diff --check`: PASS at the recorded checks; rerun after any later edits.

## Scope preserved and remaining work

No acquired source tree, source pin, source-lock record, filesystem sealing policy, NVIDIA driver installation, model weights, demo service or source-cache cleanup was changed. Normal BitBake task/sstate handling is not a manual cache deletion. No commit or push has been performed. New helper/test files are untracked until explicitly included in a reviewed commit; the wrappers depend on those helper files and must not be committed alone.

The other coder's existing changes to `symoneural-cuda.bbclass` and `tools/proofs/common.py` remain its work, not repairs authored in this pass. The PyTorch recipe and generic proof launcher contain both prior work and this pass's targeted changes.

After final PyTorch QA, the remaining C7 checkpoint workflow still requires the intended Common image, Accelerate's packagegroup/ruling transition and actual `prepare()` consumer proof, Common non-S2/S2 proofs, and newly recorded evidence. The current Common packagegroup still deliberately excludes Accelerate pending those proofs. Do not silently mark it included or complete.

GStreamer and `sv2-apps` remain scheduled implementation work, not completed runtimes. NVIDIA two-target kernel integration remains pending; this repair pass does not authorize host installation/loading or claim that kernel modules alone close the proprietary userspace/GSP firmware boundary. The LLM generation proof remains distinct from tensor-free vocabulary tests and depends on an approved available model.

## Evidence locations

Repair-session logs and raw results are in `/tmp/symoneural-estate-audit.skHs1A/`: `operator-tests.txt`, `source-audit.json`, `ingest-after.txt`, `verify-acquisition-after.txt`, `workscope-after.txt`, `closure-after.json`, `native-linkage-after.json`, `evidence-hashes-after.json`, `ravencalc-proof-after.txt`, `api-proof-after.txt`, `api-proof-host-after.txt`, `torch-dry-run.txt`, `torch-repair-build.txt` and `torch-gloo-repair-build.txt`.

The temporary evidence directory is not archival storage. Preserve the reviewed final transcripts with the eventual checkpoint before reboot/cleanup. This document records observed results without rewriting old checkpoint manifests.

## Completion by the replacement coder (Claude, 2026-09-14, 16:00–16:50 EDT)

Observed, not inferred: Codex's controlled build finished at 14:12 EDT — 2231 tasks, `do_package_qa`
PASS, S2 note "98 NEEDED entries resolved by providers; host-driver libraries used: libcuda.so.1".
Packaged `symoneural-pytorch_2.14.0-r0` (208,784,028 B, sha256 `8c010d753e4c4209…`): every torch/lib
library RPATH `$ORIGIN`, 0 build-path strings, 419 sm_120 kernels.

- `symon_cuda_qa_s2` repair applied exactly as specified after `tools/edit-guard` returned 0 (a nonzero
  `readelf` status is fatal with "ELF inspection failed"; provider-resolved count = checked − S2 entries).
  `python3 -B tools/test-estate-operators.py`: **43 tests PASS**. Dry-run then normal target: 23 tasks
  (torch `do_package_qa` + image chain); QA PASS with the repaired post-function (`log.do_package_qa.1409652`).
- Ravencalc re-proven PASS under the merged harness (Codex's fresh roots + tracing, the other coder's S2/leak logic).
- Common image rebuilt with `symoneural-accelerate` restored: rootfs-20260914203500, 131 packages, sha256
  `464dab39b9b19a7f…`. A first attempt was killed by the agent harness mid `do_image_tar` (memory-pressure kill
  of the launching shell took the cooker with it; the previous deploy had already been cleaned); the image
  recipe was `-c clean`ed and rebuilt detached, so no partial artifact remains in deploy.
- Common clean-root proofs: CPU mode PASS (no host file mapped); S2 mode PASS on the RTX 5070 Ti
  (`Accelerator(cuda).prepare()` + epoch). The first S2 run failed the leak check honestly: with `PATH` unset,
  `shutil.which("nvidia-smi")` in `accelerate.utils.environment` found and ran the host's `/usr/bin/nvidia-smi`.
  The generic launcher now confines `PATH` to the root; re-run PASS with only the five driver-owned host files.
- Accelerate ruling promoted by that evidence (records + `docs/common/COMMON-CLOSURE.md`).
- Evidence from `/tmp/symoneural-estate-audit.skHs1A/` preserved at
  `generated/evidence/maintenance/2026-09-14-operator-repairs/` (20 files + `SHA256SUMS`).
- `tools/check-evidence-hashes.py`: 131 MATCH after `generated/evidence/cuda/CUDA-SHA256SUMS` (24 current C6/C7
  artifacts); 3 MISMATCH + 6 MISSING remain in the P9-era `llm/LLM-SHA256SUMS` and `common/COMMON-SHA256SUMS`
  rows for artifacts superseded by the C6/C7 rebuilds — left as recorded, not regenerated.

Not done here: REPRODUCIBILITY (no differing-root build), INTEGRATION, any NVIDIA kernel build.
