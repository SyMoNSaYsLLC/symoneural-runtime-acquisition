# DEPENDENCY CLOSURE RESOLUTION

**STATUS: RESEARCH HOST. NON-AUTHORITATIVE.**
Nothing below is promoted to authoritative build status. All hashes, crate lists and
counts are research-derived and must be regenerated on the accepted reference machine.
No builds were executed for this report.

---

## 1. CLEANUP RESULT

| Action | Result |
|---|---|
| Delete Ravencalc `build/devtool/tmp-glibc` | DONE — 11 GB removed |
| Delete Ravencalc `sstate-cache` | DONE — 348 MB removed |
| Preserve `downloads` / `DL_DIR` | PRESERVED — 3.5 GB intact |
| Shared-cache safety check | **PASSED before deletion** |

Shared-cache check detail: `SSTATE_DIR` was grepped across all 12 workspace `local.conf`
files. Exactly **one** workspace referenced `Symoneural-Ravencalc/sstate-cache` — its own.
Every runtime has a dedicated `SSTATE_DIR`. No shared cache was deleted.

The old TMPDIR is gone and cannot be reused. 11.3 GB reclaimed.

---

## 2. CORRECTED LICENCE RECORD

### GStreamer — recorded at two distinct layers, not as a contradiction

**LAYER A — SOURCE LICENCE EVIDENCE (upstream 1.28.7 as acquired)**

Every vendored subproject ships `COPYING` = LGPL-2.1. A grep for non-Lesser
"GNU General Public License" headers across `gst-plugins-ugly/ext` and `/gst` returned
EMPTY. The GPL codec libraries are **not vendored** — `x264`, `lame`, `fdk-aac`, `FFmpeg`
exist only as meson `.wrap` download references. Confirmed: no `subprojects/x264` directory.

| File | md5 (LIC_FILES_CHKSUM) | sha256 (source lock) |
|---|---|---|
| COPYING (core) | 69333daa044cb77e486cc36129f7a770 | ad2eec519ebd4b5df86ea84dff24ae3bfa2edea846a703b58902dd221ae375db |
| subprojects/gst-plugins-good/COPYING | a6f89e2100d9b6cdffcea4f398e37343 | 6095e9ffa777dd22839f7801aa845b31c9ed07f3d6bf8a26dc5d2dec8ccc0ef3 |
| subprojects/gst-plugins-ugly/COPYING | a6f89e2100d9b6cdffcea4f398e37343 | 6095e9ffa777dd22839f7801aa845b31c9ed07f3d6bf8a26dc5d2dec8ccc0ef3 |

**LAYER B — BUILT ARTIFACT / CONFIGURATION LICENCE EFFECT**

Pinned OE-Core declares, for the same module family at 1.22.12:

    gstreamer1.0-plugins-ugly   LICENSE = "LGPL-2.1-or-later & GPL-2.0-or-later"
                                LICENSE_FLAGS = "commercial"
    gstreamer1.0-libav          LICENSE_FLAGS = "commercial"

Enabling those PACKAGECONFIGs links GPL components (x264, a52dec, mpeg2dec, libdvdread,
sidplay), so the resulting binary is GPL-affected even though the wrapper source is LGPL.
The `commercial` flag must be preserved — OE excludes these unless explicitly whitelisted.

Both layers are simultaneously true. Layer A governs source incorporation; Layer B governs
what a given PACKAGECONFIG selection produces.

### Retained corrected records

- **stratum** — dual MIT / Apache-2.0. Three licence files preserved:
  `LICENSE.md` (14ecc01e3adadf9652f355df43b4855f / 437462a699a2c34c46a0b566b06f041ea5f54652a10e73e8ac13e9c6becbd1d0),
  `LICENSE-APACHE` (86d3f3a95c324c9479bd8986968f4327 / c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4),
  `LICENSE-MIT` (abd40148cf3f5fc7a8052c45980fa081 / 638da3722c9e102ccd8011d82f61ae3b611174e4a0f8da185c582df137b60a8c)
