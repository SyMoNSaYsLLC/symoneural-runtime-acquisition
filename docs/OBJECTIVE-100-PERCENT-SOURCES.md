# PRIMARY OBJECTIVE — read this before doing anything

> **Build 100% of the estate's sources, all `symoneural-` prefixed, from pristine
> upstream. Nothing else.**

Everything below is scope. **Nothing in this file may be removed** — only added to.

## The failure this file exists to stop

I drift. Repeatedly, in one session: asked to build sources, I produced reports,
scoped adjacent features, analysed records, and wrote commentary about the work
instead of doing it. Garrett has had to redirect me to the same objective more
than once.

**The rule for me:** if a turn produces no build, no fix, and no acquisition, it
was probably drift. Reports are output of work, never a substitute for it.

## Definition of done

Every source in `acquisition/source-manifest.json` is either:

1. a `symoneural-*` recipe in `meta-symoneural`, pinned to an upstream SHA,
   pristine, **and built with its artifact on disk**; or
2. a recorded decision saying why not (DEFERRED / REFERENCE-ONLY / a layer).

**Declared is not done. Built is done.** R16.

## Live status — update after each build, never from memory

| | |
|---|---|
| Components (census) | 41 · 38 verified · 3 without a recipe |
| RavenCalc built | **5 of 6** — sympy, mpmath, numpy, openblas, scipy · scikit-learn NOT attempted |
| Other runtimes | **33 recipes never attempted** |
| Acquired today | `symoneural-cython` 3.2.9, `symoneural-pybind11` 3.0.4 |

## Order of work

1. scipy verified against estate-owned cython/pybind11
2. **scikit-learn** → RavenCalc 6/6
3. Sweep every other runtime — `tools/build-all`
4. Group B acquisitions: packaging, psutil, pyyaml, pyparsing, setuptools
5. Decisions for Garrett only — do not decide these alone

---

# SyMoNeuRaL Runtime Acquisition

> **GENERATED FILE — do not edit.** Rendered by `tools/generate-runtime-acquisition.py`
> from `acquisition/*.json`. Every number below is derived from those records and
> re-asserted against them at render time. To change this report, change the records.

| | |
|---|---|
| Parent HEAD | `c172a413ec79276f3129ac5e2fc7ab5465bed4c0` |
| Working tree | modified, uncommitted |
| Records | `acquisition/` (14 JSON + SHA256SUMS) |
| Scanner identity | `acquisition/control-plane.json` (8 tools hashed) |
| Determinism verified | YES |
| Tree inventory | `generated/runtime-tree.txt` (28644 dirs) |
| Tree SHA-256 | `f7bf4c57aef868e7360881e3f2d3051560ab86e143ae8ba55e87bf5dc488a7ae` |
| Report self-validation | PASS (10/10 totals re-derived) |

## Verdicts

Two verdicts are tracked separately. The control plane must be trustworthy
before its description of the estate means anything.

| Verdict | Result | Meaning |
|---|---|---|
| **CONTROL-PLANE** | see `tools/verify-acquisition.py` | Can the scanner be trusted to describe the estate? |
| **ACQUISITION-STATE** | **FAIL** | Has the estate resolved its acquisition decisions? |

Acquisition FAIL reasons:

- 41 provider collision(s) unresolved (15 direct-vs-OE-Core)
- 366 vendored decision(s) unresolved
- 429 licence file(s) without an established identifier
- 9 explicit control-plane decisions open

This FAIL is expected and is a statement of open decisions, not a defect.


## Repository census

| Method | Count |
|---|---|
| A — filesystem candidate + `git rev-parse` validation | 41 |
| B — independent git work-tree-top census | 41 |
| **Sets identical** | **YES** |

`.git` is accepted as a file or a directory; submodules are excluded from the
top-level set via `--show-superproject-working-tree`, which is representation-independent.


## Build-stack identity

| Component | SHA |
|---|---|
| bitbake | `046a90b0e9b7b914b7a95aec579cdc3fc9c7617a` |
| meta-openembedded | `43b79d8e372c4f69ebab6c85b39d97b41522080f` |
| openembedded-core | `fe7a24bc67118e7e184b5f5247258715e3904e7c` |

This locks the **build stack only**, never the application sources.


## Runtime inventory

