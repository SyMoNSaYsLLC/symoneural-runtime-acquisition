#!/usr/bin/env python3
"""scan-acquisition.py - source lock + submodule lock. READ-ONLY, deterministic.

A component's HISTORY lives in its pin store (or, before ingest, its in-tree
.git); its FILES live in the estate repository. So:

  commit_sha / tree_sha / upstream_url / branch   <- the pin (or in-tree .git)
  worktree cleanliness                            <- the estate repository
  recipe fields                                   <- meta-symoneural (SYMON_TREE match)
  submodules / excluded                           <- recorded by tools/ingest-tree at
                                                     ingest, carried from the
                                                     authoritative lock and RE-VERIFIED
                                                     here against the pin's gitlinks
                                                     and the committed content
"""
import os, re, sys, glob, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_acq import (ROOT, AUTH_ACQ, git, git_pin, git_at, gitdir_for, pin_path,
                     has_intree_git, components, census_a, census_b, dump, load, rebuilt_tree)

def recipe_for(abspath):
    """The meta-symoneural recipe whose SYMON_TREE is this tree. Retired recipes
    are found too and flagged, so a retired component keeps its pin/SRCREV
    agreement visible without counting as an active recipe."""
    want = abspath.rstrip("/")
    for pattern, retired in (("meta-symoneural/recipes-*/*/*.bb", False),
                             ("meta-symoneural/retired/*/*.bb", True)):
        for rp in sorted(glob.glob(os.path.join(ROOT, pattern))):
            try: txt = open(rp, encoding="utf-8", errors="ignore").read()
            except OSError: continue
            m = re.search(r'^SYMON_TREE\s*=\s*"([^"]+)"', txt, re.M)
            if m and m.group(1).rstrip("/") == want:
                return os.path.basename(rp).split("_")[0], rp, retired
    return None, None, False
def dep_consumer_for(component):
    """The meta-symoneural recipe that consumes this component as a DEPENDENCY TREE
    (symoneural-pristine SYMON_DEP_TREES = "<name>:<component> ..."): such a tree has no recipe
    of its own - it is compiled into the consumer - and its declared pin IS the lock entry,
    enforced at the consumer's do_unpack by tools/ingest-tree verify. Returns (pn, path, retired)."""
    for pattern, retired in (("meta-symoneural/recipes-*/*/*.bb", False),
                             ("meta-symoneural/retired/*/*.bb", True)):
        for rp in sorted(glob.glob(os.path.join(ROOT, pattern))):
            try: txt = open(rp, encoding="utf-8", errors="ignore").read()
            except OSError: continue
            m = re.search(r'^SYMON_DEP_TREES\s*=\s*"([^"]+)"', txt, re.M)
            if m and any(tok.split(":", 1)[-1] == component for tok in m.group(1).split()):
                return os.path.basename(rp).split("_")[0], rp, retired
    return None, None, False

def fields(rp):
    if not rp: return {}
    t = open(rp, encoding="utf-8", errors="ignore").read()
    one = lambda k: (re.search(r'^%s\s*=\s*"([^"]*)"' % k, t, re.M) or [None, None])[1]
    return {"SRCREV": one("SRCREV"), "PV": one("PV"), "LICENSE": one("LICENSE")}