- **sv2-apps** — dual MIT / Apache-2.0, identical three files and identical checksums.
- **sv2-spec** — REFERENCE-ONLY. Evidence under `License/`:
  `License/BSD-3-Clause` (bd3412dad92085eb3afc5bf9d701adf0 / c0d4dcb99e5b34c2816ec9dcc0abba0d475465458bd6cf1c9626dc31c8f2248c),
  `License/CC0-1.0` (65d3616852dbf7b1a6d4b53b00626032 / a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499)
- **MCP TypeScript SDK** — **UNRESOLVED**. Not acquired. No licence conclusion recorded.
  The MIT / Apache-2.0 transition and CC-BY-4.0 documentation treatment must be
  characterised from authoritative acquired material only.

md5 and sha256 serve different purposes and are not interchangeable: md5 satisfies
bitbake's `LIC_FILES_CHKSUM` drift detector; sha256 is the source-lock integrity record.

---

## 3. PROVIDER CLASSIFICATION (accepted)

All runtime sources: **NOT PROVIDED** by pinned OE-Core, except:
- **sv2-spec** — REFERENCE-ONLY
- **GStreamer** — provider EXISTS at 1.22.12 (13 recipes); 1.28.7 is a deliberate
  version-override decision, handled separately (section 8)

No Poky in this estate — OE-Core only.

---

## 4. RUST CLOSURE

Generated from each `Cargo.lock`. **NON-AUTHORITATIVE — regenerate on the reference machine.**

| Component | Lockfiles | Unique crates.io crates | git deps | path/local (workspace members, not fetched) | Unresolved |
|---|---|---|---|---|---|
| stratum | 1 (+1 `fuzz/`, excluded) | **160** | **0** | 17 | 0 |
| sv2-apps | **4** (stratum-apps, pool-apps, integration-tests, miner-apps) | **681** (deduplicated union) | **0** | 17 | 0 |
| librespot | 1 | **474** | **0** | 9 | 0 |

**The single most important result: ZERO git dependencies across all three.** Every
external dependency is a crates.io registry crate, which the pinned Scarthgap `crate://`
fetcher can represent directly. No separate git-repository acquisition identities are
needed for the Rust tier.

`cargo-update-recipe-crates.bbclass` is present in pinned OE-Core and is the correct
mechanism. Caveat: **sv2-apps has four independent workspaces**, each with its own lock.
The 681 figure is the deduplicated union; the class operates per-lockfile, so a
SyMoNeuRaL-side merge step is required, or four separate `.inc` files.

**Generated SRC_URI closure location:**

    <scratchpad>/closure/stratum-crates.inc      160 crate:// lines
    <scratchpad>/closure/sv2-apps-crates.inc     681 crate:// lines
    <scratchpad>/closure/librespot-crates.inc    474 crate:// lines

**Offline compile after fetch: PROBABLE for the crate tier, NOT YET PROVEN.** The crate
graph is fully enumerable, but this has not been demonstrated by an authoritative
`bitbake -c fetch` followed by a network-isolated compile. Do not treat enumeration as proof.

---

## 5. RUST TOOLCHAIN — DECISION OPTIONS (not chosen)

Pinned Scarthgap ships `rust_1.75.0` / `cargo_1.75.0`.

| Component | Declared requirement | Source of truth | Compatible? |
|---|---|---|---|
| stratum | `rust-toolchain.toml` channel = **1.75.0** | in-tree | **YES — exact match** |
| librespot | `rust-version = 1.85`, **edition 2024** | `Cargo.toml` | NO |
| sv2-apps | `rust-toolchain.toml` channel = **1.88.0** | in-tree | NO |

Edition 2024 is the harder constraint: it is not a warning, it is refused outright by
any compiler older than 1.85.