| Runtime | Components | Verified | Clean |
|---|---|---|---|
| API | 6 | 6 | 6 |
| Adaptive-Fabric | 1 | 1 | 1 |
| Build | 7 | 7 | 7 |
| CLI | 4 | 2 | 4 |
| Common | 6 | 6 | 6 |
| Crypto | 3 | 3 | 3 |
| LLM | 3 | 3 | 3 |
| Live | 1 | 1 | 1 |
| Ravencalc | 6 | 6 | 6 |
| Remix | 1 | 1 | 1 |
| Streamer | 1 | 1 | 1 |
| Web | 2 | 1 | 2 |
| **TOTAL** | **41** | **38** | **41** |

## Top-level source lock

| Runtime | Component | Commit | State | Subs | Recipe |
|---|---|---|---|---|---|
| API | httpcore | `98209758cc14` | VERIFIED | 0 | yes |
| API | httpx | `26d48e0634e6` | VERIFIED | 0 | yes |
| API | pydantic | `001dea020e08` | VERIFIED | 0 | yes |
| API | fastapi | `95f8322ee1dc` | VERIFIED | 0 | yes |
| API | starlette | `4f250d6b8145` | VERIFIED | 0 | yes |
| API | uvicorn | `8988c23704fc` | VERIFIED | 0 | yes |
| Adaptive-Fabric | FreeToken | `9db1a39455a3` | VERIFIED | 0 | yes |
| Build | autoconf | `44d712a26b0e` | VERIFIED | 0 | yes |
| Build | automake | `e82d2d34d462` | VERIFIED | 0 | yes |
| Build | libtool | `309bb53a8adf` | VERIFIED | 2 | yes |
| Build | m4 | `fe2f13ab9ab9` | VERIFIED | 2 | yes |
| Build | bitbake | `046a90b0e9b7` | VERIFIED | 0 | yes |
| Build | openembedded-core | `fe7a24bc6711` | VERIFIED | 0 | yes |
| Build | ninja | `3441b633c2fe` | VERIFIED | 0 | yes |
| CLI | anthropic-sdk-python | `eb21a4352015` | VERIFIED | 0 | yes |
| CLI | anthropic-sdk-typescript | `135f71e92976` | UNRESOLVED | 0 | **none** |
| CLI | python-sdk | `9972c21aa420` | VERIFIED | 0 | yes |
| CLI | typescript-sdk | `cc4b41617ce3` | UNRESOLVED | 0 | **none** |
| Common | accelerate | `6afc1e5ee217` | VERIFIED | 0 | yes |
| Common | huggingface-hub | `495b17c85296` | VERIFIED | 0 | yes |
| Common | pytorch | `2b3ec3482903` | VERIFIED | 65 | yes |
| Common | safetensors | `a406ca3e7a90` | VERIFIED | 0 | yes |
| Common | tokenizers | `88a4498ad4ea` | VERIFIED | 0 | yes |
| Common | transformers | `856157a2f3e9` | VERIFIED | 0 | yes |
| Crypto | stratum | `c1a799139425` | VERIFIED | 0 | yes |
| Crypto | sv2-apps | `d7d556d1a3c7` | VERIFIED | 0 | yes |
| Crypto | sv2-spec | `67d2178e12b2` | VERIFIED | 0 | yes |
| LLM | llama.cpp | `5266f24da75d` | VERIFIED | 0 | yes |
| LLM | triton | `c01b6774b186` | VERIFIED | 0 | yes |
| LLM | vllm | `98dff2a81d74` | VERIFIED | 0 | yes |
| Live | gstreamer | `070125524a84` | VERIFIED | 1 | yes |
| Ravencalc | openblas | `e0166008be8e` | VERIFIED | 0 | yes |
| Ravencalc | scikit-learn | `866c0f51e756` | VERIFIED | 0 | yes |
| Ravencalc | numpy | `dd88c0c19b54` | VERIFIED | 7 | yes |
| Ravencalc | scipy | `e4e854eaa8f1` | VERIFIED | 8 | yes |
| Ravencalc | mpmath | `c1131e2d64ab` | VERIFIED | 0 | yes |
| Ravencalc | sympy | `16fa855354eb` | VERIFIED | 0 | yes |
| Remix | librespot | `d36f9f1907e8` | VERIFIED | 0 | yes |
| Streamer | hls.js | `e5ff3583965e` | VERIFIED | 0 | yes |
| Web | workerd | `925464ba9fe5` | VERIFIED | 0 | yes |
| Web | workers-sdk | `00ae21fa8375` | UNRESOLVED | 0 | **none** |

