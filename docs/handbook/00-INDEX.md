# SyMoNeuRaL — Stakeholder Handbook

One file per stakeholder. Everything here was read from this machine's disk on
**2026-09-13**, not recalled from memory. Where something could not be verified,
the file says so in those words.

---

## THE ONE RULE — where these files live

**Canonical:** `SymonSaysLLC/docs/handbook/` (in git, published, reviewable)
**Your copy:** `~/Desktop/symonsaysllchandbook/` — **GENERATED, never edited**

Regenerate the Desktop copy at any time:

```sh
/home/google/SymonSaysLLC/tools/gen-handbook
```

### Why this rule exists, specifically

On 2026-08-20 a task list was duplicated. `PROJECT-TASKS.md` stayed canonical,
`CODER-TASKS.md` was retired — and an agent read the retired copy and started
working from it. It took a hard stop to halt:

> *"Stop. This worker is stale and must not continue. Do not create
> CODER-TASKS.md... PROJECT-TASKS.md is the canonical task list. CODER-TASKS.md
> is a retired/nonexistent name."*

Two copies of the same knowledge, no stated winner, and work proceeded from the
wrong one. A Desktop handbook is *structurally the same risk*. It is defused by
making the Desktop copy an output rather than a sibling: edit the repo, re-run
the generator. If the two ever disagree, **the repo wins and the Desktop copy is
stale by definition.**

---

## Stakeholders

| File | Stakeholder | State |
|---|---|---|
| `github.md` | GitHub — two accounts | Repo live, one account wired |
| `claude.md` | Claude — four accounts | Account-switch corruption is the open problem |
| `claude-desktop-developer.md` | Claude Desktop developer settings | MCP registered; inference gateway configured |
| `mcp.md` | The SyMoNeuRaL MCP server | 6 tools, registered, needs app restart |
| `zoho.md` | Zoho Directory — SSO / IdP | 3 steps remain |
| `cloudflare.md` | Cloudflare | Nothing required for SSO; Phase 15 tunnel only |
| `gemini.md` | Google / Gemini Pro | NOT STARTED |
| `chatgpt.md` | OpenAI / ChatGPT desktop | Same freeze class as Claude Desktop |
| `google-drive.md` | Google Drive | Source of recovered brand assets |
| `huggingface.md` | Hugging Face | Weights policy — never in git |

`SCHEDULE.md` is the sequence view. **Read its first paragraph before using it.**

---

## Two standing constraints these files obey

**R13 — no secrets, ever.** No token, key, password or certificate appears in
any handbook file. Where a credential exists, the file names *where it lives* and
nothing more. `developer_settings.json` holds a real API key and is excluded from
every snapshot and from git for this reason.

**The org invite link is deliberately absent.** It was exposed in a screenshot
(auto-approves any `@symoneural.com` address, valid to 28 Oct 2026) and still
needs rotating. Reprinting it here would widen an exposure that is already open.
Rotate it with the ⟳ beside the copy button in the org settings.

---

## Toolchain finding — Darwin Swift SDK, 2026-09-13

`~/.swiftpm/swift-sdks/darwin.artifactbundle` — **3.2 GB, installed, populated,
and unusable.** Two separate defects, found only by trying to compile:

**1. Host-triple mismatch, fixed.** The bundle declared support for
`x86_64-unknown-linux-gnu`; this host reports `x86_64-pc-linux-gnu`. One token —
`pc` vs `unknown` — and `swift build --swift-sdk darwin` answered *"No Swift SDK
found"* while `swift sdk list` happily printed `darwin`. Added the host triple to
`info.json` (backed up alongside).

**2. Compiler generation mismatch, NOT fixable by configuration.**

```
host Swift  6.0.3 (swift-6.0.3-RELEASE, Debian)
SDK         MacOSX26.5.sdk / prebuilt-modules 26.5   (Xcode 26.5 generation)
result      swift-frontend: Assertion `idx < size()' failed, SmallVector.h:294
```

The compiler is far older than the SDK and aborts parsing its module data. No
flag fixes this; it needs a Swift toolchain matched to the SDK generation.

**Why this belongs in the handbook rather than a bug report:** it is the estate's
thesis in miniature. A *prebuilt* toolchain carries assumptions about the
toolchain that produced it, and when those assumptions do not hold, the artifact
is inert in a way that looks installed. Building from pinned source is what makes
the version relationship something we choose rather than something we discover.

Five target triples are present in the bundle and would be available once the
compiler matches: `x86_64-apple-macosx`, `arm64-apple-macosx`, `arm64-apple-ios`,
`x86_64-apple-ios-simulator`, `arm64-apple-ios-simulator`.
