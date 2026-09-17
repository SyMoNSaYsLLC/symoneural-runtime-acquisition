# Host truth, 2026-09-17 — and the corrections it forces on the 16/17 September documents

Every line below was produced by a command run **on `symon` itself**, not on a sandbox
mount. Raw output: `generated/evidence/maintenance/2026-09-17-host-truth.txt` and
`generated/evidence/maintenance/2026-09-17-cli-anthropic-httpx2-import.txt`.

Context: nine chat-output files dated 16–17 September were reviewed against the
repository in `~/Desktop/github/claude-2026-09-17-estate-review-disk-vs-github.md`.
That review was written from a read-only mount and said so; it explicitly left the host
checks to be run here. Two of its findings do not survive contact with the host, and
one document claim that three separate files repeat is now disproved.

---

## 1. The GPU driver is still the OPEN kernel module — the reported change did not happen

The review's finding 14 recorded, on a verbal report, that the host had moved from the
NVIDIA open GPU kernel modules to the **proprietary** module, and asked for a
maintenance note saying so. The host says otherwise:

```
$ cat /proc/driver/nvidia/version
NVRM version: NVIDIA UNIX Open Kernel Module for x86_64  615.71.09  Release Build  (root@symon)  Tue Sep 15 10:45:45 AM EDT 2026
GCC version:  gcc version 14.2.0 (Debian 14.2.0-19)
```

`NVIDIA UNIX Open Kernel Module` is the open flavour's own string; the proprietary
module prints `NVIDIA UNIX x86_64 Kernel Module`. Supporting evidence, same run:

| Check | Output | Reads as |
|---|---|---|
| `dpkg -l nvidia-kernel-open-dkms` | `ii  nvidia-kernel-open-dkms  615.71.09-2` | the **open** DKMS source is what is installed |
| `dpkg -l nvidia-kernel-dkms` | `ii  nvidia-kernel-dkms  615.71.09-2  Transitional dummy package` | **this is the trap.** The package whose name says "proprietary" is, at this version, a Debian transitional dummy that pulls the open flavour. Reading the package list alone produces exactly the wrong conclusion |
| `ls /lib/modules/6.12.107+deb13-amd64/updates/dkms/` | `nvidia.ko.xz` + 4 siblings, all `Sep 15 10:46` | rebuilt by DKMS on 15 Sep, one minute after the module build stamp above — this is the event that was reported as a flavour change. It was a **rebuild of the same open flavour**, most likely after a kernel or driver package update |
| `lsmod \| grep ^nvidia` | `nvidia 18489344 784`, `nvidia_uvm`, `nvidia_modeset`, `nvidia_drm` | loaded and in use |
| `nvidia-smi` driver version | `615.71.09` | agrees with `/proc/driver/nvidia/version`; CUDA will initialise |

`modinfo` and `dkms` are not on this user's `PATH` (`rc=127` for both) — which is why the
review's command sketch could not settle it, and why `/proc/driver/nvidia/version` is the
check to keep.

**Consequences.** The 14 September two-target NVIDIA open-kernel work is *not* stranded:
the host runs the same flavour and the same version (615.71.09) the estate builds against.
The two open decisions (`nvidia-userspace-driver-provider`,
`nvidia-gsp-firmware-provider`) are unchanged in character — the userspace libraries and
GSP firmware still come from NVIDIA's Debian packages (`libcuda1 615.71.09-2` is
installed), and the estate still has no provider of its own. Loading an estate-built
`nvidia.ko` on this box would still collide with the DKMS module that is loaded now, open
or not; that step is unchanged and still unauthorised.

**What is genuinely new**: the modules on disk were rebuilt on 15 Sep, so any GPU
measurement taken before that date was on a different build of the driver. Record the
build stamp (`Tue Sep 15 10:45:45 AM EDT 2026`) beside GPU runs, as the review asked — the
reason was right even though the flavour claim was not.

---

## 2. `anthropic-sdk-python` is not an R16 phantom — it imports, from the estate's own Python

