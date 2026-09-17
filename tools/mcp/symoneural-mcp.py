#!/usr/bin/env python3
"""
symoneural-mcp — an MCP server that answers questions about the estate from
DISK, not from memory.

Why this exists. Three things were reported complete in this estate that had
never executed: a Fortran runtime never built, a distro config never loaded, and
assertion tasks whose names never bound. Each was found only when something
downstream needed it. R16 ("declared is not done — name the evidence") is the
rule; this server is the instrument, so any Claude session can check state
against the tree instead of trusting a transcript.

Tools:
  estate_status      what is built, pinned, open — counts with paths
  phase_state        per-phase status parsed from generated/phase-*-report.md
  open_decisions     acquisition/unresolved.json: open rows, ruled rows, release-gated rulings
  pin                a component's pinned SHA + worktree state from source-lock
  check_history      has an approach already failed? searches the transcripts
  verify_claim       R16 in one call: does an artifact actually exist on disk

Speaks MCP over stdio. No dependencies beyond the standard library.
"""
import json, os, re, subprocess, sys, glob

ROOT = "/home/google/SymonSaysLLC"
HIST = "/home/google/.claude/projects"

def _load(p):
    with open(os.path.join(ROOT, p)) as f:
        return json.load(f)

def _is_open(item):
    """unresolved.json keeps ruled items in `items` as history (state RESOLVED-A etc.).
    A row is open only if its state does not begin with RESOLVED. Same rule as
    tools/generate-runtime-acquisition.py, so the two never disagree on the count."""
    return not str(item.get("state", "OPEN")).upper().startswith("RESOLVED")

def _gated(un):
    """Rows filed under `resolved` that are NOT closed for release purposes:
    DEFERRED (e.g. the kawpowminer GPL ruling) and RESOLVED-SCOPED (e.g. offline-compile,
    which says 'RE-PROOF REQUIRED before any release claim')."""
    out = []
    for i in un.get("resolved", []):
        st = str(i.get("state", "")).upper()
        if st == "RESOLVED-SCOPED" or not st.startswith(("RESOLVED", "ACCEPTED", "REFERENCE-ONLY")):
            out.append(i)
    return out

def estate_status(**_):
    sl = _load("acquisition/source-lock.json")["components"]
    un = _load("acquisition/unresolved.json")
    recipes = [p for p in glob.glob(f"{ROOT}/meta-symoneural/recipes-*/*/*.bb") if "/retired/" not in p]
    # Every build directory, not only devtool-master (Platform has a second one).
    staged  = glob.glob(f"{ROOT}/Symoneural-*/build/*/tmp/work/*/symoneural-*/*/image")
    dirty   = [c["source_path"] for c in sl if c.get("worktree") != "clean"]
    open_items = [i for i in un["items"] if _is_open(i)]
    return {
        "pinned_sources": len(sl),
        "recipes": len(recipes),
        # Per-recipe ${D} staging directories found under tmp/work. This is NOT a count
        # of images (the estate has 5 image recipes); it was previously mislabelled.
        "recipes_with_image_dir": len(staged),
        "open_decisions": len(open_items),
        "open_decision_ids": [i["identifier"] for i in open_items],
        "ruled_in_items": len(un["items"]) - len(open_items),
        "release_gated_rulings": [f'{i.get("identifier")} ({i.get("state")})' for i in _gated(un)],
        "resolved_decisions": len(un.get("resolved", [])),
        "dirty_trees": dirty or "none",
        "head": subprocess.run(["git","-C",ROOT,"rev-parse","--short","HEAD"],
                               capture_output=True, text=True).stdout.strip(),
    }

def phase_state(**_):
    out = {}
    for p in sorted(glob.glob(f"{ROOT}/generated/phase-*-report.md")):
        name = re.sub(r".*phase-|-report\.md", "", p)
        txt = open(p, errors="ignore").read()
        m = re.search(r"^## STATUS:\s*(.+)$", txt, re.M)
        s = re.search(r"\*\*starts after:([^*]+)\*\*", txt)
        # Absence of a STATUS line is not evidence of closure (R16). Say so.
        out[name] = {"status": (m.group(1).strip() if m else "NO STATUS LINE IN REPORT — not evidence of closure"),
                     "starts_after": (s.group(1).strip() if s else "-"),
                     "lines": txt.count("\n")}
    return out

