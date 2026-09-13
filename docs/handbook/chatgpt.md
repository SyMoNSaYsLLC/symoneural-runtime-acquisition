# OpenAI / ChatGPT desktop

## The ask

*"the chatgpt app does the same thing you can fix that too"* — referring to the
freeze-and-corrupt behaviour documented for Claude Desktop.

## The diagnosis transfers, because the cause is not app-specific

Claude Desktop's freeze was **not** a Claude bug. It was Electron renderer and
Node utility processes accumulating until thread count starved the compositor:
**814 threads on 20 cores**, with `kwin_x11` taking SIGSEGV three times on
11 September. Unrelated windows (Kate, Dolphin) corrupted because the compositor
that draws them was starved.

The ChatGPT desktop app is **also Electron**. Same architecture, same failure
mode, same mitigations:

1. **Restart the app between long sessions.** Processes are not reaped on their own.
2. **Do not run it while a bitbake build is going.** Load was already 11–14 at
   five minutes during the observed lockups.
3. **Renice builds so the UI keeps cores:**
   ```sh
   /home/google/SymonSaysLLC/tools/nice-builds
   ```
   One-shot renice of the live bitbake to nice 10 / ionice idle.
4. **Watch for it coming:**
   ```sh
   /home/google/SymonSaysLLC/tools/claude-health
   ```
   Early warning on thread count. It is named for Claude but the thresholds are
   about *this machine*, so it reads true for any Electron app.

## NOT VERIFIED

I have **not** observed a ChatGPT app lockup on this machine or found one in the
journal. The reasoning above is architectural — same framework, same resource
profile — not measured. If it freezes again, capture `htop` (tasks, threads,
load) at the moment it happens and this file can be made specific instead of
inferred.

## No API integration exists

No OpenAI key is configured anywhere in this estate, and none is needed. Same
caution as `gemini.md`: a third-party API is a tool, not the product.
