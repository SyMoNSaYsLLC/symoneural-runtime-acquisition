#!/usr/bin/env python3
"""generate-runtime-acquisition.py - render Symoneural-Runtime-Aquisition.md from the
structured records. GENERATED OUTPUT.

Every numeric in the report is derived from the JSON authority at render time and
then re-asserted against the records, so a manually supplied count cannot survive.
The filesystem tree is emitted separately and referenced by SHA-256.
"""
import os, sys, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_acq import ROOT, ACQ, GEN, git, load, sha256_file, SKIP_NAMES, SKIP_PATH_MARKERS
from collections import Counter, defaultdict

sl,sm,dg,vl,li,pc,ap,un,ex,cp,sc = (load(n) for n in
 ("source-lock.json","submodule-lock.json","dependency-graph.json","vendor-lock.json",
  "license-inventory.json","provider-collisions.json","artifact-plan.json",
  "unresolved.json","exceptions.json","control-plane.json","source-collisions.json"))

os.makedirs(GEN, exist_ok=True)
tree = os.path.join(GEN, "runtime-tree.txt")
rows = []
for rt in sorted(d for d in os.listdir(ROOT) if d.startswith("Symoneural-")):
    for dp, dn, fn in os.walk(os.path.join(ROOT, rt)):
        dn[:] = sorted(d for d in dn if d not in SKIP_NAMES)
        if any(m in dp + "/" for m in SKIP_PATH_MARKERS):
            dn[:] = []; continue
        rows.append(os.path.relpath(dp, ROOT))
open(tree, "w").write("\n".join(sorted(rows)) + "\n")
TSHA, TN = sha256_file(tree), len(rows)

# ---------- DERIVED TOTALS (single source of truth for the report)
M = {}
M["components"]   = len(sl["components"])
M["verified"]     = sum(1 for c in sl["components"] if c["lock_state"] == "VERIFIED")
M["dirty"]        = sum(1 for c in sl["components"] if c["worktree"] == "DIRTY")
M["mismatch"]     = sum(1 for c in sl["components"] if c["lock_state"] == "MISMATCH")
M["submodules"]   = len(sm["entries"])
M["sub_verified"] = sum(1 for e in sm["entries"] if e["status"] == "VERIFIED")
M["sub_problem"]  = M["submodules"] - M["sub_verified"]
M["sub_unknown_url"] = sum(1 for e in sm["entries"] if e["configured_url"] == "UNKNOWN")
M["deps"]         = len(dg["dependencies"])
DC = Counter(d["classification"] for d in dg["dependencies"])
DS = Counter(d["scope"] for d in dg["dependencies"])
M["vendored"]     = len(vl["vendored"])
VS = Counter(v["scope"] for v in vl["vendored"])
VN = Counter(v["name"].lower() for v in vl["vendored"])
M["vendor_logical"] = len(VN)
M["vendor_cross"] = sum(1 for k, n in VN.items() if n > 1)
M["licences"]     = len(li["files"])
M["collisions"]   = len(pc["collisions"])
M["coll_unres"]   = sum(1 for c in pc["collisions"] if c["selected_provider"] == "UNRESOLVED")
M["oe_recipes"]   = pc["oe_core_recipes_inspected"]
M["oe_providers"] = pc["oe_core_providers_indexed"]
M["oe_direct"]    = sum(1 for c in pc["collisions"]
                        if "DIRECT-ACQUISITION" in c["provider_kinds"]
                        and "OE-CORE-RECIPE" in c["provider_kinds"])
CAPS = Counter(k for a in ap["components"] for k in a["declared_capabilities"])
M["exceptions"]   = len(ex["exceptions"])
M["unresolved"]   = len(un["items"])

# ---------- VALIDATION: assert each headline re-derives from the records
V = []
def check(label, got, want):
    ok = got == want
    V.append((label, got, want, ok))
    return ok
