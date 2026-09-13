
symonjump
#VENDORED DEPENDENCY COLLISION REGISTER#

**Living section. Regenerate before adding ANY new upstream source.**
Tools: `vendor-scan.py` (vendor/ third_party/ subprojects/) and `vendor-scan2.py`
(the harder case: third-party code vendored into ORDINARY directories).

## Why this gates compilation

A vendored copy is a second, invisible instance of a dependency. It creates four
concrete problems, and all four are cheaper to fix before a first build than after:

1. **Provider collision** — adding the upstream component creates two copies with
   different versions in one build.
2. **Split CVE tracking** — a CVE against upstream will not match a vendored copy,
   so scanners report clean while the vulnerable code ships.
3. **Undeclared licences** — vendored trees frequently ship with no licence file of
   their own, so they are invisible to licence scanning.
4. **Symbol clash at link time** — two copies of the same C/C++ library in one
   address space is undefined behaviour at best.

## WORKED EXAMPLE — ply (the case that prompted this register)

    BitBake 2.8 (our pin)  vendors  lib/ply           version 3.3
    BitBake master         adds     vendor/licenses/ply
    Upstream ply current                              version 3.11

Three facts follow:

- Our pinned BitBake carries **ply 3.3**, roughly a decade behind upstream 3.11.
- Our pin has **no `vendor/` directory at all** — the vendored licence is not declared.
  Upstream BitBake added `vendor/licenses/ply` precisely because this was a gap.
- Therefore adding upstream `ply` as a SyMoNeuRaL component **without** resolving
  BitBake's vendored copy produces two divergent plys in one estate.

This is an independent argument for the master re-baseline: master has materially
better vendored-dependency hygiene than scarthgap.

## SCAN RESULT A — vendored into ordinary directories (the dangerous pattern)

| Package | Version | Runtime | Location |
|---|---|---|---|
| **ply** | **3.3** | Build | `bitbake/source/lib/ply` |
| **bs4** | **4.4.1** | Build | `bitbake/source/lib/bs4` |
| progressbar | 2.3 | Build | `bitbake/source/lib/progressbar` |
| simplediff | 1.0 | Build | `bitbake/source/lib/simplediff` |
| packaging | 23.2 | Common | `pytorch/torch/_vendor/packaging` |
| stb | — | LLM | `llama.cpp/vendor/stb` |
| xxhash | — | LLM | `llama.cpp/vendor/hash/xxhash` |
| spdlog | — | Common | `pytorch/.../mkl-dnn/third_party/spdlog` |

## SCAN RESULT B — duplicate counts (de-duplication targets)

| Package | Copies | Worst case |
|---|---|---|
| **nlohmann/json** | **11** | 10 inside PyTorch alone (kineto, fbgemm, cudnn_frontend, ...) + 1 in llama.cpp |
| **googletest** | **10** | all inside PyTorch's nested third_party tree |
| cpp-httplib | 3 | PyTorch x2, llama.cpp x1 |
| fmt | 3 | PyTorch x3 (fmt, kineto/fmt, mkl-dnn/spdlog/fmt) |

## SCAN RESULT C — cross-component collisions

| Package | Copy A | Copy B | Note |
|---|---|---|---|
| array_api_compat | scipy/subprojects | scikit-learn/sklearn/externals | **scipy copy has NO licence file** |
| array_api_extra | scipy/subprojects | scikit-learn/sklearn/externals | both carry LICENSE |
| cpp-httplib | pytorch/third_party | llama.cpp/vendor | both carry LICENSE |
| nlohmann | pytorch/third_party | llama.cpp/vendor | **llama.cpp copy has NO licence file** |

`packagefiles` (3 hits) is a FALSE POSITIVE — meson test fixtures, not vendored code.

Totals: **317 vendored directories, 206 distinct names, 5 raw collisions.**
PyTorch is the dominant source: 43 vendored directories, nested up to four deep.

## IMPORTANT — de-vendoring is NOT automatically correct

Upstreams vendor deliberately. PyTorch's `fmt` may be patched or ABI-matched to its
own build; llama.cpp's `nlohmann` may be pinned to a version its code depends on.
Forcing a single shared copy can break a build that works.

The correct output of this register is a **decision per package**, not a blanket
de-vendor. Three valid outcomes:

- **DEVENDOR** — use one upstream copy; upstream supports an external/system version.
- **KEEP VENDORED** — upstream requires its own copy; record the licence and CVE
  surface explicitly so scanning is not blind to it.
- **DO-NOT-DUPLICATE** — never acquire this as a separate SyMoNeuRaL component,
  because a vendored copy already exists in the estate.

## TO-DO TASKS GENERATED

| # | Package | Task | Decision needed |
|---|---|---|---|
| V1 | ply | BitBake vendors 3.3; upstream is 3.11 | DEVENDOR / KEEP / DO-NOT-DUPLICATE |
| V2 | bs4 | BitBake vendors 4.4.1; upstream far newer | DEVENDOR / KEEP / DO-NOT-DUPLICATE |
| V3 | progressbar, simplediff | BitBake vendored, tiny, unmaintained upstream | likely KEEP — confirm |
| V4 | nlohmann/json | 11 copies; one has no licence file | DEVENDOR where upstream allows |
| V5 | googletest | 10 copies, all test-only | likely KEEP (test scope) — confirm not shipped |
| V6 | cpp-httplib | 3 copies across PyTorch + llama.cpp | DEVENDOR / KEEP |
| V7 | fmt | 3 copies inside PyTorch | DEVENDOR / KEEP |
| V8 | array_api_compat | scipy copy has **no licence file** | licence evidence required before build |
| V9 | array_api_extra | duplicated scipy / scikit-learn | DEVENDOR / KEEP |
| V10 | packaging 23.2 | PyTorch `_vendor` | KEEP (private vendor namespace) — confirm |

## STANDING RULE

Before acquiring any new upstream component, grep this register for its name.
If it appears, the acquisition is a **collision** and requires a decision first.
