# Claude — accounts, settings, and the switching problem

## Four accounts

| Email | Note |
|---|---|
| `symonsayadmin@symoneural.com` | Org admin — the identity this machine is configured as |
| `gmcdonald@symoneural.com` | Org member |
| `bhesley@...` | Org member |
| `garrettmcdonald87@gmail.com` | Personal |

The org members export lives at `~/symoneural-ops/claude-org-members.csv`
(3 rows). **Out of git, permanently** — it is personal data for other people.

## THE OPEN PROBLEM: config corruption on account switch

Your requirement, stated directly: *"i have 4 claude accounts please make sure
the settings dont get corrupted when i switch."*

**This is not solved, and I am not going to claim it is.** Claude Desktop keeps
**one** config directory (`~/.config/Claude/`) regardless of which account is
signed in. There is no per-account profile. Switching accounts does not swap
`claude_desktop_config.json`, `developer_settings.json`, or the MCP registration
— they persist across the switch, which is why settings appear to "corrupt": they
are not corrupt, they are the *previous account's* settings still in force.

### What exists to manage that

```sh
tools/claude-config save <label>    # snapshot current config
tools/claude-config diff <label>    # what changed since
tools/claude-config restore <label> # put it back
```

Snapshot **before** switching, restore **after**. `developer_settings.json` is
deliberately excluded from snapshots — it holds a live API key (R13).

### What would actually fix it

A per-account profile wrapper that points `$XDG_CONFIG_HOME` at a different
directory per account, so each identity gets its own config tree. **NOT BUILT.**
It is the correct fix and it is a real piece of work, not a toggle.

## Version channels — not a bug

CLI `2.1.236` and desktop reporting something different is **normal channel
skew**, not desync. `claude update` reporting "up to date (2.1.236)" is correct.
`2.1.246` was pulled. Nothing to fix here.

## The freeze

Fully diagnosed in `docs/symoneuralorgclaudesetup.md` §1. Short version: agent
mode leaks renderer and Node utility processes (**814 threads** observed on 20
cores), which starves `kwin_x11`, which corrupts unrelated Kate and Dolphin
windows. `kwin_x11` took SIGSEGV three times on 11 September.

**Restart Claude Desktop between long agent runs.** That is the single effective
mitigation. Do not run desktop agent work while a bitbake build is running.

## Trusted folders — verified current

Already pruned to 3, all of which exist:

```
/home/google/Desktop     /home/google/Downloads     /home/google/SymonSaysLLC
```

The earlier note about 16 entries with dead paths is **resolved and stale**.