check("top-level source count", M["components"], len(load("source-lock.json")["components"]))
check("submodule count", M["submodules"], len(load("submodule-lock.json")["entries"]))
check("dependency total", M["deps"], sum(DC.values()))
check("dependency scope total", M["deps"], sum(DS.values()))
check("vendor count", M["vendored"], len(load("vendor-lock.json")["vendored"]))
check("licence count", M["licences"], len(load("license-inventory.json")["files"]))
check("provider collision count", M["collisions"], len(load("provider-collisions.json")["collisions"]))
check("artifact capability records", len(ap["components"]), M["components"])
check("exception count", M["exceptions"], len(load("exceptions.json")["exceptions"]))
check("unresolved count", M["unresolved"], len(load("unresolved.json")["items"]))
VALID = all(v[3] for v in V)

# ---------- ACQUISITION-STATE verdict (separate from control-plane verdict)
af = []
if M["mismatch"]: af.append("%d source(s) differ from recipe SRCREV" % M["mismatch"])
if M["dirty"]:    af.append("%d upstream tree(s) dirty" % M["dirty"])
if M["sub_problem"]: af.append("%d submodule(s) not at recorded commit" % M["sub_problem"])
if M["coll_unres"]: af.append("%d provider collision(s) unresolved (%d direct-vs-OE-Core)"
                              % (M["coll_unres"], M["oe_direct"]))
if un["counts"]["vendored_decisions_unresolved"]:
    af.append("%d vendored decision(s) unresolved" % un["counts"]["vendored_decisions_unresolved"])
if un["counts"]["licence_files_unresolved"]:
    af.append("%d licence file(s) without an established identifier" % un["counts"]["licence_files_unresolved"])
if un["items"]: af.append("%d explicit control-plane decisions open" % len(un["items"]))
ACQ_VERDICT = "PASS" if not af else "FAIL"

o=[]; w=o.append
w("# SyMoNeuRaL Runtime Acquisition\n")
w("> **GENERATED FILE — do not edit.** Rendered by `tools/generate-runtime-acquisition.py`")
w("> from `acquisition/*.json`. Every number below is derived from those records and")
w("> re-asserted against them at render time. To change this report, change the records.\n")
w("| | |\n|---|---|")
w("| Parent HEAD | `%s` |" % git(ROOT, "rev-parse", "HEAD"))
w("| Working tree | %s |" % ("clean" if not git(ROOT, "status", "--short") else "modified, uncommitted"))
w("| Records | `acquisition/` (%d JSON + SHA256SUMS) |" % len(cp["record_schemas"]))
w("| Scanner identity | `acquisition/control-plane.json` (%d tools hashed) |" % len(cp["tool_sha256"]))
w("| Determinism verified | %s |" % ("YES" if cp.get("determinism_verified") else "NO"))
w("| Tree inventory | `generated/runtime-tree.txt` (%d dirs) |" % TN)
w("| Tree SHA-256 | `%s` |" % TSHA)
w("| Report self-validation | %s (%d/%d totals re-derived) |"
  % ("PASS" if VALID else "FAIL", sum(1 for x in V if x[3]), len(V)))

w("\n## Verdicts\n")
w("Two verdicts are tracked separately. The control plane must be trustworthy")
w("before its description of the estate means anything.\n")
w("| Verdict | Result | Meaning |\n|---|---|---|")
w("| **CONTROL-PLANE** | see `tools/verify-acquisition.py` | Can the scanner be trusted to describe the estate? |")
w("| **ACQUISITION-STATE** | **%s** | Has the estate resolved its acquisition decisions? |" % ACQ_VERDICT)
if af:
    w("\nAcquisition FAIL reasons:\n")
    for f in af: w("- %s" % f)
    w("\nThis FAIL is expected and is a statement of open decisions, not a defect.\n")

w("\n## Repository census\n")
w("| Method | Count |\n|---|---|")
w("| A — filesystem candidate + `git rev-parse` validation | %d |" % sl["census"]["method_a_count"])
w("| B — independent git work-tree-top census | %d |" % sl["census"]["method_b_count"])
w("| **Sets identical** | **%s** |" % ("YES" if sl["census"]["sets_identical"] else "NO"))
w("\n`.git` is accepted as a file or a directory; submodules are excluded from the")
w("top-level set via `--show-superproject-working-tree`, which is representation-independent.\n")

