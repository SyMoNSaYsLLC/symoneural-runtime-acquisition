# Google / Gemini Pro

## Status: NOT STARTED

You have a Gemini Pro account and asked for it to be integrated. **Nothing has
been built, configured, or authenticated.** This file exists so the ask is
recorded rather than forgotten — not to imply progress.

## What "integrated" could mean — decide before building

These are genuinely different pieces of work, and picking one is your call:

| Reading | What it would be | Cost |
|---|---|---|
| **Second opinion** | Query Gemini alongside Claude on design questions | Small — an API key and a CLI wrapper |
| **Product backend** | SyMoNeuRaL routes customer inference to Gemini | **Contradicts the product.** See below |
| **Drive/Workspace** | Gemini's Google Workspace surface | Overlaps `google-drive.md` |

## The reading to reject

**Do not make Gemini a product backend.** The entire point of this estate is
building your own runtimes from pristine source. Routing SyMoNeuRaL inference to
a third-party API is the same architectural inversion flagged in
`claude-desktop-developer.md` — it makes the product a thin wrapper over someone
else's model and makes every month of build work decorative.

Gemini as a *tool you use* is fine. Gemini as *the thing customers get* is not
the product you are building.

## Prerequisite

Nothing here should start before the Phase 11 runtimes build and serve. There is
no integration point yet.