## Submodule summary

Entries: **85** · identity key `owner_source_path + submodule_path` · unknown URLs: **0**

- AT-RECORDED-COMMIT: 85

## Dependency graph

Declarations discovered from on-disk manifests: **12825**. No depth limit; nothing fetched.

| Classification | Count |
|---|---|
| PACKAGE-MANAGED | 8692 |
| DIRECT-DECLARED | 3722 |
| BUILD-FETCH | 227 |
| WORKSPACE-LOCAL | 99 |
| SUBMODULE | 85 |

| Scope | Count |
|---|---|
| DEV-ONLY | 6160 |
| UNKNOWN | 5188 |
| RUNTIME/SHIP | 1267 |
| BUILD-ONLY | 188 |
| TEST-ONLY | 19 |
| DOC-ONLY | 3 |

A lockfile establishes resolution, not directness: a `Cargo.lock` entry with no
source URL is `WORKSPACE-LOCAL`, never `DIRECT-DECLARED`.


## Vendored register

Entries **369** across **223** logical packages; **41** appear in more than one place.

| Scope | Count |
|---|---|
| UNKNOWN | 338 |
| TEST-ONLY | 21 |
| PRIVATE-VENDORED | 9 |
| DOC-ONLY | 1 |

| Most-duplicated | Copies |
|---|---|
| sub | 23 |
| cmmod | 15 |
| foo | 14 |
| nlohmann | 11 |
| gtest | 10 |
| a | 9 |
| b | 8 |
| sub2 | 7 |

All decisions are `UNRESOLVED`. A test-only vendored library must not be pushed
through the same release path as a runtime-linked one — hence the scope column.


## Provider graph

OE-Core recipes inspected **%d**, providers indexed **%d**, collisions **%d**

| | |
|---|---|
| OE-Core recipes inspected | 2760 |
| Providers indexed | 2823 |
| Collisions | 48 |
| Direct-acquisition vs OE-Core | **15** |

| Logical dependency | Direct | OE-Core recipe |
|---|---|---|
| gstreamer | Live/gstreamer | gstreamer1.0 1.28.7 |
| ninja | Build/ninja | ninja 1.13.2 |
| autoconf | Build/autoconf | autoconf 2.73 |
| automake | Build/automake | automake 1.19 |
| fastapi | API/fastapi | python3-fastapi 0.141.1 |
| httpcore | API/httpcore | python3-httpcore 1.0.9 |
| httpx | API/httpx | python3-httpx 0.28.1 |
| libtool | Build/libtool | libtool 2.6.2 |
| m4 | Build/m4 | m4 1.4.21 |
| mpmath | Ravencalc/mpmath | python3-mpmath 1.4.1 |
| numpy | Ravencalc/numpy | python3-numpy 2.5.3 |
| pydantic | API/pydantic | python3-pydantic 2.13.4 |
| starlette | API/starlette | python3-starlette 1.6.0 |
| sympy | Ravencalc/sympy | python3-sympy 1.14.0 |
| uvicorn | API/uvicorn | python3-uvicorn 0.49.0 |

Provider **existence** is recorded; `selected_provider` stays `UNRESOLVED`.
The scanner exposes choices and does not make architecture decisions.


## Source collisions

Provider kinds indexed: DIRECT-ACQUISITION, OE-CORE-RECIPE, SUBMODULE, VENDORED

| | |
|---|---|
| Logical sources indexed | 314 |
| With more than one provider | **88** |
| INTRA-COMPONENT-DUPLICATE | 77 |
| CROSS-COMPONENT-DUPLICATE | 7 |
| CROSS-RUNTIME-DUPLICATE | 4 |
| DIRECT-VERSUS-OE-CORE | 14 |
| Vendor entries reclassified as SUBMODULE | 64 |
| Duplicate top-level upstream URLs | 0 (invariant) |

| Cross-runtime source | Runtimes | Copies | Kinds |
|---|---|---|---|
| nlohmann | Common, LLM | 12 | SUBMODULE, VENDORED |
| cpp-httplib | Common, LLM | 3 | SUBMODULE, VENDORED |
| packaging | Common, Ravencalc | 3 | OE-CORE-RECIPE, VENDORED |
| pocketfft | Common, Ravencalc | 2 | SUBMODULE |

