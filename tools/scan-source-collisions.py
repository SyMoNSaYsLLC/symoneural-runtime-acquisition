#!/usr/bin/env python3
"""scan-source-collisions.py - cross-runtime source collision map (v1.2 §9c).

Keyed by normalised logical source name. Every provider kind is treated on equal
terms: DIRECT-ACQUISITION, SUBMODULE, VENDORED, OE-CORE-RECIPE.

DETECTION ONLY. Nothing is collapsed, deleted or rewritten; every entry carries
selected_provider=UNRESOLVED and decision=UNRESOLVED. De-duplication is an
architecture decision and belongs after acquisition is complete.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_acq import ROOT, BOOT, load, dump
from collections import defaultdict

def logical(n):
    n = os.path.basename(n.rstrip("/")).lower()
    n = re.sub(r'^(symoneural-|python3?-|lib)', '', n)
    n = re.sub(r'1\.0$', '', n)
    n = re.sub(r'[._]', '-', n)
    return n.strip('-') or "UNKNOWN"

sl = load("source-lock.json")["components"]
sm = load("submodule-lock.json")["entries"]
vl = load("vendor-lock.json")["vendored"]
pc = load("provider-collisions.json")

prov = defaultdict(list)
for c in sl:
    prov[logical(c["component"])].append({
        "kind": "DIRECT-ACQUISITION", "runtime": c["runtime"],
        "owning_component": c["component"], "path": c["source_path"],
        "resolved_revision": c["commit_sha"],
        "upstream_url": c["upstream_url"]})
for e in sm:
    prov[logical(e["submodule_path"])].append({
        "kind": "SUBMODULE", "runtime": e["owner_runtime"],
        "owning_component": e["owner_component"],
        "path": e["owner_source_path"] + "/" + e["submodule_path"],
        "resolved_revision": e["commit_sha"],
        "upstream_url": e["configured_url"]})
for v in vl:
    prov[logical(v["name"])].append({
        "kind": "VENDORED", "runtime": v["owning_upstream"].split("/")[0],
        "owning_component": v["owning_upstream"].split("/")[-1],
        "path": v["location"], "resolved_revision": "UNKNOWN",
        "upstream_url": "UNKNOWN"})
for c in pc["collisions"]:
    for p in c["providers"]:
        if p["kind"] == "OE-CORE-RECIPE":
            prov[c["logical_dependency"]].append({
                "kind": "OE-CORE-RECIPE", "runtime": "<build-stack>",
                "owning_component": p["identity"], "path": p["location"],
                "resolved_revision": p["version"], "upstream_url": "openembedded-core"})

entries = []
for name in sorted(prov):
    ps = sorted(prov[name], key=lambda x: (x["kind"], x["path"]))
    kinds = {p["kind"] for p in ps}
    rts = {p["runtime"] for p in ps if p["runtime"] != "<build-stack>"}
    comps = {(p["runtime"], p["owning_component"]) for p in ps if p["runtime"] != "<build-stack>"}
    flags = []
    if len(ps) > 1:
        if len(rts) > 1:     flags.append("CROSS-RUNTIME-DUPLICATE")
        elif len(comps) > 1: flags.append("CROSS-COMPONENT-DUPLICATE")
        else:                flags.append("INTRA-COMPONENT-DUPLICATE")
    direct_vs_oe = "DIRECT-ACQUISITION" in kinds and "OE-CORE-RECIPE" in kinds
    if direct_vs_oe:
        flags.append("DIRECT-VERSUS-OE-CORE")
    # DIRECT-VERSUS-OE-CORE takes precedence as the primary label: a SyMoNeuRaL
    # acquisition duplicating a recipe the locked base already provides is the
    # most architecturally actionable signal. Duplicate SCOPE is kept as a flag
    # so nothing is lost.
    if direct_vs_oe:                primary = "DIRECT-VERSUS-OE-CORE"
    elif len(ps) == 1:              primary = "SINGLE-PROVIDER"
    else:                           primary = flags[0]
    entries.append({
        "logical_source": name, "provider_count": len(ps),
        "provider_kinds": sorted(kinds), "runtimes": sorted(rts),
        "classification": primary, "classification_flags": sorted(set(flags)),
        "providers": ps,
        "selected_provider": "UNRESOLVED", "decision": "UNRESOLVED"})

entries.sort(key=lambda e: (-e["provider_count"], e["logical_source"]))
dump({"schema": "symoneural-source-collisions/1",
      "note": "DETECTION ONLY. No copy is collapsed, deleted or rewritten. "
              "Every entry is UNRESOLVED by design.",
      "provider_kinds_indexed": ["DIRECT-ACQUISITION", "OE-CORE-RECIPE",
                                 "SUBMODULE", "VENDORED"],
      "entries": entries}, "source-collisions.json")

from collections import Counter
cc = Counter(e["classification"] for e in entries)
fc = Counter(f for e in entries for f in e["classification_flags"])
multi = [e for e in entries if e["provider_count"] > 1]
print("logical sources indexed     : %d" % len(entries))
print("logical names with >1 provider: %d" % len(multi))
for k in ("INTRA-COMPONENT-DUPLICATE","CROSS-COMPONENT-DUPLICATE",
          "CROSS-RUNTIME-DUPLICATE","DIRECT-VERSUS-OE-CORE"):
    print("  %-28s primary=%-4d flagged=%d" % (k+":", cc.get(k,0), fc.get(k,0)))
print("  %-28s %d" % ("SINGLE-PROVIDER:", cc.get("SINGLE-PROVIDER",0)))
print("  all decisions UNRESOLVED   : %s" %
      all(e["selected_provider"]=="UNRESOLVED" and e["decision"]=="UNRESOLVED" for e in entries))
print("cross-runtime detail:")
for e in entries:
    if e["classification"] == "CROSS-RUNTIME-DUPLICATE":
        print("  %-18s runtimes=%-22s copies=%d kinds=%s"
              % (e["logical_source"], ",".join(e["runtimes"]),
                 e["provider_count"], ",".join(e["provider_kinds"])))
