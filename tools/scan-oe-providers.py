#!/usr/bin/env python3
"""scan-oe-providers.py - inventory providers from the LOCKED OE-Core metadata on
disk and build the provider-collision graph. No bitbake execution: PN/PV come from
recipe filenames, PROVIDES from static recipe text.

Provider EXISTENCE is separated from provider SELECTION. The scanner exposes
choices; it never makes an architecture decision.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_acq import ROOT, BOOT, components, dump, load
from collections import defaultdict

META = os.path.join(BOOT, "openembedded-core", "meta")
# D1 admitted meta-oe and meta-python; the provider graph must see what they
# supply or it will report absent providers that are in fact available.
EXTRA_LAYERS = [os.path.join(BOOT, "meta-openembedded", l)
                for l in ("meta-oe", "meta-python")]
EXTRA_LAYERS = [p for p in EXTRA_LAYERS if os.path.isdir(p)]
RE_BB = re.compile(r'^(?P<pn>.+?)_(?P<pv>[^_]+)\.bb$')

recipes, provides_idx = [], defaultdict(list)
n_files = 0
for _root in [META] + EXTRA_LAYERS:
  for dp, dn, fn in os.walk(_root):
      dn[:] = sorted(dn)
      for f in sorted(fn):
          if not f.endswith(".bb"): continue
          n_files += 1
          m = RE_BB.match(f)
          pn = m.group("pn") if m else f[:-3]
          pv = m.group("pv") if m else "UNKNOWN"
          rp = os.path.relpath(os.path.join(dp, f), BOOT)
          prov = []
          try:
              t = open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
              for pm in re.finditer(r'^PROVIDES\s*[:+]?=?\s*[+]?=\s*"([^"]*)"', t, re.M):
                  prov += pm.group(1).split()
          except OSError:
              pass
          rec = {"PN": pn, "PV": pv, "recipe_path": rp,
                 "PROVIDES": sorted(set(prov)) or []}
          recipes.append(rec)
          provides_idx[pn].append(rec)
          for p in rec["PROVIDES"]:
              provides_idx[p].append(rec)

# ---- logical-name normalisation so OE PN and SyMoNeuRaL names can be compared
def logical(n):
    n = n.lower()
    n = re.sub(r'^symoneural-', '', n)
    n = re.sub(r'^python3-', '', n)
    n = re.sub(r'1\.0$', '', n)          # gstreamer1.0 -> gstreamer
    n = n.replace('_', '-')
    return n.strip('-')

direct = {}
for c in components():
    direct.setdefault(logical(c["component"]), []).append(c)

vend = load("vendor-lock.json")["vendored"]
subs = load("submodule-lock.json")["entries"]
sub_idx = defaultdict(list)
for e in subs:
    # a git submodule IS a source copy with its own upstream identity; excluding
    # it from the provider graph understates the collision surface
    sub_idx[logical(os.path.basename(e["submodule_path"]))].append(e)
vend_idx = defaultdict(list)
for v in vend: vend_idx[logical(v["name"])].append(v)

oe_idx = defaultdict(list)
for r in recipes:
    oe_idx[logical(r["PN"])].append(r)
    for p in r["PROVIDES"]: oe_idx[logical(p)].append(r)

collisions = []
for key in sorted(set(direct) | set(vend_idx) | set(sub_idx)):
    provs = []
    for c in direct.get(key, []):
        provs.append({"kind": "DIRECT-ACQUISITION", "state": "AVAILABLE",
                      "identity": "%s/%s" % (c["runtime"], c["component"]),
                      "version": "see source-lock", "location": c["source_path"]})
    for r in oe_idx.get(key, [])[:4]:
        provs.append({"kind": "OE-CORE-RECIPE", "state": "AVAILABLE",
                      "identity": r["PN"], "version": r["PV"],
                      "location": r["recipe_path"]})
    for e in sub_idx.get(key, [])[:6]:
        provs.append({"kind": "SUBMODULE", "state": "AVAILABLE",
                      "identity": "%s/%s" % (e["owner_runtime"], e["owner_component"]),
                      "version": e["commit_sha"][:12],
                      "location": e["owner_source_path"] + "/" + e["submodule_path"]})
    for v in vend_idx.get(key, [])[:6]:
        provs.append({"kind": "VENDORED", "state": "AVAILABLE",
                      "identity": v["owning_upstream"], "version": v["version"],
                      "location": v["location"]})
    kinds = {p["kind"] for p in provs}
    owners = {p["identity"] for p in provs}
    if len(provs) > 1 and (len(kinds) > 1 or len(owners) > 1):
        collisions.append({
            "logical_dependency": key,
            "provider_count": len(provs),
            "provider_kinds": sorted(kinds),
            "providers": provs,
            "consumers": sorted(owners),
            "link_scope": "UNKNOWN",
            "selected_provider": "UNRESOLVED",
            "decision": "UNRESOLVED",
            "evidence": "tools/scan-oe-providers.py"})

collisions.sort(key=lambda x: (-x["provider_count"], x["logical_dependency"]))

# --- MERGE curated D2 decisions -------------------------------------------
# Scanner-derived records are overwritten on every regeneration, so decisions
# must live in a curated record and be merged in here. Hand-editing the output
# is exactly how host_designation was silently lost.
try:
    _pd = load("provider-decisions.json")["decisions"]
    _by = {d["logical"]: d for d in _pd}
    for _c in collisions:
        _d = _by.get(_c["logical_dependency"])
        if _d:
            _c["selected_provider"] = _d["selected_provider"]
            _c["decision"] = "RESOLVED (D2): " + _d["rationale"]
except Exception as _e:
    print("WARN: provider-decisions merge skipped: %s" % _e)

dump({"schema": "symoneural-provider-collisions/2",
      "note": "Provider EXISTENCE only. selected_provider stays UNRESOLVED; the "
              "scanner exposes choices and does not make architecture decisions.",
      "oe_core_recipes_inspected": n_files,
      "oe_core_providers_indexed": len(oe_idx),
      "collisions": collisions}, "provider-collisions.json")

direct_coll = sum(1 for c in collisions if "DIRECT-ACQUISITION" in c["provider_kinds"]
                  and "OE-CORE-RECIPE" in c["provider_kinds"])
print("OE recipes inspected : %d" % n_files)
print("providers indexed    : %d" % len(oe_idx))
print("collisions           : %d" % len(collisions))
print("direct-vs-OE-Core    : %d" % direct_coll)
for c in collisions:
    if "DIRECT-ACQUISITION" in c["provider_kinds"] and "OE-CORE-RECIPE" in c["provider_kinds"]:
        oe = [p for p in c["providers"] if p["kind"] == "OE-CORE-RECIPE"][0]
        print("   *** %-16s direct-acquisition  vs  OE-Core %s %s"
              % (c["logical_dependency"], oe["identity"], oe["version"]))