**Option A — pinned newer Rust recipes inside the accepted layer stack.**
Scope: author/port `rust`, `rust-llvm`, `cargo`, `rust-cross-*`, `libstd-rs` at the target
version. Trade-off: total control and no new layer, but Rust recipes are tightly coupled to
LLVM and to OE's cross-canadian machinery; this is a substantial and ongoing maintenance
burden, re-incurred at every Rust bump. Highest effort, lowest external dependency.

**Option B — pinned external OE layer supplying the required Rust.**
Scope: add one immutably-pinned layer to the accepted stack. Trade-off: far less work and
maintained upstream, but introduces a new provider into the layer stack, with attendant
provider-collision risk against OE-Core's own `rust`/`cargo`. Requires explicit acceptance
that the stack is no longer OE-Core-only. **Note this is the same decision as the Node
blocker (section 7)** — if a layer is admitted for nodejs, the Rust question may be
answerable by the same decision rather than a second one.

**Option C — select older upstream releases compatible with 1.75.0.**
Scope: re-pin librespot and sv2-apps to the newest releases that still build on 1.75.0.
Trade-off: zero toolchain work and keeps the stack pure, but contradicts the stated release
decisions (librespot v0.8.0, sv2-apps v0.7.0) and forfeits upstream fixes. Viable **only if**
functionality and release policy permit. Note stratum v1.11.1 needs no change under any option.

**Not proposed:** rustup or a host-installed compiler. Excluded per instruction.

---

## 6. PYTHON CLOSURE

Pinned OE-Core provides `python3_3.12.13`. All three components declare `requires-python
>= 3.10` — satisfied.

### Build backends (PEP 517)

| Component | `build-system.requires` | OE-Core | Classification |
|---|---|---|---|
| anthropic-sdk-python | `hatchling==1.26.3` | 1.21.1 | **VERSION OVERRIDE REQUIRED** (exact pin; not satisfiable by 1.21.1) |
| anthropic-sdk-python | `hatch-fancy-pypi-readme>=22.4,<26` | 24.1.0 | PROVIDED |
| mcp-python-sdk | `hatchling` (unpinned) | 1.21.1 | PROVIDED |
| mcp-python-sdk | `uv-dynamic-versioning` | — | **NOT PROVIDED** (plus its own closure, incl. `uv` — also NOT PROVIDED) |
| FreeToken | `setuptools>=77` | 69.1.1 | **VERSION OVERRIDE REQUIRED** |
| FreeToken | `wheel` | 0.42.0 | PROVIDED |
| FreeToken | `torch>=2.11,<2.12` | — | **ARCHITECTURE DECISION REQUIRED** |

### Runtime dependencies

| Dependency | OE-Core | SyMoNeuRaL-acquired | Classification |
|---|---|---|---|
| typing-extensions | 4.10.0 | — | PROVIDED |
| jsonschema | 4.21.1 | — | PROVIDED |
| pydantic | — | **Symoneural-API** v2.13.5 | NOT PROVIDED by OE; SyMoNeuRaL-supplied |
| starlette | — | **Symoneural-API** 1.6.0 | NOT PROVIDED by OE; SyMoNeuRaL-supplied |
| uvicorn | — | **Symoneural-API** 0.52.4 | NOT PROVIDED by OE; SyMoNeuRaL-supplied |
| **httpx2** | — | **NOT ACQUIRED** | **NOT PROVIDED — see finding below** |
| anyio, sniffio, jiter, docstring-parser | — | — | NOT PROVIDED |
| mcp-types, sse-starlette, pyjwt, typing-inspection, opentelemetry-api, python-multipart | — | — | NOT PROVIDED |

**FINDING — `httpx` vs `httpx2` mismatch.** Both anthropic-sdk-python and mcp-python-sdk
declare a runtime dependency on **`httpx2`**, not `httpx`. Symoneural-API acquired
**`httpx` 0.28.1** (`encode/httpx`). These are different distributions. The acquired httpx
does not satisfy either SDK, and `httpx2` has no acquisition identity in this estate.
This must be resolved before either SDK can be considered closed.

