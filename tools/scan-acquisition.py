#!/usr/bin/env python3
"""scan-acquisition.py - source lock + submodule lock. READ-ONLY, deterministic."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_acq import (ROOT, git, components, census_a, census_b, dump, LOCKED_STACK, BOOT)

def recipe_for(rt, abspath):
    wsa = os.path.join(ROOT, "Symoneural-"+rt, "build", "devtool-workspace", "appends")
    wsr = os.path.join(ROOT, "Symoneural-"+rt, "build", "devtool-workspace", "recipes")
    if not os.path.isdir(wsa):
        return None, None, None
    for a in sorted(os.listdir(wsa)):
        ap = os.path.join(wsa, a)
        try: txt = open(ap, encoding="utf-8", errors="ignore").read()
        except OSError: continue
        if re.search(r'EXTERNALSRC\s*=\s*"%s"' % re.escape(abspath), txt):
            n = a.replace("_git.bbappend", "")
            rp = os.path.join(wsr, n, n + "_git.bb")
            return n, (rp if os.path.isfile(rp) else None), ap
    return None, None, None

def fields(rp):
    if not rp: return {}
    t = open(rp, encoding="utf-8", errors="ignore").read()
    one = lambda k: (re.search(r'^%s\s*=\s*"([^"]*)"' % k, t, re.M) or [None, None])[1]
    return {"SRCREV": one("SRCREV"), "PV": one("PV"), "LICENSE": one("LICENSE")}

def gitmodules(path):
    """name -> (path, url). The .gitmodules SECTION NAME is not required to equal
    the submodule path, so the relationship is resolved through git config rather
    than assumed."""
    out = {}
    gm = os.path.join(path, ".gitmodules")
    if not os.path.isfile(gm): return out
    for line in git(path, "config", "-f", ".gitmodules",
                    "--get-regexp", r"submodule\..*\.path").splitlines():
        k, _, v = line.partition(" ")
        name = k[len("submodule."):-len(".path")]
        url = git(path, "config", "-f", ".gitmodules", "--get",
                  "submodule.%s.url" % name)
        out[v.strip()] = (name, url or "UNKNOWN")
    return out

COMPS = components()
A, B = census_a(), census_b()

src = {"schema": "symoneural-source-lock/2",
       "census": {"method_a_count": len(A), "method_b_count": len(B),
                  "sets_identical": A == B,
                  "only_in_a": sorted(A - B), "only_in_b": sorted(B - A)},
       "note": "Exact commit SHA is authoritative; branch is context only.",
       "components": []}
sub = {"schema": "symoneural-submodule-lock/2",
       "identity_key": "owner_source_path + submodule_path",
       "entries": []}

for c in COMPS:
    p = c["abspath"]
    rec, rp, ap = recipe_for(c["runtime"], p)
    f = fields(rp)
    head = git(p, "rev-parse", "HEAD")
    st = git(p, "status", "--short")
    decl = f.get("SRCREV")
    state = ("UNKNOWN" if not head else
             "MISMATCH" if (decl and decl != head) else
             "VERIFIED" if decl == head else "UNRESOLVED")
    gm = gitmodules(p)
    smlines = [l for l in git(p, "submodule", "status", "--recursive").splitlines() if l.strip()]
    src["components"].append({
        "runtime": c["runtime"], "category": c["category"], "component": c["component"],
        "source_path": c["source_path"],
        "upstream_url": git(p, "remote", "get-url", "origin") or "UNKNOWN",
        "declared_version_PV": f.get("PV") or "UNKNOWN",
        "requested_tag": "UNKNOWN",
        "branch_context": git(p, "rev-parse", "--abbrev-ref", "HEAD") or "UNKNOWN",
        "commit_sha": head or "UNKNOWN",
        "recipe_SRCREV": decl or "NOT-APPLICABLE",
        "recipe_LICENSE": f.get("LICENSE") or "NOT-APPLICABLE",
        "lock_state": state,
        "worktree": "clean" if st == "" else "DIRTY",
        "worktree_detail": sorted(st.splitlines())[:5],
        "submodule_count": len(smlines),
        "recipe_name": rec or "NOT-APPLICABLE",
        "recipe_path": os.path.relpath(rp, ROOT) if rp else "NOT-APPLICABLE",
        "bbappend_path": os.path.relpath(ap, ROOT) if ap else "NOT-APPLICABLE",
        "raw_generated_baseline": "RAW-GENERATED-BASELINE NOT PRESERVED",
    })
    for line in smlines:
        flag = line[0] if line[0] in "-+U" else " "
        parts = line[1:].split()
        if len(parts) < 2: continue
        sha, sp = parts[0], parts[1]
        name, url = gm.get(sp, (None, None))
        if url is None:
            # Nested submodule: its .gitmodules lives in the INTERMEDIATE repo,
            # not the top-level component. Ask git which superproject owns it,
            # then read that superproject's .gitmodules for the relative path.
            full = os.path.join(p, sp)
            sup = git(full, "rev-parse", "--show-superproject-working-tree")
            if sup and os.path.isdir(sup):
                rel = os.path.relpath(full, sup)
                for k, (n2, u2) in gitmodules(sup).items():
                    if k == rel:
                        name, url = n2, u2
                        break
            if url is None:
                name, url = "UNKNOWN", "UNKNOWN"
        sub["entries"].append({
            "identity": "%s::%s" % (c["source_path"], sp),
            "owner_runtime": c["runtime"], "owner_component": c["component"],
            "owner_source_path": c["source_path"],
            "submodule_path": sp, "gitmodules_section": name,
            "configured_url": url, "commit_sha": sha,
            "init_state": {"-": "NOT-INITIALISED", "+": "DRIFTED",
                           "U": "MERGE-CONFLICT", " ": "AT-RECORDED-COMMIT"}[flag],
            "status": "VERIFIED" if flag == " " else "UNRESOLVED"})

src["components"].sort(key=lambda x: x["source_path"])
sub["entries"].sort(key=lambda x: x["identity"])
dump(src, "source-lock.json"); dump(sub, "submodule-lock.json")

unk = sum(1 for e in sub["entries"] if e["configured_url"] == "UNKNOWN")
dupe = len(sub["entries"]) - len({e["identity"] for e in sub["entries"]})
print("census A=%d B=%d identical=%s" % (len(A), len(B), A == B))
print("source-lock    : %d components" % len(src["components"]))
print("submodule-lock : %d entries, %d unknown URL, %d identity collisions"
      % (len(sub["entries"]), unk, dupe))
