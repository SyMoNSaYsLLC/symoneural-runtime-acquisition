# DECISION FOR GARRETT — does the estate need Node on the target at all?

Raised 2026-09-13 during Phase 10e. **Not acted on**: this is a scope change to an
acquired component, and those have come back as Garrett's rulings twice tonight
(mcp typescript-sdk, workers-sdk). Recorded with proof so it can be decided, not
inferred.

## THE CLAIM

**Target `nodejs` is required by nothing the estate ships, and the one recipe that
forces it onto the target has no consumer.** If that holds, target `nodejs` drops
out of the estate entirely and roughly an hour of V8 compilation stops being part
of every future npm build.

`nodejs-native` is a **separate matter and genuinely needed** — it is what builds
the hls.js browser bundle. This claim is only about the *target* runtime.

## THE PROOF

**1. `npm.bbclass` forces Node twice, unconditionally.** Verbatim from
`openembedded-core/meta/classes-recipe/npm.bbclass`:

```
26: DEPENDS:prepend = "nodejs-native nodejs-oe-cache-native "
27: RDEPENDS:${PN}:append:class-target = " nodejs"
```

Line 26 builds Node for the **host** (so bitbake has an `npm`). Line 27 puts Node
on the **target** as a runtime dependency of any npm package. Neither is
conditional on what the package actually is.

**2. The cost is not small.** The currently running target build, measured:

```
elapsed          55+ minutes, still linking
objects          919 obj.target + 919 obj.host for v8_base_without_compiler alone
                 (this single recipe builds V8 TWICE - host tooling and target)
work directory   9.1 GB
nodejs-native    a further 1.6 GB, ~30 min, built earlier tonight
```

**3. No shipped unit is a Node service.** The 15 units named across the phase
specs: `asic chat coder exp image live miner project rack ravencalc remix sigils
streamer studio voice`. The API is FastAPI (Python), the gateway is
Rust/Caddy/Go, Chat is `llama-server` (C++), Voice is `whisper-cli` (C++).

**4. Only two npm recipes exist**, and they are different cases:

| recipe | needs `nodejs-native` to BUILD | needs target `nodejs` to RUN |
|---|---|---|
| `symoneural-hlsjs` | **yes** — the bundler produces `dist/hls.min.js` | **no** — it is a browser asset. Advisor P2 already removes it: `RDEPENDS:${PN}:remove = "nodejs"` |
| `symoneural-anthropic-sdk-typescript` | yes | only because it is a Node library — **and nothing consumes it** |

**5. The TypeScript SDK has no consumer — one incidental mention, not a use.**
Raw output, nothing removed:

```
$ grep -rn "anthropic-sdk-typescript" meta-symoneural --include=*.bb --include=*.bbappend
meta-symoneural/recipes-cli/symoneural-anthropic-sdk-typescript/symoneural-anthropic-sdk-typescript_git.bb:24:HOMEPAGE = "https://github.com/anthropics/anthropic-sdk-typescript"
meta-symoneural/recipes-cli/symoneural-anthropic-sdk-typescript/symoneural-anthropic-sdk-typescript_git.bb:32:SYMON_TREE = ".../anthropic-sdk-typescript"

$ grep -rn "anthropic-sdk-typescript" generated/phase-1[1-9]*.md
generated/phase-15-report.md:113:(`symoneural-anthropic-sdk-typescript`, `symoneural-hlsjs`) ship a
```

Both recipe hits are the recipe's own `HOMEPAGE` and `SYMON_TREE` — self-references,
not dependencies. **No `DEPENDS` or `RDEPENDS` anywhere names it.** The single
phase-spec hit at `phase-15-report.md:113` is prose I wrote myself, noting that
npmsw works in this estate; it is an incidental mention, not a consumer.

> **CORRECTION.** The first version of this brief reported "NONE" for the phase-spec
> grep. That was produced by a command that piped the result through
> `grep -v "phase-15-report.md:113"` — the one hit was FILTERED OUT and the filtered
> result then presented as if unfiltered. The conclusion is unchanged, but the proof
> as first stated was not honest. Raw output is pasted above, and grep output is
> pasted rather than summarised from here on.

The client CLI actually uses is **`symoneural-anthropic-sdk-python`**, which
already builds clean and installs **2,817 files**. Same reasoning by which
`mcp typescript-sdk` was ruled REFERENCE-ONLY: *"no shipped unit consumes it; Coder
and Studio run on the Python SDK."*

## RULING — RECEIVED 2026-09-13

**`symoneural-anthropic-sdk-typescript` is REFERENCE-ONLY. Target `nodejs` ships
nowhere.** Verified independently against the tree at `fe7a24bc`: npm.bbclass 26-27
verbatim, no recipe consumer, anthropic-sdk-python built at 2,817 files.

## THE QUESTION (answered above; retained for the record)

Should `symoneural-anthropic-sdk-typescript` be **REFERENCE-ONLY** as well —
acquired and pinned, not built?

**If YES:** hls.js is the only npm recipe, it needs no target Node (P2 already
removes it), and **target `nodejs` is needed by nothing**. It never enters a
shipped image and never has to be rebuilt. `nodejs-native` stays, because the
bundle must still be built.

**If NO:** the TS SDK is built and ships, target Node comes with it, and the cost
is a one-time ~1 hour now cached in sstate.

## WHAT IS BEING DONE MEANWHILE

Per the built-in advisor, and deliberately **not** pre-empting the decision:

1. The running target-Node build is **allowed to finish**. The cost is sunk either
   way; letting it land puts it in sstate where hls.js reuses it. Killing it now
   would pay the cost and cache nothing.
2. **Both recipes are built as Phase 10e's gate (E3) specifies.** That gate is
   satisfiable now and closes Phase 10. It is not reopened over a design question
   that does not block it.
3. If the answer later is REFERENCE-ONLY, the change is a recipe removal and a
   manifest row — cheap, and nothing built tonight is wasted.

## ONE VERIFICATION OWED REGARDLESS

P2's `RDEPENDS:${PN}:remove = "nodejs"` on hls.js must be **confirmed to have taken
effect**, because `npm.bbclass:27` applies it via `:append:class-target` and
override ordering against `:remove` is not always intuitive:

```
bitbake -e symoneural-hlsjs | grep '^RDEPENDS:symoneural-hlsjs='
```

If `nodejs` survives that expression, a static browser asset is still dragging a
Node runtime onto the target and P2's third point has silently failed — the kind of
failure that reports success.
