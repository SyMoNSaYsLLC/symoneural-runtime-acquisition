# INSTALL — pre-built packages

> **No release is published yet.** This documents the intended path and states
> plainly what must exist first. Written now so the structure is ready; it will
> be filled in when the first release is cut.

## Why there is no release yet

Status as of 2026-09-15 (the full list, with evidence, is in
`docs/PRODUCTION-VERIFICATION-2026-09-15.md`):

**1. No release unit.** Packages exist for 85 of 86 target components (per the
2026-09-14 workscope audit) and five per-runtime packagegroups exist
(`packagegroup-symoneural-{api,cli,common,llm,ravencalc}`), but
`packagegroup-symoneural-rack` — the tenant unit this document installs — has
not been written, and neither has `packagegroup-symoneural-operator`
(`DECISIONS.md` §1). Without it, "install SyMoNeuRaL" has no meaning. Its
contents are a product decision that has not been made.

**2. No release identity.** `DISTRO` is unset in every build directory, so
`symoneural.conf` has never been loaded; there is no `DISTRO_VERSION`, no PR
service (every package is `-r0`, so a rebuilt package at the same `PV` is not an
upgrade), no `MAINTAINER`, no feed signing, no SBOM or CVE configuration. The
recipetool `1.0+git` placeholder versions noted here earlier have been corrected
(e.g. `symoneural-pytorch_2.14.0-r0`); that blocker is gone.

**3. The release gate has not started.** Phase 20 (licence manifest with no
`Unknown`, NOTICE aggregation, `INCOMPATIBLE_LICENSE` posture, cve-check,
offline re-proof under the pristine class, `tools/pre-publish-audit.sh`) is
defined in `docs/` and `generated/` and nothing in it has run.

**4. Not relocatable.** Absolute `/home/google/SymonSaysLLC` paths in the
recipes, classes and every build configuration mean no one but this host can
rebuild what a release would ship (Phase 19f).

A release therefore requires the packagegroup, the distro identity and the gate
— not an upload of what is on disk today.

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

matched against `acquisition/source-lock.json`, which records `commit_sha` and
`tree_sha` for all 100 acquired trees, and `submodule-lock.json` for their 86
submodules.

## Building instead

See [README.md](README.md) and [BOOTSTRAP.md](BOOTSTRAP.md). Building from source
is the supported path today.
