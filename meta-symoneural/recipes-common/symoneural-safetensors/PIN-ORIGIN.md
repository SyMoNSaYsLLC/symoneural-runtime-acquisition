# PIN-ORIGIN: SYMONEURAL-GENERATED

`Cargo.lock` in this directory is **not upstream's**. safetensors ships no
lockfile anywhere in its tree — only three `Cargo.toml`. Without one there is no
pinned crate set, so a build would resolve from crates.io at build time:
non-deterministic, and it breaks the estate's offline guarantee.

| | |
|---|---|
| Generated | 2026-09-13 |
| By | `cargo generate-lockfile` |
| cargo | 1.97.1 (c980f4866 2026-06-30) |
| rustc | 1.97.1 (8bab26f4f 2026-07-14) |
| Manifest | `bindings/python/Cargo.toml` at SRCREV `a406ca3e7a90598be0cd05a50069cb9bf5ef6ba6` |
| Packages locked | 46 |
| Notable | `pyo3 v0.28.3` selected; v0.29.2 was available but out of the manifest's range |

**Generated in a scratch copy, never in the acquired tree.** R1 holds — the tree
at `Symoneural-Common/src/ml/source/safetensors` reported 0 modifications after
generation.

## Why this is honest

The rule is *own what you ship*: `accelerate` RDEPENDS on safetensors, so it
reaches a customer's disk. A build that cannot run offline cannot be reproduced,
and an unpinned crate set is not a pin at all.

A pin that is ours rather than upstream's is acceptable **once recorded as such**.
An unrecorded one is not — it would read as upstream provenance it does not have.

## When upstream ships a lockfile

Delete this file and the `Cargo.lock` beside it, take upstream's, and remove
`PIN-ORIGIN: SYMONEURAL-GENERATED` from the manifest entry. This is a stopgap with
a defined end, not a permanent fork.