Three documents (`claude-2026-09-17-api-tree-concrete.md` §0/§5/§7,
`claude-2026-09-17-gameplan.md` finding 8 and S7, and the 16 September report) record the
estate's anthropic SDK as a *candidate phantom*: "built, 2,817 files" but `httpx2` —
which `anthropic` imports at `_base_client.py:39` — believed unsourced. The repository
already contradicted the acquisition half (component `httpx2`, commit `71ae23be5448`,
`VERIFIED`, recipe and `.ipk` on disk). The import half is now settled too:

```
$ tools/clean-root-proof CLI symoneural-image-cli          # rc=0
image   : symoneural-image-cli-qemux86-64.rootfs-20260914053558.tar.gz
sha256  : 5bfecdb79b45025b62f967e26c5f68f10a81008feaa783e0b1deaa7f1a775e69
python 3.14.7 prefix <disposable root>/usr
  anthropic                  1.5.0        PASS
  httpx2                     2.12.0       PASS
  httpcore2                  2.12.0       PASS
  truststore                 0.10.4       PASS
  jiter                      0.17.0       PASS
  meaningful ops PASS: ... httpx2 built a POST (unsent); anthropic SDK built a
  /v1/messages request locally, never sent; ...
CLI CLEAN ROOT PROOF: PASS
  none: no external library initialization in captured loader traces
```

The interpreter is the image's own Python 3.14.7, reached through the image's loader with
an empty environment; the loader traces show **no host library** was used. This is the
artifact-level and consumer-level proof R16 asks for, and it is stronger than the
`PYTHONPATH` import the review proposed (the recipe work trees have since been cleaned,
so the `.ipk` and the image are the only artifacts left).

**Consequence**: the gameplan's step **S7 precondition is met**. "API step 2 with the
estate `llama-server`" is no longer blocked on an acquisition; what remains is wiring, not
sourcing. Delete the `httpx2` row from every open-work list.

---

## 3. Host facts the documents disagreed about

| Question | Documents | Host says | Note |
|---|---|---|---|
| CPU shape | 16 Sep report: FreeToken JSON `physical_cores: 4`; handbook: 10c/20t | **i9-10900KF, 10 cores / 20 threads, 1 socket**, `Virtualization: VT-x`, no hypervisor line | The JSON's `4` is wrong. Every CPU-side figure in the 16 Sep report is a 4-thread number on a 10-core machine and understates the host. `avx2` and `fma` only — **no AVX-512, no AMX**, which caps CPU-side expert compute more than the core count does |
| PCIe link | "Gen 3 ×8 host-capped, 6.94 GB/s measured" | `gen.current 3`, `gen.max 3`, **`width.current 8`, `width.max 16`** | Confirmed, with one addition the documents missed: the *card* can do ×16 and is negotiating ×8. The ×8 is the slot, not the card. Moving it to a ×16 slot is the single change that would roughly double every offload figure — a platform change, still not a software item |
| Host RAM | not in the JSON | **94 GB total, 82 GB available**, 31 GB swap | Enough for the expert-offload cases the report modelled |
| Chat worker port | handbook `:8081`; transcript `:8802` | **Nothing is listening on 8081, 8802, 8800, 8000 or 7966.** The repository defines 8802 in both places: `Symoneural-API/app/symoneural_api/units.py:62-69` and `Symoneural-LLM/app/symoneural_llm/main.py:36-38`. `8081` does not occur anywhere in the first-party tree | The listener cannot arbitrate because no API is running. The repository wins: **8802**. `units.py`'s description still says "via llama-server" while `symoneural_llm` says it is that process — one of those lines is stale and should be fixed when `Unit(...)` moves to a registry file |
| Port 7966 free | proposed by D7 | free — not in the listening set | Nine other local services are listening (ssh, a database, printing, a remote-desktop port among them). The full inventory is deliberately **not committed** — this repository is public and a listening-socket map of the workstation does not belong in it. It is at `~/Desktop/claude/2026-09-17-host-truth-FULL-local-only.txt`. One of them, a remote-desktop port bound to all interfaces rather than loopback, is worth Garrett's attention independently of this work |
| `127.0.0.1:8800` | R14: "read-only and demo-critical" | **not listening** | The demo is down. R14 still stands as a rule; there is nothing running to disturb today |
| Auth model | "two credentials, `KeyRing`, 403 `operator_required`" | `routeclass.py:27-32` — five classes: `PUBLIC_BOOTSTRAP, SHARED_AUTH, AUTHENTICATED_APPLICATION, ENTITLEMENT_REQUIRED, OPERATOR_ONLY`; operator failure → **404** (`:116-119`, "should not confirm its own existence"), entitlement failure → 403 (`:125`) | The reference gateway's `KeyRing`/403 is superseded. A conformance check for operator routes must expect **404**, not 403 |
| FreeToken: how many, which | gameplan §5: "estate pin 0.1.2 and the Desktop's 0.2.0-beta.19 app" | Two installs, **both 0.1.3 at `cac247a86`**: `~/SymonSaysLLC/FreeToken/.venv` reports `0.1.3`, `~/.freetoken/venv` reports `0.1.3+gcac247a86`. The **acquired pin is still `9db1a39455a3`** (0.1.2) | Simpler than the documents had it. D4 (move the pin to `cac247a860e3`) would align the pin with both working copies; it remains an acquisition change, not done |