### FreeToken — ARCHITECTURE DECISION REQUIRED

`torch>=2.11,<2.12` is a **build-time** requirement: FreeToken compiles C++/CUDA extensions
that link libtorch, and its own comments state a mismatch links against the wrong libtorch.
Published manylinux/CUDA kernel-cache wheels are excluded as a source-authority substitute.

Symoneural-Common now holds **PyTorch v2.14.0** (`2b3ec348`, 65 submodules, clean). That is
**outside FreeToken's declared range** — it needs 2.11.x. Satisfying FreeToken therefore
means either building a second, older PyTorch, or moving Common's PyTorch pin backwards and
re-evaluating every other consumer. Either way this introduces a full framework/toolchain
stack (CUDA toolkit, cuDNN, libtorch build) and is a genuine architecture decision, not a
recipe choice. **Escalated, not resolved.**

---

## 7. NODE / TYPESCRIPT CLOSURE

Only **hls.js** is acquired; the other three failed acquisition on `nodejs-native` and
cannot be inventoried from authoritative material.

| Item | hls.js (acquired) | anthropic-sdk-typescript | MCP TypeScript SDK | workers-sdk / Wrangler |
|---|---|---|---|---|
| Package manager | npm | UNKNOWN — not acquired | UNKNOWN — not acquired | UNKNOWN — not acquired |
| Lockfile | `package-lock.json` v2 | — | — | — |
| Package count | **2144** | — | — | — |
| git dependencies | **0** | — | — | — |
| Non-registry resolved | **0** (all registry.npmjs.org) | — | — | — |
| Packages with install scripts | **5** | — | — | — |
| Platform-specific (`os` constraint) | **82** | — | — | — |

**The blocker is structural, not per-package.** `npm.bbclass` exists in pinned OE-Core, but
line 22 reads:

    DEPENDS:prepend = "nodejs-native nodejs-oe-cache-native "

and line 31 comments *"must match mapping in nodejs.bb (openembedded-meta)"*. OE-Core ships
**no nodejs recipe**. So the class is present but inert: recipe generation via
`recipetool create` fails at dependency resolution, and any generated recipe could not build.

Verified failure, reproduced on three repositories:

    ERROR: Nothing provides 'nodejs-native' which is required for the build
    NOTE: You will likely need to add a layer that provides nodejs

hls.js is a partial exception: recipetool never routed it through the npm handler and
emitted a generic empty-stub recipe. The source is correctly pinned, but **no dependency
closure was generated**, so its 2144 packages remain unrepresented.

**Alternatives (not chosen):**
- **N-A. Admit a pinned external layer providing nodejs.** Same decision as Rust Option B;
  one layer may answer both. Introduces a provider outside OE-Core.
- **N-B. SyMoNeuRaL-authored nodejs-native recipe** inside the accepted stack. No new layer,
  but nodejs is a large C++/V8 build and a significant standing maintenance burden.
- **N-C. Treat the TypeScript SDKs as REFERENCE-ONLY** and consume Node artifacts through a
  different mechanism entirely. Avoids the problem; changes the product architecture.

`npm install` / `pnpm install` during `do_compile` is **not** proposed under any option.

---

## 8. GSTREAMER 1.28.7 DELTA

Pinned OE-Core ships **13 gstreamer recipes, all at 1.22.12**. Decision is **1.28.7** —
three stable generations ahead (1.22 → 1.24 → 1.26 → 1.28).

### Can the core alone be upgraded? NO.

`subprojects/gst-plugins-good/meson.build` in 1.28.7 declares:

    gst_req = '>= @0@.@1@.0'.format(gst_version_major, gst_version_minor)

Each module requires a core matching **its own major.minor**. OE-Core reinforces this —
every module recipe `DEPENDS` on `gstreamer1.0-plugins-base`, which itself tracks the core.