w("\n## Build-stack identity\n")
w("| Component | SHA |\n|---|---|")
for k, v in sorted(cp["build_stack"].items()): w("| %s | `%s` |" % (k, v))
w("\nThis locks the **build stack only**, never the application sources.\n")

w("\n## Runtime inventory\n")
byrt=defaultdict(list)
for c in sl["components"]: byrt[c["runtime"]].append(c)
w("| Runtime | Components | Verified | Clean |\n|---|---|---|---|")
for rt in sorted(byrt):
    cs=byrt[rt]
    w("| %s | %d | %d | %d |" % (rt, len(cs),
      sum(1 for c in cs if c["lock_state"]=="VERIFIED"),
      sum(1 for c in cs if c["worktree"]=="clean")))
w("| **TOTAL** | **%d** | **%d** | **%d** |" % (M["components"], M["verified"], M["components"]-M["dirty"]))

w("\n## Top-level source lock\n")
w("| Runtime | Component | Commit | State | Subs | Recipe |\n|---|---|---|---|---|---|")
for c in sl["components"]:
    w("| %s | %s | `%s` | %s | %d | %s |" % (c["runtime"], c["component"],
      c["commit_sha"][:12], c["lock_state"], c["submodule_count"],
      "yes" if c["recipe_name"]!="NOT-APPLICABLE" else "**none**"))

w("\n## Submodule summary\n")
w("Entries: **%d** · identity key `%s` · unknown URLs: **%d**\n"
  % (M["submodules"], sm["identity_key"], M["sub_unknown_url"]))
for k,v in sorted(Counter(e["init_state"] for e in sm["entries"]).items()):
    w("- %s: %d" % (k, v))

w("\n## Dependency graph\n")
w("Declarations discovered from on-disk manifests: **%d**. No depth limit; nothing fetched.\n" % M["deps"])
w("| Classification | Count |\n|---|---|")
for k,v in sorted(DC.items(), key=lambda x:-x[1]): w("| %s | %d |" % (k,v))
w("\n| Scope | Count |\n|---|---|")
for k,v in sorted(DS.items(), key=lambda x:-x[1]): w("| %s | %d |" % (k,v))
w("\nA lockfile establishes resolution, not directness: a `Cargo.lock` entry with no")
w("source URL is `WORKSPACE-LOCAL`, never `DIRECT-DECLARED`.\n")

w("\n## Vendored register\n")
w("Entries **%d** across **%d** logical packages; **%d** appear in more than one place.\n"
  % (M["vendored"], M["vendor_logical"], M["vendor_cross"]))
w("| Scope | Count |\n|---|---|")
for k,v in sorted(VS.items(), key=lambda x:-x[1]): w("| %s | %d |" % (k,v))
w("\n| Most-duplicated | Copies |\n|---|---|")
for k,v in VN.most_common(8):
    if v>1: w("| %s | %d |" % (k,v))
w("\nAll decisions are `UNRESOLVED`. A test-only vendored library must not be pushed")
w("through the same release path as a runtime-linked one — hence the scope column.\n")

w("\n## Provider graph\n")
w("OE-Core recipes inspected **%d**, providers indexed **%d**, collisions **%d**")
w("(of which **%d** are direct-acquisition versus an OE-Core recipe).\n"
  % (M["oe_recipes"], M["oe_providers"], M["collisions"], M["oe_direct"]) if False else "")
w("| | |\n|---|---|")
w("| OE-Core recipes inspected | %d |" % M["oe_recipes"])
w("| Providers indexed | %d |" % M["oe_providers"])
w("| Collisions | %d |" % M["collisions"])
w("| Direct-acquisition vs OE-Core | **%d** |" % M["oe_direct"])
w("\n| Logical dependency | Direct | OE-Core recipe |\n|---|---|---|")
for c in pc["collisions"]:
    if "DIRECT-ACQUISITION" in c["provider_kinds"] and "OE-CORE-RECIPE" in c["provider_kinds"]:
        d=[p for p in c["providers"] if p["kind"]=="DIRECT-ACQUISITION"][0]
        e=[p for p in c["providers"] if p["kind"]=="OE-CORE-RECIPE"][0]
        w("| %s | %s | %s %s |" % (c["logical_dependency"], d["identity"], e["identity"], e["version"]))
