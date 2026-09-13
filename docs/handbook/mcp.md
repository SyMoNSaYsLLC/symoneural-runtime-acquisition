# MCP — the SyMoNeuRaL server

## What it is

`tools/mcp/symoneural-mcp.py` — a local MCP server exposing the estate's own
state to Claude, so answers come from disk instead of from recall.

## Registered — verified in the live config

```json
{
  "mcpServers": {
    "symoneural": {
      "command": "python3",
      "args": ["/home/google/SymonSaysLLC/tools/mcp/symoneural-mcp.py"]
    }
  }
}
```

**Requires an app restart to become live.** Registration is not activation.

## The six tools

| Tool | Answers |
|---|---|
| `estate_status` | What exists on disk right now |
| `phase_state` | Which phase, which items, from the phase reports |
| `open_decisions` | Decisions still unmade |
| `pin` | The pinned SRCREV for a given upstream |
| `check_history` | Searches 134 prior transcripts for a prior attempt |
| `verify_claim` | **R16 as a callable** |

## `verify_claim` is the important one

R16 is the rule that *"DECLARED IS NOT DONE"* — an item is done only when its
artifact exists on disk or a consumer exercised it. `verify_claim` makes that
mechanical: it takes a claim and checks it against the filesystem rather than
against a report that says it was completed.

This exists because the failure kept repeating: a phase marked complete whose
tasks were all no-ops. Phase 10 closed only after **every assertion task turned
out to be a no-op** and was made live.

## Verify it is actually running

After restarting the app, ask for `estate_status`. If the tool is not offered,
it did not start — check the path in the stanza above and that `python3` resolves.