**Upgrading only the core recipe is unsafe and effectively impossible.** A 1.28.7 core
beside 1.22.12 modules fails the `gst_req` check; 1.28.7 modules against a 1.22.12 core fail
identically. The stack must move as one unit.

### Module inventory — all must move together

| Module | Pinned OE-Core | Target | Present in acquired 1.28.7 monorepo |
|---|---|---|---|
| gstreamer (core) | 1.22.12 | 1.28.7 | yes |
| gst-plugins-base | 1.22.12 | 1.28.7 | yes |
| gst-plugins-good | 1.22.12 | 1.28.7 | yes |
| gst-plugins-bad | 1.22.12 | 1.28.7 | yes |
| gst-plugins-ugly | 1.22.12 | 1.28.7 | yes (LICENSE_FLAGS commercial — preserve) |
| gst-libav | 1.22.12 | 1.28.7 | yes (LICENSE_FLAGS commercial — preserve) |
| gst-devtools | 1.22.12 | 1.28.7 | yes |
| gst-rtsp-server | 1.22.12 | 1.28.7 | yes |
| gstreamer1.0-python | 1.22.12 | 1.28.7 | yes (`gst-python`) — required only if SyMoNeuRaL-Live needs bindings; **undecided** |
| gstreamer1.0-omx | 1.22.12 | — | not in monorepo; separate upstream |
| gstreamer1.0-vaapi | 1.22.12 | — | **superseded** — VA-API moved into gst-plugins-bad after 1.22 |
| gst-examples | 1.18.6 | — | already version-skewed in OE-Core |

Structural change: 1.28.7 is a **monorepo** with all modules under `subprojects/`, whereas
OE-Core packages them as separate recipes from separate tarballs. The override must decide
whether to keep OE-Core's per-module recipe split or collapse to one — that is an
architecture choice, flagged, not made.

### Dependency/toolchain changes caused by the generation move

| Requirement | 1.28.7 needs | Pinned OE-Core provides | Verdict |
|---|---|---|---|
| **meson** | **>= 1.4** | **meson_1.3.1** | **BLOCKER — version override required** |
| glib-2.0 | >= 2.64.0 | 2.78.6 | satisfied |
| ffmpeg (for gst-libav) | generation-matched | ffmpeg_6.1.4 | unverified — libav is tightly coupled to ffmpeg major |

**The meson floor is a hard blocker.** GStreamer 1.28.7 cannot configure under the pinned
stack's meson 1.3.1. Any 1.28.7 override silently requires a meson override first — which
would change a build tool used by **many** other OE-Core recipes, well beyond GStreamer's
stated scope. That is precisely the "override would silently replace OE-Core packages beyond
its stated scope" stop condition.

**No 1.28.7 override drafted.** LOCK-PENDING, as instructed.

---

## 9. REMAINING BLOCKERS

| # | Blocker | Class | Stop condition |
|---|---|---|---|
| 1 | workerd acquired at `909e388c` (v1.20260912.1); decision is `925464ba` (v1.20260911.1) | SRCREV mismatch | tag/SRCREV mismatch |
| 2 | nodejs absent from OE-Core — blocks anthropic-ts, MCP-ts, workers-sdk; leaves hls.js's 2144 packages unrepresented | toolchain/provider | toolchain not representable |
| 3 | Rust 1.85 / edition 2024 (librespot) and 1.88.0 (sv2-apps) vs Scarthgap 1.75.0 | toolchain | toolchain not representable |
| 4 | `uv-dynamic-versioning` + `uv` NOT PROVIDED | Python closure | dependency without acquisition identity |
| 5 | `hatchling==1.26.3` exact vs OE-Core 1.21.1 | Python version override | dependency not locked |
| 6 | **`httpx2`** required by both Anthropic and MCP Python SDKs; not acquired; `httpx` 0.28.1 is a different distribution | Python closure | dependency without acquisition identity |
| 7 | FreeToken needs torch 2.11.x; Common holds **2.14.0** — outside range | **architecture** | architectural choice, not recipe choice |
| 8 | GStreamer 1.28.7 needs meson >= 1.4; pinned stack has 1.3.1 | toolchain override | override exceeds stated scope |
| 9 | ~20 Python runtime deps NOT PROVIDED (anyio, sniffio, jiter, mcp-types, sse-starlette, pyjwt, opentelemetry-api, …), each with its own recursive closure | Python closure | dependency not locked |
| 10 | MCP TypeScript SDK licence UNRESOLVED — not acquired | licence | licence not characterisable |
| 11 | Offline-compile-after-fetch unproven for every component — enumeration is not proof | verification | build-time network unproven |