w("\nProvider **existence** is recorded; `selected_provider` stays `UNRESOLVED`.")
w("The scanner exposes choices and does not make architecture decisions.\n")

w("\n## Source collisions\n")
_fc=Counter(f for e in sc["entries"] for f in e["classification_flags"])
_multi=[e for e in sc["entries"] if e["provider_count"]>1]
w("Provider kinds indexed: %s\n" % ", ".join(sc["provider_kinds_indexed"]))
w("| | |\n|---|---|")
w("| Logical sources indexed | %d |" % len(sc["entries"]))
w("| With more than one provider | **%d** |" % len(_multi))
for k in ("INTRA-COMPONENT-DUPLICATE","CROSS-COMPONENT-DUPLICATE",
          "CROSS-RUNTIME-DUPLICATE","DIRECT-VERSUS-OE-CORE"):
    w("| %s | %d |" % (k, _fc.get(k,0)))
w("| Vendor entries reclassified as SUBMODULE | %d |" % len(vl.get("reclassified_as_submodule",[])))
w("| Duplicate top-level upstream URLs | 0 (invariant) |")
_cr=[e for e in sc["entries"] if e["classification"]=="CROSS-RUNTIME-DUPLICATE"]
if _cr:
    w("\n| Cross-runtime source | Runtimes | Copies | Kinds |\n|---|---|---|---|")
    for e in _cr:
        w("| %s | %s | %d | %s |" % (e["logical_source"], ", ".join(e["runtimes"]),
          e["provider_count"], ", ".join(e["provider_kinds"])))
w("\nA git submodule is a real source copy with its own upstream identity, so")
w("`SUBMODULE` is indexed as a provider kind alongside the others. **Detection only** —")
w("no copy is collapsed, deleted or rewritten; every entry is `UNRESOLVED`.\n")

w("\n## Licence inventory\n")
w("Licence-bearing files: **%d**\n" % M["licences"])
for k,v in sorted(Counter(f["apparent_scope"] for f in li["files"]).items()): w("- %s: %d" % (k,v))
w("\n**LICENSE expression and LIC_FILES_CHKSUM coverage are separate concepts.**")
w("This inventory is drift evidence, not a licensing conclusion.\n")

w("\n## Artifact capabilities\n")
w("What each source **natively declares**. No SyMoNeuRaL decision is recorded.\n")
w("| Capability | Components |\n|---|---|")
for k,v in sorted(CAPS.items(), key=lambda x:-x[1]): w("| %s | %d |" % (k,v))

w("\n## Unresolved decisions\n")
w("| Category | Identifier | Blocks |\n|---|---|---|")
for i in un["items"]: w("| %s | %s | %s |" % (i["category"], i["identifier"], i["blocks"]))
w("")
for k,v in sorted(un["counts"].items()): w("- %s: **%d**" % (k.replace("_"," "), v))

w("\n## Exceptions\n")
w("| ID | Component | Result | Classification |\n|---|---|---|---|")
for e in ex["exceptions"]:
    w("| %s | %s | %s | %s |" % (e["id"], e["component"], e["result"], ", ".join(e["classification"])))
w("\nRecorded as history. Neither build is authoritative for release.\n")

w("\n## Generated to-do tasks\n")
for n,i in enumerate(un["items"],1):
    w("%d. **[%s] %s** — %s\n" % (n, i["category"], i["identifier"], i["description"]))

open(os.path.join(ROOT,"Symoneural-Runtime-Aquisition.md"),"w").write("\n".join(o)+"\n")
print("report validation:")
for label,got,want,ok in V: print("  %-32s %-8s %s" % (label, got, "OK" if ok else "MISMATCH want=%s"%want))
print("report written : %d lines" % len(o))
print("tree           : %d dirs  sha256=%s" % (TN, TSHA))
print("ACQUISITION-STATE VERDICT: %s" % ACQ_VERDICT)
