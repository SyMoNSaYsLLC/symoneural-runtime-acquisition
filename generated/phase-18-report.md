# PHASE 18 — Live, Streamer, Voice: the NET and CPU units

## STATUS: PENDING — NOT STARTED

**starts after: Phase 11 gate**

> **ORDERING (O1).** Each phase's own "Start after" line is authoritative. The
> QUEUED headers' serial chain was a paste convenience and is **WITHDRAWN**.
> Dependency graph:
>
> ```
> 10 → 11 → { 11-T, 18 }
> 11 → 12 → { 13, 14, 17 }
> 13 → 16          14 → 15          { 15, 16, 18 } → 19
> ```
>
> Builds run **concurrently in separate build dirs** when dependencies are met
> (R3', R6'). GPU PROOF steps (12f, 13e/13f, 14e, 16 runs, 17e) execute **one at a
> time through the governor** — train is never evicted, so a 13e run finishes
> before 14e's contention test starts.


Queued 2026-09-13 by Garrett with "QUEUED — do not start." Spec verbatim below.
Nothing acquired, built or streamed. Per A7, `piper` has NOT been cloned.


Milestone: a live source streams to the page over HLS from estate gstreamer;
speech transcribes on CPU during a render.

---

## SETTLED

- **S1** gstreamer is SyMoNeuRaL-owned (D2); build only needed plugin sets;
  accept **no** `LICENSE_FLAGS` commercial; **record what each exclusion cost**.
- **S2** Segmenter is gstreamer, **not ffmpeg**; hls.js stays in the browser.
- **S3** Voice is **CPU-only**.
- **S4** Acquire here (A7): `piper` (MIT) with its **voice model's licence in the
  register**.

## ITEMS

- **18a** `symoneural-gstreamer`: core, base, good, HLS sink (`hlssink3` from
  gst-plugins-rs via cargo, else `hlssink2` only if S1 permits); **plugin list
  recorded**.
- **18b** Live: pipeline units — `videotestsrc`, then v4l2, screen, RTMP/SRT
  ingest — segments to tmpfs served by Caddy; `live` unit registered.
- **18c** Streamer: August's IPTV contract (SSRF guard, Xtream/M3U, EPG, two
  slots) rebuilt in `Symoneural-Streamer/app/` on the gstreamer segmenter; hls.js
  from Phase 10's recipe.
- **18d** Voice: `whisper-cli` unit at `/api/voice` with row and page; piper TTS.

## GATE

Test pattern over HLS with **measured latency under 10 s**; an M3U channel plays;
a 3 s clip transcribes on CPU **during a render**; clean.

## COMMIT

`phase 18: gstreamer HLS live, Streamer rebuilt, Voice unit with TTS`

## RETURN

- GST plugins built, exclusions and cost; LIVE latency, sources
- STREAMER channels, guard tests; VOICE ASR ms during render, TTS voice + licence
- DECISIONS FOR GARRETT: none

---

## NOTES CARRIED IN FROM EARLIER PHASES

**18c's hls.js recipe exists and now represents its full lockfile.**
`symoneural-hlsjs` is hand-curated at PV **1.7.3**, `LICENSE = "Apache-2.0"` read
from the tree, inheriting `symoneural-pristine` + `npm`, with a shipped
`npm-shrinkwrap.json` of **1,073 packages** fetched via `npmsw://`.

Two facts 18c should know. First, recipetool could not generate this recipe:
`devtool add` returned **rc=0** and produced a stub with `SRC_URI=""` and empty
tasks, because hls.js's `package.json` has **no `version` field** and
`create_npm.py:process()` declines on that. The shrinkwrap was produced by
injecting a version into a **disposable** export only — the acquired tree was
verified clean afterwards.

Second, **hls.js has 0 runtime npm dependencies**; all 1,072 non-root packages are
DEV-ONLY. The recipe therefore sets `NPM_INSTALL_DEV = "1"`, because the toolchain
is what *builds* the browser bundle. `dependency-graph.json` independently agrees:
1,072 lockfile rows + 74 `package.json` devDeps = 1,146, every one DEV-ONLY.

**`symoneural-gstreamer` already exists as a recipe** at PV **1.28.7** (derived
from the tag at its pinned SHA during Phase 10's PV sweep, replacing the
`1.0+git` placeholder). 18a extends it; it is not a fresh acquisition.

**S1's "record what each exclusion cost" is the same discipline** the estate
already applies to vendored and collision records — the cost of a decision is
recorded, not just the decision.