---

## 4. Model storage — five roots, and two of them are not where any document says

| Path | Size | What it is |
|---|---|---|
| `/home/google/SymonSaysLLC/models` | **35 GB** | `gpt-oss-20b` (13 GB) and `Qwen3.6-35B-A3B-NVFP4` (22 GB). **A mount point**: `/etc/fstab` line 6 mounts `UUID=baf9f6dc-…` (`/dev/nvme0n1p7`, 143 GB) here. Not a directory the repository created |
| `/mnt/models` | **75 GB** | `/dev/sdb1`, a 916 GB disk labelled `models`. Holds only `.hf-cache`: `models--openai--gpt-oss-120b` (53 GB) and `models--google--gemma-4-26B-A4B-it` (23 GB) — the **two abandoned downloads** the gameplan named. 795 GB free |
| `/home/google/symoneural-models` | 24 KB | The empty skeleton the model register names in `SYMON_MODELS_DIR` (`hf/ llm/ image/ rembg/ whisper/`) |
| `/yocto/models` | absent | The handbook's path does not exist |
| `/var/lib/symoneural/models/llm` | absent | The worker's `DEFAULT_REGISTRY` does not exist |

Every row of `acquisition/model-register.json` is still `ABSENT`; nothing above is
registered, so Chat cannot activate. That is unchanged and correct — registration is
gated on a T2/T3 measurement (decision D2), not on the bytes existing.

**The git hazard this created has been closed.** `models/` was untracked and *not*
ignored: a `git add .` would have staged third-party model cards (`config.json`,
`README.md`, `LICENSE`, `model.safetensors.index.json`) and, for a Hub-cache layout,
weights stored as `blobs/<sha256>` with no extension at all — which the extension rules
cannot catch. `.gitignore` now denies the **directories**: `/models/`, `/FreeToken/`,
`/files*.zip`. Verified against paths that exist, not hypothetical ones:

```
$ git check-ignore -v models/gpt-oss-20b/config.json models/gpt-oss-20b/model.safetensors.index.json
.gitignore:166:/models/   models/gpt-oss-20b/config.json
.gitignore:166:/models/   models/gpt-oss-20b/model.safetensors.index.json
```

**Not done, for Garrett**: whether `/dev/nvme0n1p7` should be re-mounted outside the
repository (one `/etc/fstab` line, then `systemctl daemon-reload` and a remount) and
whether the 75 GB of abandoned partials on `/mnt/models` should be removed. Both are his;
neither is needed to make the repository safe.