A git submodule is a real source copy with its own upstream identity, so
`SUBMODULE` is indexed as a provider kind alongside the others. **Detection only** —
no copy is collapsed, deleted or rewritten; every entry is `UNRESOLVED`.


## Licence inventory

Licence-bearing files: **430**

- NESTED/DEPENDENCY: 378
- TOP-LEVEL: 52

**LICENSE expression and LIC_FILES_CHKSUM coverage are separate concepts.**
This inventory is drift evidence, not a licensing conclusion.


## Artifact capabilities

What each source **natively declares**. No SyMoNeuRaL decision is recorded.

| Capability | Components |
|---|---|
| PYTHON-PACKAGE | 27 |
| PYTHON-EXTENSION | 13 |
| EXECUTABLE | 13 |
| NODE-BUNDLE | 12 |
| RUST-RLIB | 11 |
| RUST-CDYLIB | 7 |
| SHARED-LIBRARY | 6 |
| UNKNOWN | 5 |
| STATIC-LIBRARY|SHARED-LIBRARY | 5 |

## Unresolved decisions

| Category | Identifier | Blocks |
|---|---|---|
| ACQUISITION | mcp-typescript-sdk | Symoneural-CLI source lock |
| ACQUISITION | symoneural-workerd | Symoneural-Web source lock |
| ARCHITECTURE | FreeToken/torch | Adaptive-Fabric build design |
| BUILD-DESIGN | pydantic-core-ownership | Symoneural-API release posture |
| BUILD-DESIGN | scipy-fortran | Ravencalc scipy and scikit-learn (transitively) |
| LICENCE | symoneural-openblas | release licensing claim |
| PROVENANCE | all recipes | audit of SyMoNeuRaL modifications |
| PROVIDER | direct-vs-oe-core | build design for Build, Ravencalc and Live |
| PROVIDER | nodejs | Node/TypeScript acquisition |

- artifact decisions pending: **41**
- licence files unresolved: **429**
- provider collisions unresolved: **30**
- source collision decisions unresolved: **73**
- vendor entries reclassified as submodule: **64**
- vendored decisions unresolved: **366**

## Exceptions

| ID | Component | Result | Classification |
|---|---|---|---|
| EXC-001 | symoneural-openblas | SUCCESS rc=0, 984 tasks, 0 errors | EXPLORATORY, OUTSIDE ACQUISITION GATE |
| EXC-002 | symoneural-openblas | SUCCESS rc=0, 773 tasks after adding cross-compile options | EXPLORATORY, OUTSIDE ACQUISITION GATE |

Recorded as history. Neither build is authoritative for release.


## Generated to-do tasks

1. **[ACQUISITION] mcp-typescript-sdk** — Not acquired. Release decision specifies v2 GA 2.0.0 at cc4b41617ce3601b1290d67216ea0b194a3cd9ac; tag-to-commit unverified and mixed MIT / Apache-2.0 / CC-BY-4.0 treatment uncharacterised.

2. **[ACQUISITION] symoneural-workerd** — On disk at 909e388c (v1.20260912.1); release decision specifies 925464ba (v1.20260911.1) paired with Wrangler 4.131.1.

3. **[ARCHITECTURE] FreeToken/torch** — FreeToken requires torch>=2.11,<2.12; Common holds PyTorch 2.14.0, outside that range.

4. **[BUILD-DESIGN] pydantic-core-ownership** — pydantic requires pydantic-core (Rust/maturin). meta-python supplies python3-pydantic-core 2.46.4 and it is BORROWED tonight so the API stack can build. But D2's rule is 'own what you ship, borrow what you only build with', and pydantic-core is linked into the shipped runtime, not merely used to build it. Under D2 it should be SyMoNeuRaL-owned, which means acquiring it as a source component. Recorded, not decided.

5. **[BUILD-DESIGN] scipy-fortran** — scipy requires a Fortran compiler. The OE cross toolchain is built LANGUAGES="c,c++" with FORTRAN="", so x86_64-oe-linux-gfortran does not exist. Evidence: scipy meson.build:91 'Unknown compiler(s): x86_64-oe-linux-gfortran', log tmp/work/x86-64-v3-oe-linux/symoneural-scipy/1.18.1/temp/log.do_compile.2878019. TOOLCHAIN decision, not a recipe fix: either rebuild gcc-cross with fortran enabled (FORTRAN:forcevariable = ",fortran"), or accept scipy/scikit-learn as unbuildable on this toolchain. Not resolvable by guessing.

