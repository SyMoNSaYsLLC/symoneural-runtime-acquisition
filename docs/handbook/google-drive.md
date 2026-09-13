# Google Drive

## What it is to this project

The Drive (`/mnt/gdrive` when mounted) is where recoverable prior work lived —
it is **not** a build input and nothing in the build reads from it.

## What was recovered from it

**134 icon files** — `symoneural-mark`, `ravencalc`, `studio`, `terminal`,
`sync`, `support`, `reinforce`, `iptv` — at 16–512 px plus SVG sources. These
are the brand assets Phase 15d needs. They exist **only on the Drive** and are
not in git.

## The standing constraint on recovery

**Do not use anything from August.** Your instruction, and it holds for every
recovery from Drive, from `/yocto`, and from transcripts. August-era artifacts
predate the fresh start and re-importing them reintroduces exactly the state this
repo was created to leave behind.

## Related: what was preserved from /yocto

`/yocto` was 112 GB and has been deleted. Before deletion, **358 MB** was
extracted to:

```
/home/google/symoneural-archive/yocto-2026-08-25/
```

sha256-verified `2974ceed743c9fe385d8a60355d4c316`. That archive is the record;
`/yocto` itself is gone and is not coming back.

## NOT STARTED

The brand assets have not been brought into the repo. That is Phase 15d and is
not begun. When it is, the decision to make first is **which** of the 134 files
are canonical — 134 icons is an export, not a brand system.

Weights are a separate matter entirely — see `huggingface.md`. Nothing about
Drive changes the rule that weights never enter git.
