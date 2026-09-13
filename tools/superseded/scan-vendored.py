#!/usr/bin/env python3
"""Scan acquired SyMoNeuRaL sources for vendored/bundled third-party code.
Finds collisions (same component vendored in >1 place) and collects licence evidence.
NON-AUTHORITATIVE research artifact."""
import os, re, sys, json, hashlib
from collections import defaultdict

ROOT = "/home/google/SymonSaysLLC"
VENDOR_DIRS = {"vendor","vendored","third_party","thirdparty","3rdparty","external",
               "externals","extern","deps","subprojects","contrib","bundled"}
SKIP = {".git","node_modules","__pycache__",".github",".tox","test","tests","docs","doc"}
LICENSE_RE = re.compile(r'^(LICENSE|LICENCE|COPYING|NOTICE)', re.I)

def licences(path, limit=3):
    out=[]
    try:
        for e in sorted(os.listdir(path)):
            if LICENSE_RE.match(e):
                f=os.path.join(path,e)
                if os.path.isfile(f):
                    with open(f,'rb') as fh: b=fh.read()
                    out.append((e, hashlib.md5(b).hexdigest(), hashlib.sha256(b).hexdigest()))
                if len(out)>=limit: break
    except OSError: pass
    return out

findings=[]   # (runtime, component, vendor_root, vendored_name, path)
for rt in sorted(os.listdir(ROOT)):
    if not rt.startswith("Symoneural-"): continue
    srcroot=os.path.join(ROOT,rt,"src")
    if not os.path.isdir(srcroot): continue
    for dirpath,dirnames,filenames in os.walk(srcroot):
        dirnames[:]=[d for d in dirnames if d not in SKIP]
        base=os.path.basename(dirpath)
        if base.lower() in VENDOR_DIRS:
            rel=os.path.relpath(dirpath,srcroot)
            comp=rel.split(os.sep)[0] if os.sep in rel else rel
            for child in sorted(os.listdir(dirpath)):
                cp=os.path.join(dirpath,child)
                if not os.path.isdir(cp) or child in SKIP: continue
                findings.append({
                    "runtime":rt.replace("Symoneural-",""),
                    "component":comp,
                    "vendor_root":rel,
                    "name":child,
                    "path":os.path.relpath(cp,ROOT),
                    "licences":licences(cp),
                })
            dirnames[:]=[]   # don't descend further into a vendor dir

# collisions: same vendored name appearing in >1 distinct component
byname=defaultdict(list)
for f in findings: byname[f["name"].lower()].append(f)
collisions={k:v for k,v in byname.items()
            if len({(x["runtime"],x["component"]) for x in v})>1}

json.dump({"findings":findings,"collisions":collisions},
          open(sys.argv[1],"w"), indent=1)
print("vendored dirs found : %d" % len(findings))
print("distinct names      : %d" % len(byname))
print("COLLISIONS          : %d" % len(collisions))
