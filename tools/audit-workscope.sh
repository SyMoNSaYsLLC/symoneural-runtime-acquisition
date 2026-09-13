#!/bin/bash
# audit-workscope.sh — the full pipeline audit for the SyMoNeuRaL estate.
#
# Answers one question per acquired source: did it become a symoneural-* package?
#
#   1 ACQUIRED   tree exists at its pinned SHA
#   2 RECORDED   row in source-manifest.json AND source-lock.json
#   3 RECIPE     a .bb in meta-symoneural inheriting symoneural-pristine AND a
#                real build class (cargo/cmake/meson/python_*/maturin/npm/autotools)
#   4 PACKAGED   at least one symoneural-<component>*.ipk in tmp/deploy/ipk
#
# Read-only. Starts no bitbake. Safe while a cooker is live.
# Usage:  bash audit-workscope.sh [--csv]
set -uo pipefail
ROOT=/home/google/SymonSaysLLC
cd "$ROOT" || { echo "cannot cd $ROOT"; exit 1; }
CSV=${1:-}

# ---------------------------------------------------------------- fd pressure
NF=$(cat /proc/sys/fs/file-nr 2>/dev/null | awk '{print $1}')
MX=$(cat /proc/sys/fs/file-max 2>/dev/null)
if [ -n "${NF:-}" ] && [ -n "${MX:-}" ]; then
  PCT=$(( NF * 100 / MX ))
  printf 'file descriptors: %s of %s in use (%s%%)\n' "$NF" "$MX" "$PCT"
  [ "$PCT" -gt 80 ] && echo "  WARNING: near the kernel ceiling — raise fs.file-max before trusting any build"
fi
echo

# ---------------------------------------------------------------- inventories
# ipks actually produced, estate-wide, base package names only
ls Symoneural-*/build/devtool-master/tmp/deploy/ipk/*/symoneural-*.ipk 2>/dev/null \
  | sed 's|.*/||; s/_.*//' \
  | sed -E 's/-(dbg|dev|src|staticdev|doc|locale.*|ptest)$//' \
  | sort -u > /tmp/aud-ipk.txt