### Defects found in recipetool-generated metadata (repaired, mechanical only)

- **symoneural-pytorch** — emitted `inherit distutils3`; that class was **removed** in
  scarthgap. Recipe failed to parse and was quarantined as `.parsefailed`. Repaired to
  `setuptools3`; bbappend authored manually. Source was fetched correctly and is untouched.
- **symoneural-vllm** — emitted PyPI extras syntax (`python3-runai-model-streamer[s3,gcs,azure]`)
  into `PACKAGECONFIG` values. `PACKAGECONFIG` fields are comma-separated, so the bracketed
  commas corrupted the 4-field format: *"Invalid conflict package config 'azure]'"*. This
  single malformed recipe **poisoned the entire workspace parse**, causing every subsequent
  devtool operation in Symoneural-LLM to fail — which initially presented as an unrelated
  triton fetch failure. Repaired by reducing to base package names (OE has no extras concept).

Both are DRAFT, NON-AUTHORITATIVE repairs of invalid generated metadata. Neither touched
upstream source.

---

## 10. COMPONENTS CLEARED FOR RECIPE DRAFTING

**Cleared: NONE — with one near-miss.**

| Component | Closure state | Cleared? |
|---|---|---|
| **stratum** | 160 crates enumerated, 0 git deps, toolchain matches 1.75.0 exactly | **NEAREST — blocked only by item 11** (offline compile unproven on the reference machine) |
| sv2-spec | REFERENCE-ONLY; no build step consumes it | N/A — no recipe by decision |
| librespot | crates enumerated, but toolchain incompatible | NO — blocker 3 |
| sv2-apps | crates enumerated, but toolchain incompatible | NO — blocker 3 |
| anthropic-sdk-python | NO — blockers 5, 6, 9 | NO |
| mcp-python-sdk | NO — blockers 4, 6, 9 | NO |
| FreeToken | NO — blocker 7 (architecture) | NO |
| hls.js | NO — blocker 2 | NO |
| anthropic-sdk-typescript, MCP-ts, workers-sdk | not acquired | NO — blocker 2 |
| workerd | wrong revision on disk | NO — blocker 1 |
| GStreamer 1.28.7 | NO — blocker 8, plus lockstep module decision | NO — LOCK-PENDING |

**stratum is the only component whose dependency closure is fully resolved**: complete crate
enumeration, zero git dependencies, and an exact toolchain match against the pinned stack.
It is the correct first candidate — but clearing it requires an authoritative
`bitbake -c fetch` followed by a network-isolated compile on the reference machine. Closure
resolution is not proof of offline buildability, and this report does not promote it.

### Decisions required before further progress

1. **One layer decision may unblock two tiers.** Blockers 2 (nodejs) and 3 (Rust) are both
   "admit a pinned external layer, or author the recipes in-stack, or re-pin upstream older."
   They should be decided together, not separately.
2. **FreeToken/PyTorch (blocker 7)** needs an architecture decision on torch 2.11.x vs the
   acquired 2.14.0 before any implementation.
3. **GStreamer (blocker 8)** — a meson override affecting the whole stack must be
   authorised explicitly, or 1.28.7 abandoned in favour of the 1.22.12 provider.
4. **workerd (blocker 1)** — re-acquire at `925464ba` through the accepted path.
