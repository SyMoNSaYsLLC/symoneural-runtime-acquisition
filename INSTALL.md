# INSTALL — pre-built packages

> **No release is published yet.** This documents the intended path and states
> plainly what must exist first. Written now so the structure is ready; it will
> be filled in when the first release is cut.

## Why there is no release yet

Two blockers, both real:

**1. No packagegroup.** 248 `.ipk` files exist across the build directories, but
they are loose packages, not a coherent installable unit.
`packagegroup-symoneural-rack` is **Phase 11d**. Without it, "install SyMoNeuRaL"
has no meaning — there is no list of what constitutes the product.

**2. The built packages carry stale versions.** Every `.ipk` currently in
`tmp/deploy/ipk/` is named `<pkg>_1.0+git-r0`. That was recipetool's placeholder
`PV`, corrected across 22 recipes in Phase 10 by deriving each version from the
release tag at its pinned SHA (`symoneural-fastapi` → `0.141.1`,
`symoneural-pydantic` → `2.13.5`, and so on). **The deploy directory predates
that fix.** Releasing those artifacts would ship packages whose versions are
meaningless and whose dependency resolution cannot work.

A release therefore requires a rebuild after the PV correction, not just an
upload of what is on disk today.

## What a release will contain

| Artifact | What |
|---|---|
| `symoneural-rack-<version>-<arch>.tar.zst` | the packagegroup and its dependency closure as `.ipk` |
| `SHA256SUMS` | checksums for every artifact |
| `sbom-<version>.spdx.json` | SPDX SBOM (Phase 15e) |
| `cve-report-<version>.txt` | `cve-check` output by severity (Phase 15e) |

Attached to a git tag as a **GitHub Release** — release assets, not git objects.
Nothing binary enters the repository itself.

## Installing (once published)

```sh
# 1. fetch and verify
curl -LO https://github.com/<owner>/<repo>/releases/download/<tag>/symoneural-rack-<version>-x86-64-v3.tar.zst
curl -LO https://github.com/<owner>/<repo>/releases/download/<tag>/SHA256SUMS
sha256sum -c SHA256SUMS --ignore-missing

# 2. unpack the feed
mkdir -p /opt/symoneural/feed && tar -I zstd -xf symoneural-rack-*.tar.zst -C /opt/symoneural/feed

# 3. install with opkg
opkg --offline-root / add-dependent-feed symoneural file:///opt/symoneural/feed
opkg update && opkg install packagegroup-symoneural-rack
```

## What install does NOT give you

**Secrets.** `/etc/symoneural/*.env` is provisioned by `symoneural-secrets`
(R13), never shipped. A unit whose secret is unset is configured **OFF** and
named in the report — it does not fail, it stays off.

**Model weights.** `SYMON_MODELS_DIR` (`/home/google/symoneural-models`) is
populated separately per the register in `acquisition/model-register.json`, with
each file recorded FOUND / FETCHED / ABSENT by sha256. Weights never enter git
and never ship in a package.

**A relocatable install.** Until Phase 19f, absolute paths are baked in. See the
limitation in [README.md](README.md).

## Verifying what you installed

Every package traces to a pinned commit:

```sh
opkg info symoneural-numpy          # version, e.g. 2.5.3
```

matched against `acquisition/source-lock.json`, which records `commit_sha` for
all 41 acquired trees, and `submodule-lock.json` for their 85 submodules.

## Building instead

See [README.md](README.md) and [BOOTSTRAP.md](BOOTSTRAP.md). Building from source
is the supported path today.