# full ipk list, for counting per component
ls Symoneural-*/build/devtool-master/tmp/deploy/ipk/*/symoneural-*.ipk 2>/dev/null > /tmp/aud-ipk-full.txt

python3 - "$CSV" <<'PY'
import json, os, re, subprocess, sys, glob
csv = (len(sys.argv) > 1 and sys.argv[1] == "--csv")
ROOT = "/home/google/SymonSaysLLC"

def jload(p):
    try:
        return json.load(open(os.path.join(ROOT, "acquisition", p)))
    except Exception:
        return {}

lock = {c.get("component"): c for c in jload("source-lock.json").get("components", [])}
man  = {e.get("component"): e for e in jload("source-manifest.json").get("entries", [])}

ipk_base = set(open("/tmp/aud-ipk.txt").read().split())
ipk_all  = [l.strip() for l in open("/tmp/aud-ipk-full.txt") if l.strip()]

BUILD_CLASSES = ("cargo","cmake","meson","python_","maturin","npm","autotools",
                 "bin_package","go","setuptools")

# recipes: component name -> (path, inherits, srcrev, pv, symon_tree)
recipes = {}
for bb in glob.glob(os.path.join(ROOT, "meta-symoneural/recipes-*/*/*.bb")):
    if "/retired/" in bb:
        continue
    try:
        s = open(bb, encoding="utf-8", errors="replace").read()
    except OSError:
        continue
    pn = os.path.basename(bb).split("_")[0]
    inh = " ".join(re.findall(r"^inherit\s+(.*)$", s, re.M))
    srcrev = (re.findall(r'^SRCREV\s*=\s*"([^"]+)"', s, re.M) or [""])[0]
    pv     = (re.findall(r'^PV\s*=\s*"([^"]+)"', s, re.M) or [""])[0]
    tree   = (re.findall(r'^SYMON_TREE\s*=\s*"([^"]+)"', s, re.M) or [""])[0]
    recipes[pn] = dict(path=bb, inherit=inh, srcrev=srcrev, pv=pv, tree=tree)

def head(path):
    if not path or not os.path.isdir(path):
        return ""
    try:
        r = subprocess.run(["git","-C",path,"rev-parse","HEAD"],
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""

# acquired trees, from disk
trees = sorted(glob.glob(os.path.join(ROOT, "Symoneural-*/src/*/source/*")))
trees = [t for t in trees if os.path.isdir(t) and os.path.exists(os.path.join(t, ".git"))]

rows, stats = [], dict(acq=0, rec=0, rcp=0, pkg=0, ref=0)
for t in trees:
    rel  = os.path.relpath(t, ROOT)
    parts = rel.split(os.sep)
    runtime = parts[0].replace("Symoneural-", "")
    comp    = os.path.basename(t)
    stats["acq"] += 1

    m = man.get(comp, {}); l = lock.get(comp, {})
    recorded = bool(m) and bool(l)
    if recorded: stats["rec"] += 1
    refonly = "REFERENCE" in str(m.get("acquisition_state","")).upper() or \
              "REFERENCE" in str(m.get("kind","")).upper()
    if refonly: stats["ref"] += 1

    # match a recipe by the symoneural-<component> convention, then by SYMON_TREE
    pn = None
    for cand in ("symoneural-" + comp, "symoneural-" + comp.replace(".", "-").replace("_","-")):
        if cand in recipes: pn = cand; break
    if pn is None:
        for k, v in recipes.items():
            if v["tree"] and os.path.realpath(v["tree"]) == os.path.realpath(t):
                pn = k; break

    r = recipes.get(pn, {}) if pn else {}
    has_class = any(c in r.get("inherit","") for c in BUILD_CLASSES)
    is_stub   = bool(r) and not has_class
    if r and has_class: stats["rcp"] += 1

    h = head(t)
    pin = "?" if not (h and r.get("srcrev")) else ("ok" if h == r["srcrev"] else "MISMATCH")

    n_ipk = len([p for p in ipk_all
                 if pn and os.path.basename(p).startswith(pn + "_")
                 or pn and re.match(re.escape(pn) + r"-(dbg|dev|src|staticdev|doc)_", os.path.basename(p))])
    packaged = n_ipk > 0
    if packaged: stats["pkg"] += 1

    if refonly:              status = "REFERENCE-ONLY"
    elif packaged:           status = "DONE"
    elif is_stub:            status = "STUB — no build class"
    elif not r:              status = "NO RECIPE"
    elif not recorded:       status = "NOT IN CONTROL PLANE"
    else:                    status = "RECIPE, NEVER PACKAGED"

    rows.append((runtime, comp, h[:9], "y" if recorded else "-",
                 pn or "-", pin, "y" if has_class else ("stub" if r else "-"),
                 str(n_ipk), status))

if csv:
    print("runtime,component,head,recorded,recipe,pin,build_class,ipks,status")
    for r in rows: print(",".join(r))
else:
    w = [10, 26, 10, 4, 34, 9, 6, 5, 24]
    hdr = ("RUNTIME","COMPONENT","HEAD","REC","RECIPE","PIN","CLASS","IPK","STATUS")
    print("  ".join(h.ljust(x) for h, x in zip(hdr, w)))
    print("  ".join("-"*x for x in w))
    last = None
    for r in rows:
        if r[0] != last:
            if last is not None: print()
            last = r[0]
        print("  ".join(c.ljust(x)[:x] for c, x in zip(r, w)))

print()
print("=" * 78)
print(f"acquired trees            : {stats['acq']}")
print(f"recorded in control plane : {stats['rec']}   (manifest AND lock)")
print(f"recipe with a build class : {stats['rcp']}")
print(f"PACKAGED as symoneural-*  : {stats['pkg']}")
print(f"REFERENCE-ONLY (exempt)   : {stats['ref']}")
need = stats['acq'] - stats['ref']
pct = (stats['pkg'] * 100 // need) if need else 0
print(f"objective: {stats['pkg']} of {need} non-exempt components packaged  ({pct}%)")
print("=" * 78)
PY

echo
echo "--- ipk deploy dirs ---"
ls -d Symoneural-*/build/devtool-master/tmp/deploy/ipk 2>/dev/null | sed 's|/build.*||' | tr '\n' ' '; echo
echo "--- total symoneural-* ipks on disk: $(wc -l < /tmp/aud-ipk-full.txt) ---"
