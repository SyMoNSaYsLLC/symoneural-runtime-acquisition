#!/usr/bin/env python3
"""check-determinism.py - run the full scanner suite twice into isolated dirs and
require byte-identical records. Also writes acquisition/SHA256SUMS and
acquisition/control-plane.json (scanner identity)."""
import os, sys, json, hashlib, tempfile, subprocess, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_acq import ROOT, ACQ, LOCKED_STACK, sha256_file

TOOLS = os.path.dirname(os.path.abspath(__file__))
SCANNERS = ["scan-acquisition.py", "scan-dependencies.py", "scan-oe-providers.py",
            "scan-source-collisions.py"]
RECORDS = ["source-lock.json","submodule-lock.json","dependency-graph.json",
           "vendor-lock.json","license-inventory.json","provider-collisions.json",
           "artifact-plan.json", "source-collisions.json"]

def run(out):
    env = dict(os.environ, ACQ_OUT=out)
    for s in SCANNERS:
        r = subprocess.run([sys.executable, os.path.join(TOOLS, s)],
                           capture_output=True, text=True, env=env, cwd=ROOT)
        if r.returncode != 0:
            print("scanner %s FAILED: %s" % (s, r.stderr[-300:])); sys.exit(2)

a, b = tempfile.mkdtemp(prefix="det-a-"), tempfile.mkdtemp(prefix="det-b-")
try:
    run(a); run(b)
    ok, rows = True, []
    for r in RECORDS:
        pa, pb = os.path.join(a, r), os.path.join(b, r)
        ha = sha256_file(pa) if os.path.isfile(pa) else "MISSING"
        hb = sha256_file(pb) if os.path.isfile(pb) else "MISSING"
        same = ha == hb and ha != "MISSING"
        ok &= same
        rows.append((r, ha, hb, same))
        print("  %-28s %s  %s" % (r, "IDENTICAL" if same else "*** DIFFERS ***", ha[:16]))
    print("RUN_A_SHA256 == RUN_B_SHA256 : %s" % ("YES" if ok else "NO"))
finally:
    shutil.rmtree(a, ignore_errors=True); shutil.rmtree(b, ignore_errors=True)

# ---- SHA256SUMS over the authoritative records
lines = []
for r in sorted(os.listdir(ACQ)):
    if r.endswith(".json"):
        lines.append("%s  %s" % (sha256_file(os.path.join(ACQ, r)), r))
open(os.path.join(ACQ, "SHA256SUMS"), "w").write("\n".join(lines) + "\n")

# ---- control-plane.json : what implementation produced the result
CURATED = ["source-manifest.json", "unresolved.json", "exceptions.json"]
cp = {"schema": "symoneural-control-plane/1.2",
      "build_stack": dict(sorted(LOCKED_STACK.items())),
      "record_schemas": {}, "record_provenance": {},
      "tool_sha256": {}, "superseded_tools": {},
      "census_note": (
        "METHOD A and METHOD B differ in discovery but BOTH call is_submodule(), "
        "which depends on `git rev-parse --show-superproject-working-tree`. The "
        "methods are therefore NOT fully independent. Their agreement remains "
        "meaningful evidence about discovery, but must not be read as two wholly "
        "independent confirmations."),
      "census_shared_primitive": "lib_acq.is_submodule -> git rev-parse --show-superproject-working-tree"}
for t in sorted(os.listdir(TOOLS)):
    if t.endswith(".py"):
        cp["tool_sha256"][t] = sha256_file(os.path.join(TOOLS, t))
sup = os.path.join(TOOLS, "superseded")
if os.path.isdir(sup):
    for t in sorted(os.listdir(sup)):
        cp["superseded_tools"][t] = {"sha256": sha256_file(os.path.join(sup, t)),
                                     "status": "SUPERSEDED-BY-V1.1"}
for r in sorted(set(RECORDS) | set(CURATED)):
    p = os.path.join(ACQ, r)
    if os.path.isfile(p):
        try: cp["record_schemas"][r] = json.load(open(p)).get("schema", "UNKNOWN")
        except Exception: cp["record_schemas"][r] = "UNPARSEABLE"
        cp["record_provenance"][r] = "CURATED" if r in CURATED else "SCANNER-DERIVED"
# Determinism is a property of SCANNER-DERIVED records only. Curated records are
# authored, not reproduced by re-running scanners, so claiming determinism for
# them would overstate what was actually proven.
cp["determinism_verified_scope"] = "SCANNER-DERIVED records only"
cp["determinism_scanner_derived_checked"] = sorted(RECORDS)
cp["determinism_curated_declared"] = sorted(r for r in CURATED
                                            if os.path.isfile(os.path.join(ACQ, r)))
cp["determinism_verified"] = bool(ok)
with open(os.path.join(ACQ, "control-plane.json"), "w") as f:
    json.dump(cp, f, indent=1, sort_keys=True); f.write("\n")
# SHA256SUMS again now that control-plane.json exists
lines = ["%s  %s" % (sha256_file(os.path.join(ACQ, r)), r)
         for r in sorted(os.listdir(ACQ)) if r.endswith(".json")]
open(os.path.join(ACQ, "SHA256SUMS"), "w").write("\n".join(lines) + "\n")
print("SHA256SUMS   : %d records" % len(lines))
print("tools hashed : %d" % len(cp["tool_sha256"]))
sys.exit(0 if ok else 1)