---

## 5. What was moved, and where it went

| Was | Now | Why |
|---|---|---|
| `SymonSaysLLC/symoneural-runtime-acquisition/` (5.6 GB, a clone of GitHub `main` at `769b4f3ae`) | `~/symoneural-runtime-acquisition-github-769b4f3ae` | A git repository nested inside the estate repository. Kept as the "what GitHub has" reference |
| `SymonSaysLLC/FreeToken/` (6.8 GB) | **left in place**, ignored | Moving it would break it: its console scripts carry an absolute shebang into `/home/google/SymonSaysLLC/FreeToken/.venv/bin/python`, and `ft --version` works today (`0.1.3`). The 17 Sep test plan's T0 path stays valid |
| `SymonSaysLLC/files.zip`, `files2.zip` | extracted to `~/Desktop/claude/` (8 files, hashes match the originals); originals left in place, ignored | Where their own headers say they belong |

Nothing was deleted.

---

## 6. Verification run today (all rc read directly, never through a pipe)

| Check | Result |
|---|---|
| `tools/edit-guard`, `meta-symoneural/tools/edit-guard` | both rc=0, same message — no cooker live, and the 15 Sep `exec` shim works |
| `bash -n` ×3, `python3 -m py_compile` ×2 | five rc=0 |
| `python3 -B tools/test-estate-operators.py` | **44 tests OK**, rc=0 — the count the record claimed, now on disk at `generated/evidence/maintenance/2026-09-15-verification-fixes/operator-tests.txt` |
| `tools/generate-runtime-acquisition.py` | rc=0; no literal `%d` left; Provider-graph line renders (`2760 / 2823 / 104`); `sympy-mpmath-constraint` no longer counted as open; derived counts replace the stale curated ones (vendored 366 → **406**, licence files 429 → **568**) |
| `tools/check-determinism.py` | rc=0, `RUN_A_SHA256 == RUN_B_SHA256`, 20 tools hashed |
| `tools/verify-acquisition.py` | rc=0, `CONTROL-PLANE RESULT: PASS`, `ESTATE-COMPLETENESS RESULT: PASS` |
| `tools/pre-publish-audit.sh` | **AUDIT PASS**, rc=0. Secret content clean in tree *and* in history (the new scan); weight magic bytes none; files over 100 MB none; tracked size 4.8 GB; **35 commits ahead**; **pack a push would send: 42 MB** (no batching needed); the four `.gitignore` preconditions present; untracked list exactly 5 paths |
| `tools/clean-root-proof CLI symoneural-image-cli` | rc=0, PASS — §2 above |

---

## 7. Open, and whose it is

1. **The push.** 35 commits plus today's are not on GitHub, the audit passes, and the pack
   is 42 MB. Not pushed: the standing rule is no push without Garrett's word, and the
   repository is now **public** (an unauthenticated `git ls-remote` succeeded), which
   raises the stakes rather than lowering them.
2. **`config/claude-desktop/*.json` on a public repo.** Four tracked files. Read today:
   they hold **no key values** — the content is four account UUIDs, one org UUID, a
   `python3` MCP command line, an extensions blocklist and boolean preferences. Not
   credentials; still account identifiers, and publishing them is Garrett's call, not
   mine.
3. **The `models` mount point** (§4) and the **75 GB of abandoned partials**.
4. **Phase 10's status** still disagrees across three documents: `PHASE-INDEX.md` says
   CLOSED at `1f007af`, `phase-11-report.md` says the gate passed, `phase-10-report.md`
   has no STATUS line at all. The MCP server now reports that honestly
   ("NO STATUS LINE IN REPORT — not evidence of closure") instead of inferring closure.
   Unadjudicated since 15 Sep.
5. **D4**, the FreeToken pin move to `cac247a860e3` — recorded in the 17 Sep documents,
   not done; it is an acquisition change.
6. The stale `"via llama-server"` description in `units.py` (§3).
