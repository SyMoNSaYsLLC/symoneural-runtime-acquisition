# SyMoNeuRaL — Claude setup for the org

Written 2026-09-13 from what is on this machine. Everything below was read from
disk, not recalled. Where I could not verify something, it says so.

---

## 1. THE FREEZE — diagnosed

**Symptom:** Claude Desktop intermittently locks up and corrupts Kate and Dolphin
windows, *"towards the tail end of an agent working in the desktop app"*.

**It is not the GPU.** The app already runs `--disable-gpu` (confirmed in the
process list), the compositor is `kwin_x11` on X11, and there are **zero** NVIDIA
Xid faults in the journal. VRAM sits at 1,361 MiB of 16,303 MiB at rest.

**It is not RAM.** Your own capture during a lockup: `7.83G / 94.1G` — **8% used**.

**It is process and thread proliferation from agent mode.** From your htop
captures:

| Capture | Tasks | Threads | Memory | Load (1/5/15) |
|---|---:|---:|---|---|
| 21:51 | 165 | **814** | 9.38 G / 94.1 G | 3.78 / 11.47 / 14.46 |
| 21:55 | 137 | 693 | 6.70 G | 3.65 / 6.32 / 11.52 |

The process tree showed **dozens** of:

```
claude-desktop --type=renderer      ~400–450 MB each
claude-desktop --type=utility --utility-sub-type=node.mojom.NodeService
claude-code/2.1.266/claude --output-format stream-json ... --effort max
```

Each agent turn spawns renderer and Node utility processes plus a `claude-code`
CLI child. They accumulate rather than being reaped. **814 threads** on 20 cores
is what starves `kwin_x11` — and a starved compositor is exactly how unrelated
windows (Kate, Dolphin) corrupt.

`kwin_x11` has in fact crashed with **SIGSEGV** three times, all on 11 September
(15:37, 15:39, 15:40), each followed by a reboot.

### What to do

1. **Restart Claude Desktop between long agent runs.** The processes do not come
   back on their own; a restart reaps them. This is the single most effective step.
2. **Don't run desktop agent work while a build is running.** Load was already
   11–14 at five minutes in both captures.
3. **SDK debugging is now off** — I set `isCoworkSdkDebuggingEnabled: false` in
   `claude_desktop_config.json` (backup alongside it, timestamped). It had been
   writing a 2.5 MB `sdk-debug.txt`. **Restart the app for this to take**, and
   restart rather than leaving it running, since the app may rewrite the file on
   exit.
4. **Deprioritise builds so the UI keeps cores:**
   ```sh
   nice -n 10 ionice -c3 bitbake <target>
   ```
5. **Cap build concurrency at two build directories** at
   `BB_NUMBER_THREADS=10` / `PARALLEL_MAKE="-j 12"`, or three at `-j 6`.
   Three directories at current settings can ask for ~30 tasks × 12 jobs on 20
   cores.

---

## 2. SKILLS PLUGIN — what is installed

`/home/google/.config/Claude/local-agent-mode-sessions/skills-plugin/`

Plugin: `anthropic-skills` v1.0.0, *"Anthropic-managed skills for Claude Desktop"*.
Installed per org/session UUID, so the same set appears under several directories.

**22 skills present:**

| Group | Skills |
|---|---|
| Documents | `docx` · `xlsx` · `pptx` · `pdf` |
| Design | `canvas-design` · `theme-factory` · `brand-guidelines` · `algorithmic-art` · `web-artifacts-builder` |
| Authoring | `doc-coauthoring` · `internal-comms` · `slack-gif-creator` |
| Memory | `consolidate-memory` · `import-memory` · `learn` |
| Setup | `setup-claude` · `setup-cowork` · `mcp-builder` · `skill-creator` |
| Routine | `morning` · `schedule` · `explain-usage` |

Each carries `enabled: true` and a trigger description. `creatorType: anthropic` —
these are managed, not authored by you.

### Which matter for SyMoNeuRaL

**`brand-guidelines`** — you have 134 icon files (`symoneural-mark`, `ravencalc`,
`studio`, `terminal`, `sync`, `support`, `reinforce`, `iptv`) at 16–512 px plus
SVG sources, currently only on the Drive. Phase 15d needs exactly this. Feeding
the palette and marks into a brand skill would make every later artifact
consistent without restating it.

**`skill-creator`** — the case for a SyMoNeuRaL-specific skill. The rules that
keep being restated (R1 pristine source, R12 empty-`${D}`, R16 declared-is-not-done,
never `git add .`, one bitbake per build directory) are exactly what a skill
encodes once.

**`web-artifacts-builder` / `canvas-design`** — for the site, alongside
`docs/build-manuals.html`.

**Not useful here:** `slack-gif-creator`, `internal-comms`, `morning`.

---

## 3. ORGANISATION SETTINGS — how to get them to me

I can read local config. I **cannot** read claude.ai org settings, another
conversation, or a Cowork thread. Three ways to bridge that:

**Members export** — already done. `/home/google/symoneural-ops/claude-org-members.csv`
(`0600`, dir `0700`), 3 rows, columns `Name, Email, Role, Status, Seat Tier`.
Kept **out of git** — it is personal data for other people. See `ops/README.md`.

**Settings screens** — paste the values as text, or save screenshots to
`/home/google/Pictures/` and give me the paths. I read them from disk.

**Local config I can already see:**

| File | What it holds |
|---|---|
| `~/.config/Claude/claude_desktop_config.json` | MCP servers (currently **empty**), Cowork prefs, **16 trusted folders** |
| `~/.config/Claude/config.json` | version, locale, theme, window state |
| `~/.config/Claude/developer_settings.json` | developer toggles |
| `~/.config/Claude/mcp-user-tool-toggles.json` | per-tool enable/disable |
| `~/.config/Claude/plan-usage-history.json` | usage history |

### What I could not verify

You sent 25 screenshots of the hamburger menu. **I could not read their contents
in a usable form**, so nothing in this document describes them. Rather than guess
at settings I cannot see: save them to `/home/google/Pictures/` and give me the
directory, or paste the option names as text, and I will write that section
properly.

### One thing worth checking yourself

`localAgentModeTrustedFolders` lists **16 directories**, several of which no
longer exist (`/home/google/symonsaysllc` lowercase, `/home/google/attic`,
`/home/google/darwin_build`, `/home/google/yuki`). Trusted-folder lists are a
permission surface; entries for paths that do not exist are harmless today but
become live the moment something recreates that path. Worth pruning to the ones
you actually use.

---

## 4. SSO — where it stands

Identity provider is **Zoho Directory** (Zoho One — `one.zoho.com` appears in your
SPF record). Custom SAML, since Zoho is not in Anthropic's provider list.

Done: app created in Zoho with `Issuer` and ACS URL matching
(`YtgXgNBn2yIWMIIadbpBgincL`), NameID format **Email Address**, Application
Username **Primary email address**, and attribute mapping `email` / `firstName` /
`lastName`.

Remaining: paste Zoho's **IdP Login URL**, **IdP Entity ID** and **X.509
certificate** into Anthropic's step 3, then test in a clean browser before
enabling JIT provisioning.

**Nothing is needed on Cloudflare for SSO.** Your domain is already Verified. The
Cloudflare work is Phase 15's tunnel, unrelated.

**Still outstanding:** your org **invite link was visible in a screenshot**
(`claude.ai/join/org#...`, auto-approving anyone with an `@symoneural.com`
address, valid to 28 Oct 2026). **Rotate it** — the ⟳ beside the copy button.