def gitmodules(path):
    """name -> (path, url) from a .gitmodules FILE in the (committed) work tree.
    The section name is not required to equal the submodule path, so the
    relationship is read through git config -f rather than assumed."""
    out = {}
    gm = os.path.join(path, ".gitmodules")
    if not os.path.isfile(gm): return out
    def cfg(*a):
        r = subprocess.run(["git", "config", "-f", gm, *a], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    for line in cfg("--get-regexp", r"submodule\..*\.path").splitlines():
        k, _, v = line.partition(" ")
        name = k[len("submodule."):-len(".path")]
        url = cfg("--get", "submodule.%s.url" % name)
        out[v.strip()] = (name, url or "UNKNOWN")
    return out

def estate_dirty(rel):
    """Paths under rel whose WORKING TREE differs from the estate index, or that
    are untracked. Column X (index vs HEAD) is irrelevant here; column Y and '??'
    are the question 'was anything written into the acquired tree?'."""
    out = []
    for l in git(ROOT, "status", "--porcelain", "--untracked-files=all", "--", rel).splitlines():
        if l.startswith("??") or l[1:2] != " ":
            out.append(l)
    return out

try:
    AUTH = {c["source_path"]: c for c in load("source-lock.json", base=AUTH_ACQ)["components"]}
except Exception:
    AUTH = {}

COMPS = components()
A, B = census_a(), census_b()

src = {"schema": "symoneural-source-lock/3",
       "census": {"method_a_count": len(A), "method_b_count": len(B),
                  "sets_identical": A == B,
                  "only_in_a": sorted(A - B), "only_in_b": sorted(B - A)},
       "note": ("Exact commit SHA is authoritative; branch is context only. tree_sha is "
                "the upstream commit's tree; HEAD:<source_path> in the estate repository "
                "must equal it (or, with submodules, rebuild to it - tools/ingest-tree verify)."),
       "components": []}
sub = {"schema": "symoneural-submodule-lock/3",
       "identity_key": "owner_source_path + submodule_path",
       "entries": []}

for c in COMPS:
    p, rel = c["abspath"], c["source_path"]
    rec, rp, retired = recipe_for(p)
    via_dep = False
    if rec is None:
        rec, rp, retired = dep_consumer_for(c["component"])
        via_dep = rec is not None
    f = fields(rp)
    head = git_at(p, "rev-parse", "HEAD")
    tree = git_at(p, "rev-parse", head + "^{tree}") if head else ""
    dirty = git(p, "status", "--short").splitlines() if has_intree_git(p) else estate_dirty(rel)
    if via_dep:
        # the consumer's SRCREV is ITS tree's pin; this tree is pinned by the lock entry, which
        # the consumer's build verifies (symoneural-pristine symon_export_dep_trees)
        decl = "SYMON_DEP_TREES:" + rec
        f = {}   # the consumer's PV/LICENSE are its own, not this tree's
        state = "UNKNOWN" if not head else "VERIFIED"
    else:
        decl = f.get("SRCREV")
        state = ("UNKNOWN" if not head else
                 "MISMATCH" if (decl and decl != head) else
                 "VERIFIED" if decl == head else "UNRESOLVED")
    pin = pin_path(rel)
    pins_path = os.path.relpath(pin, ROOT) if pin and os.path.isdir(pin) else "IN-TREE"
    prev = AUTH.get(rel, {})
    subs = [dict(s) for s in prev.get("submodules", [])]
    excluded = prev.get("excluded", [])

    # re-verify every recorded submodule against the pin's gitlink and the
    # committed content, so a carried-forward record cannot silently rot
    for s in subs:
        owner_rel, owner_pin, owner_commit = "", (pin if pins_path != "IN-TREE" else None), head
        for o in subs:
            if o is not s and s["path"].startswith(o["path"] + "/") and len(o["path"]) > len(owner_rel):
                owner_rel, owner_pin, owner_commit = o["path"], os.path.join(ROOT, o["pins_path"]) if o.get("pins_path") else None, o["commit_sha"]
        in_owner = os.path.relpath(s["path"], owner_rel) if owner_rel else s["path"]
        # --full-tree: with --work-tree=/ git would otherwise prefix the path with the cwd
        link = git_pin(owner_pin, "ls-tree", "--full-tree", owner_commit, "--", in_owner) if owner_pin and os.path.isdir(owner_pin) else ""
        parts = link.split()
        s["gitlink_check"] = ("GITLINK-VERIFIED" if len(parts) >= 3 and parts[0] == "160000" and parts[2] == s["commit_sha"]
                              else "GITLINK-MISMATCH" if parts else "GITLINK-UNAVAILABLE")
        # committed content vs the recorded tree. A submodule that itself has
        # submodules holds their CONTENT here where upstream holds gitlinks, so
        # rebuild upstream's shape (direct children -> gitlinks) before comparing.
        direct = []
        for o in subs:
            if o is s or not o["path"].startswith(s["path"] + "/"):
                continue
            between = o["path"][len(s["path"]) + 1:]
            if not any(x is not o and x is not s and o["path"].startswith(x["path"] + "/")
                       and x["path"].startswith(s["path"] + "/") for x in subs):
                direct.append((between, o["commit_sha"]))
        node = "HEAD:%s/%s" % (rel, s["path"])
        committed = rebuilt_tree(node, direct) if direct else git(ROOT, "rev-parse", node)
        s["content_check"] = "AT-RECORDED-TREE" if committed == s.get("tree_sha") else "CONTENT-DRIFTED"

    src["components"].append({
        "runtime": c["runtime"], "category": c["category"], "component": c["component"],
        "source_path": rel,
        "upstream_url": git_at(p, "remote", "get-url", "origin") or "UNKNOWN",
        "declared_version_PV": f.get("PV") or "UNKNOWN",
        "requested_tag": "UNKNOWN",
        "branch_context": git_at(p, "rev-parse", "--abbrev-ref", "HEAD") or "UNKNOWN",
        "commit_sha": head or "UNKNOWN",
        "tree_sha": tree or "UNKNOWN",
        "pins_path": pins_path,
        "recipe_SRCREV": decl or "NOT-APPLICABLE",
        "recipe_LICENSE": f.get("LICENSE") or "NOT-APPLICABLE",
        "lock_state": state,
        "worktree": "clean" if not dirty else "DIRTY",
        "worktree_detail": sorted(dirty)[:5],
        "submodule_count": len(subs),
        "submodules": subs,
        "excluded": excluded,
        "recipe_name": rec or "NOT-APPLICABLE",
        "recipe_path": os.path.relpath(rp, ROOT) if rp else "NOT-APPLICABLE",
        "recipe_retired": bool(retired),
        "bbappend_path": "NOT-APPLICABLE",
        "raw_generated_baseline": "RAW-GENERATED-BASELINE NOT PRESERVED",
    })
    for s in subs:
        owner_rel = ""
        for o in subs:
            if o is not s and s["path"].startswith(o["path"] + "/") and len(o["path"]) > len(owner_rel):
                owner_rel = o["path"]
        owner_dir = os.path.join(p, owner_rel) if owner_rel else p
        in_owner = os.path.relpath(s["path"], owner_rel) if owner_rel else s["path"]
        name, url = gitmodules(owner_dir).get(in_owner, ("UNKNOWN", "UNKNOWN"))
        sub["entries"].append({
            "identity": "%s::%s" % (rel, s["path"]),
            "owner_runtime": c["runtime"], "owner_component": c["component"],
            "owner_source_path": rel,
            "submodule_path": s["path"], "gitmodules_section": name,
            "configured_url": url, "commit_sha": s["commit_sha"],
            "tree_sha": s.get("tree_sha", "UNKNOWN"),
            "pins_path": s.get("pins_path", ""),
            "init_state": "AT-RECORDED-COMMIT" if s["content_check"] == "AT-RECORDED-TREE" else "DRIFTED",
            "status": "VERIFIED" if (s["content_check"] == "AT-RECORDED-TREE"
                                     and s["gitlink_check"] == "GITLINK-VERIFIED") else "UNRESOLVED"})

src["components"].sort(key=lambda x: x["source_path"])
sub["entries"].sort(key=lambda x: x["identity"])
dump(src, "source-lock.json"); dump(sub, "submodule-lock.json")

unk = sum(1 for e in sub["entries"] if e["configured_url"] == "UNKNOWN")
dupe = len(sub["entries"]) - len({e["identity"] for e in sub["entries"]})
unres = sum(1 for e in sub["entries"] if e["status"] != "VERIFIED")
print("census A=%d B=%d identical=%s" % (len(A), len(B), A == B))
print("source-lock    : %d components" % len(src["components"]))
print("submodule-lock : %d entries, %d unknown URL, %d identity collisions, %d not verified"
      % (len(sub["entries"]), unk, dupe, unres))
