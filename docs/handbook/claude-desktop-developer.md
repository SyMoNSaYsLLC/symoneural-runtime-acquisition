# Claude Desktop — developer integrations

**This is the file you lost.** Reconstructed on 2026-09-13 by reading
`~/.config/Claude/` directly, so it describes what is *actually configured now*,
not what was once recommended.

## Where the settings live

| File | Holds |
|---|---|
| `~/.config/Claude/claude_desktop_config.json` | MCP servers, Cowork prefs, trusted folders |
| `~/.config/Claude/developer_settings.json` | **developer toggles — CONTAINS A LIVE API KEY** |
| `~/.config/Claude/config.json` | version, locale, theme, window state |
| `~/.config/Claude/mcp-user-tool-toggles.json` | per-tool enable/disable |

Developer settings are reachable in-app once `allowDevTools` is true.

## Current state — read from disk

### `claude_desktop_config.json`

```
mcpServers                   : 1 server  -> "symoneural"      REGISTERED
isCoworkSdkDebuggingEnabled  : false                          (I set this)
coworkUserFilesPath          : /home/google/Claude
preferences                  : 24 keys
localAgentModeTrustedFolders : 3 entries, all existing
```

`isCoworkSdkDebuggingEnabled: false` was changed to stop a 2.5 MB `sdk-debug.txt`
being written every session. **It only takes effect after an app restart**, and
the app may rewrite the file on exit — so restart rather than leaving it running.

### `developer_settings.json`

```
allowDevTools              : true
inferenceProvider          : "gateway"
inferenceGatewayBaseUrl    : "http://localhost:9001"
inferenceCredentialKind    : "static"
inferenceGatewayAuthScheme : "bearer"
inferenceGatewayApiKey     : <PRESENT — value deliberately not printed, R13>
```

**Handle this file as a credential.** It is excluded from `tools/claude-config`
snapshots and from git. It was one `git add .` away from being committed once
already.

## A correction worth keeping

There is a standing temptation to point `inferenceGatewayBaseUrl` at a
SyMoNeuRaL-built `llama-server`. **Do not treat that as the goal.** Your own
words, and they were right:

> *"you have spent all this fucking time helping me build the sources to make my
> own version of this and then you just through everything out the window with a
> couple side notes"*

Claude Desktop is a **tool you use to build SyMoNeuRaL**. SyMoNeuRaL is the
product. Wiring the tool to consume the product inverts that and proves nothing
about the product. The gateway setting above is a developer convenience, not an
architecture.

## Restart is part of the procedure

Every change in this file requires a **full restart** — quit, do not just close
the window. MCP servers are spawned at launch; config edits are read at launch.

## NOT VERIFIED

25 screenshots of the hamburger menu could not be read in usable form. Nothing
in this file describes them. To document those screens: save them to
`/home/google/Pictures/` and give me the directory, or paste the option names as
text.