6. **[LICENCE] symoneural-openblas** — 8 licence-bearing files (OpenBLAS BSD-3, GotoBLAS, LAPACK modified-BSD, LAPACKE, ReLAPACK, netlib BLAS reference whose grant is non-OSI 'requests proper credit'). Recipe LICENSE expression is still the single token BSD-3-Clause. Retained UNRESOLVED.

7. **[PROVENANCE] all recipes** — RAW-GENERATED-BASELINE NOT PRESERVED. recipetool output was edited in place. Historical absence is not reconstructable and is not fabricated. STANDING REQUIREMENT: before editing any newly generated recipe, preserve its raw generated form or deterministic hash in acquisition evidence first.

8. **[PROVIDER] direct-vs-oe-core** — The master re-baseline made 7 directly-acquired components duplicate an OE-Core recipe at the SAME version: gstreamer(1.28.7), autoconf(2.73), automake(1.19), libtool(2.6.2), m4(1.4.21), ninja(1.13.2), numpy(2.5.3). Each needs a provider selection. Provider graph now indexes SUBMODULE as a provider kind; the cross-runtime map is acquisition/source-collisions.json.

9. **[PROVIDER] nodejs** — No nodejs provider in OE-Core at the locked SHA; npm.bbclass DEPENDS on nodejs-native and cites openembedded-meta.




# Getting to 100% `symoneural-` sources

Status as of **2026-09-13**, read from disk. 41 recipes in `meta-symoneural`.

---

## The rule, stated once

**Own what you ship. Borrow what you only build with.**

"100%" does **not** mean zero borrowed recipes. It means **every borrowed recipe
is a deliberate, recorded decision** rather than an accident. A `.pyc` that ends
up on a customer's disk must come from a source we pinned. A tool that only runs
on this build host does not.

The failure this prevents is **D2, the provider collision**: the estate builds
`symoneural-numpy`, and a sibling recipe quietly depends on OE-Core's
`python3-numpy`. Two copies of the same library, only one pinned by us, and the
package feed resolving whichever it saw first.

---

## Status: three groups

### GROUP A — borrowed, but the estate already owned it. **FIXED TODAY.**

These were live collisions. Every one is now pointed at the estate's own recipe.

| Was | Now | Recipes affected |
|---|---|---|
| `python3-torch` | `symoneural-pytorch` | accelerate |
| `python3-numpy` | `symoneural-numpy` | accelerate |
| `python3-safetensors` | `symoneural-safetensors` | accelerate |
| `python3-huggingface_hub` | `symoneural-huggingface-hub` | accelerate |
| `python3-cython-native` | `symoneural-cython-native` | numpy, scipy, scikit-learn |
| `python3-pybind11`, `-native` | `symoneural-pybind11`, `-native` | scipy |
| `python3-ninja-native` | `symoneural-ninja-native` | pybind11 |

**`symoneural-cython` and `symoneural-pybind11` were acquired today** to make the
last four possible:

```
cython    3.2.9   58b8e6adc51c99c8cd5dd75db720e4aa7c051cb6   106M   clean, HEAD == pin
pybind11  v3.0.4  d03662f0984f652b60e7ddce53d3868002275197    19M   clean, HEAD == pin
```

Both mirror OE's own recipe — same upstream, same version, same build classes —
repointed at our pinned tree. **Licence checksums match OE's byte for byte**, so
these are provably the same sources, not lookalikes.

Cython mattered most: scipy's extension modules are *generated* by it, so
borrowing meant shipping C emitted by a compiler the estate never pinned. That is
the collision one level further back than usual, because it is a code generator
rather than a library.

### GROUP B — borrowed, ships to customers, **SHOULD be owned**

These end up on a customer's disk. Each needs acquisition.

| Dependency | Used by | Note |
|---|---|---|
| `python3-packaging` | accelerate | pure python, small |
| `python3-psutil` | accelerate | C extension |
| `python3-pyyaml` | accelerate | C extension (libyaml) |
| `python3-pyparsing` | cython | pure python |
| `python3-setuptools` | cython | large surface |