def open_decisions(**_):
    d = _load("acquisition/unresolved.json")
    row = lambda i: {"id": i["identifier"], "category": i.get("category"),
                     "state": i.get("state"), "blocks": i.get("blocks")}
    return {
        "open": [row(i) for i in d["items"] if _is_open(i)],
        "ruled_still_listed_in_items": [row(i) for i in d["items"] if not _is_open(i)],
        "release_gated_rulings": [row(i) for i in _gated(d)],
    }

def pin(component: str = "", **_):
    sl = _load("acquisition/source-lock.json")["components"]
    hits = [c for c in sl if component.lower() in c.get("source_path","").lower()]
    return hits or {"error": f"no component matching {component!r}"}

def check_history(term: str = "", **_):
    """Has this been tried before, and did it fail? The estate's own record."""
    if not term:
        return {"error": "term required"}
    r = subprocess.run([f"{ROOT}/tools/check-history.sh", term, "--failures"],
                       capture_output=True, text=True, timeout=600)
    return {"output": r.stdout[-6000:] or "(no record — absence of a hit is NOT proof it is safe)"}

def verify_claim(path: str = "", min_bytes: int = 1, **_):
    """R16 in one call. Does the artifact exist, and is it non-trivial?"""
    if not path:
        return {"error": "path required"}
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.exists(p):
        return {"exists": False, "verdict": "NOT DONE — artifact absent", "path": p}
    if os.path.isdir(p):
        n = sum(len(f) for _,_,f in os.walk(p))
        return {"exists": True, "is_dir": True, "files": n,
                "verdict": "DONE" if n else "NOT DONE — directory is empty", "path": p}
    sz = os.path.getsize(p)
    return {"exists": True, "bytes": sz,
            "verdict": "DONE" if sz >= min_bytes else f"NOT DONE — {sz} < {min_bytes} bytes",
            "path": p}

TOOLS = {
    "estate_status":  (estate_status,  "What is built, pinned and open. Counts with evidence.", {}),
    "phase_state":    (phase_state,    "Per-phase status read from the report files on disk.", {}),
    "open_decisions": (open_decisions, "Control-plane decisions: open, ruled-but-listed, and release-gated rulings (DEFERRED / RESOLVED-SCOPED).", {}),
    "pin":            (pin,            "A component's pinned SHA and worktree state.",
                       {"component": {"type":"string","description":"name fragment, e.g. numpy"}}),
    "check_history":  (check_history,  "Has this approach already failed here? Searches 134 session transcripts.",
                       {"term": {"type":"string","description":"approach, flag or error text"}}),
    "verify_claim":   (verify_claim,   "R16: does the artifact actually exist on disk?",
                       {"path": {"type":"string","description":"path, absolute or repo-relative"},
                        "min_bytes": {"type":"integer","description":"minimum plausible size"}}),
}

def send(o): sys.stdout.write(json.dumps(o) + "\n"); sys.stdout.flush()

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try: req = json.loads(line)
        except Exception: continue
        mid, method = req.get("id"), req.get("method")
        if method == "initialize":
            send({"jsonrpc":"2.0","id":mid,"result":{
                "protocolVersion":"2024-11-05",
                "capabilities":{"tools":{}},
                "serverInfo":{"name":"symoneural","version":"1.0.0"}}})
        elif method == "tools/list":
            send({"jsonrpc":"2.0","id":mid,"result":{"tools":[
                {"name":n,"description":d,
                 "inputSchema":{"type":"object","properties":p,
                                "required":[k for k in p if k in ("term","component","path")]}}
                for n,(f,d,p) in TOOLS.items()]}})
        elif method == "tools/call":
            nm = req.get("params",{}).get("name")
            args = req.get("params",{}).get("arguments",{}) or {}
            try:
                res = TOOLS[nm][0](**args)
                send({"jsonrpc":"2.0","id":mid,"result":{
                    "content":[{"type":"text","text":json.dumps(res,indent=2)}]}})
            except Exception as e:
                send({"jsonrpc":"2.0","id":mid,"result":{
                    "content":[{"type":"text","text":f"error: {e}"}],"isError":True}})
        elif mid is not None:
            send({"jsonrpc":"2.0","id":mid,"result":{}})

if __name__ == "__main__":
    main()