**Five acquisitions.** None is difficult; all are the same pattern used for
cython and pybind11 today.

### GROUP C — borrowed **by rule, correctly**. No action.

**Build-only, never shipped** — "borrow what you only build with":
`bison-native`, `flex-native`, `python3-cmake-native`, `python3-hatchling-native`,
`python3-setuptools-scm-native`, `python3-pdm-backend-native`,
`python3-hatch-fancy-pypi-readme-native`, `python3-dunamai-native`,
`python3-tomlkit-native`, `python3-jinja2-native`,
`python3-uv-dynamic-versioning-native`.

These are PEP 517 backends and build tools. They run on this host and vanish.

**Parts of CPython itself**: `python3`, `python3-core`, `python3-misc`,
`python3-shell`, `python3-xml`, `python3-pkgutil`, `python3-netserver`.

OE splits one CPython into many packages. Owning these means acquiring and
maintaining **CPython**, which is a genuine decision with real cost, not a
tidy-up. **Recorded as a decision for Garrett, not assumed either way.**

**Cross-toolchain**: `libgfortran` — produced by the OE toolchain the estate
already uses. Owning it means owning GCC.

**Deferred by existing decision**: `nodejs` — *"target nodejs ships nowhere."*

---

## The workflow — how a source becomes `symoneural-*`

Repeatable, and it is exactly what was done twice today.

**1. Resolve the pin. Never a tag alone.**
```sh
git ls-remote https://github.com/<org>/<repo> 'refs/tags/<tag>^{}'
```
Tags move; a dereferenced SHA does not. Verify branch containment — release tags
frequently do not live on the default branch (m4, mpmath, numpy, scipy and
scikit-learn have all caught this).

**2. Acquire into the estate tree, read-only thereafter.**
```sh
git clone <url> Symoneural-<Runtime>/src/<category>/source/<name>
git -C <tree> checkout <SHA>
```
Verify three things, every time:
`git rev-parse HEAD` equals the pin · `git status --short` empty ·
`git submodule status --recursive` shows no `-` (hollow) or `+` (drifted).

**3. Checksum the licence from OUR tree, not from upstream's README.**
```sh
md5sum <tree>/LICENSE
```

**4. Write the recipe by MIRRORING the existing OE one — do not redesign.**
Same `LICENSE`, same `LIC_FILES_CHKSUM`, same `inherit`, same `EXTRA_OE*`.
Change only `SYMON_TREE`, `SRC_URI`, `SRCREV`, `PV`, and the `symoneural-` name.

**5. Switch consumers in the same change.** An owned recipe nobody uses is a
phantom completion — build it and immediately start using it.

**6. Build and verify the artifact exists.** `BUILD_RC` captured directly, never
through a pipeline. Then `find ... -name '*.ipk'`.

---

## What is NOT done

**RavenCalc is 5 of 6 built.** sympy, mpmath, numpy, openblas and **scipy** have
produced packages. **scikit-learn has not been attempted.**

scipy took five failures to land today, each fixed at its cause rather than
silenced:

| Failure | Cause |
|---|---|
| `meson.build:207` f2py | empty `PYTHONPATH` entry = cwd; scipy's `signal/` shadowed **stdlib** `signal` |
| `meson.build:296` | OpenBLAS built in the estate, absent from scipy's DEPENDS |
| `_duccfft` poison-dirs | pybind11 resolved via native config-tool, leaked an unprefixed target path |
| `__config__.py` | scipy embeds build provenance; sanitised, QA left armed |
| Cython `.c` | Cython writes the `.pyx` path into generated C |

A rebuild is running now to prove scipy still builds against the estate's **own**
cython and pybind11 rather than OE's.

---

## Order of work to 100%

1. **Verify scipy against estate-owned cython/pybind11** — running.
2. **scikit-learn** → RavenCalc 6 of 6, closes the Phase 11 build gate.
3. **Sweep every other runtime** (`tools/build-all`): API, CLI, Crypto, LLM,
   Remix, Streamer, Web, Adaptive-Fabric — 33 recipes never yet attempted.
4. **Group B: five acquisitions** — packaging, psutil, pyyaml, pyparsing,
   setuptools.
5. **Decide CPython** — the one item that needs your call, not mine.

Steps 1–3 are the real content. Step 4 is mechanical. Step 5 is a decision.
