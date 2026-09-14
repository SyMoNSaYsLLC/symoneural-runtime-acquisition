#!/bin/bash
# audit-workscope.sh — the full pipeline audit for the SyMoNeuRaL estate.
#
# Two questions per acquired source, both answered from disk:
#   is its source IN THIS REPOSITORY at its pin, and did it become a symoneural-* package?
#
#   0 COMMITTED  tree at HEAD:<source_path>; hash- or listing-verified against the
#                lock (tools/ingest-tree verify - no pin or upstream access needed)
#   1 ACQUIRED   the pin (moved .git in .gitpins/, or the tree's own .git) is at commit_sha
#   2 RECORDED   row in source-manifest.json AND source-lock.json
#   3 RECIPE     a .bb in meta-symoneural inheriting symoneural-pristine AND a
#                real build class (cargo/cmake/meson/python_*/maturin/npm/autotools)
#   4 PACKAGED   tmp/pkgdata/*/<pn> exists - do_package ran for the recipe. Keyed on
#                pkgdata, NOT the ipk filename: debian.bbclass renames openblas's
#                package to libopenblas0, so a filename match under-counts.
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

# stage 0, once for every component; the tool reads HEAD and the lock only
AUD=$(mktemp "${TMPDIR:-/tmp}/aud-committed.XXXXXX") || exit 1
python3 tools/ingest-tree verify --all > "$AUD" 2>&1
echo "stage 0 (tools/ingest-tree verify --all) rc=$?"
echo

python3 - "$CSV" "$AUD" <<'PY'
import json, os, re, subprocess, sys, glob
csv = (len(sys.argv) > 1 and sys.argv[1] == "--csv")
AUD = sys.argv[2]
ROOT = "/home/google/SymonSaysLLC"

def jload(p):
    try:
        return json.load(open(os.path.join(ROOT, "acquisition", p)))
    except Exception:
        return {}

lock_l = jload("source-lock.json").get("components", [])
lock = {c.get("component"): c for c in lock_l}
man  = {e.get("component"): e for e in jload("source-manifest.json").get("entries", [])}

# component state: the ONE machine-readable record of TARGET / REFERENCE_ONLY /
# RETIRED_TO_PROVIDER / DEFERRED (acquisition/component-state.json). Non-TARGET
# rows are exempt from package proof BY RECORDED RULING; the audit never
# special-cases a name.
cstate = {r["component"]: r for r in jload("component-state.json").get("components", [])}
refonly = {c for c, r in cstate.items() if r.get("state") != "TARGET"}

# stage 0 results
committed = {}
for line in open(AUD, errors="replace"):
    parts = line.split()
    if len(parts) >= 3 and parts[0] in lock:
        m = re.search(r"·\s+\d+ files ·\s+(\S+)", line)
        committed[parts[0]] = m.group(1) if m else "?"

BUILD_CLASSES = ("cargo","cmake","meson","python_","maturin","npm","autotools",
                 "bin_package","go","setuptools")

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

def git_head(gitdir=None, worktree=None):
    cmd = ["git"]
    if gitdir:
        cmd += ["--git-dir=" + gitdir, "--work-tree=/"]
    elif worktree:
        cmd += ["-C", worktree]
    cmd += ["rev-parse", "HEAD"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""

def pins_dir(sp):
    return "/".join(sp.split("/")[:3]) + "/.gitpins"

# pkgdata: PN-level file per packaged recipe, under any machine dir
pkgdata = {}
for f in glob.glob(os.path.join(ROOT, "Symoneural-*/build/devtool-master/tmp/pkgdata/*/*")):
    if os.path.isfile(f):
        pkgdata.setdefault(os.path.basename(f), []).append(f)

def packages_of(pn):
    n = 0
    for f in pkgdata.get(pn, []):
        try:
            for line in open(f, errors="replace"):
                if line.startswith("PACKAGES:"):
                    n = max(n, len(line.split(":", 1)[1].split()))
        except OSError:
            pass
    return n

# rows: every lock component, plus any on-disk source dir the lock does not know
rows, per_rt = [], {}
seen_paths = set()
def add_row(runtime, comp, sp, in_lock):
    l = lock.get(comp, {}); m = man.get(comp, {})
    st = per_rt.setdefault(runtime, dict(total=0, committed=0, packaged=0, exempt=0))
    st["total"] += 1
    recorded = bool(m) and bool(l)
    is_ref = comp in refonly
    if is_ref: st["exempt"] += 1

    cstat = committed.get(comp, "-" if in_lock else "NOT-IN-LOCK")
    is_committed = cstat == "VERIFIED" or cstat.startswith("LISTING-VERIFIED")
    if is_committed: st["committed"] += 1

    pin = l.get("pins_path") or os.path.join(pins_dir(sp), comp + ".git")
    if os.path.isdir(os.path.join(ROOT, pin)):
        head = git_head(gitdir=os.path.join(ROOT, pin))
    elif os.path.exists(os.path.join(ROOT, sp, ".git")):
        head = git_head(worktree=os.path.join(ROOT, sp))
    else:
        head = ""
    acquired = bool(head) and head == l.get("commit_sha", "\0")

    pn = None
    for cand in ("symoneural-" + comp, "symoneural-" + comp.replace(".", "-").replace("_", "-")):
        if cand in recipes: pn = cand; break
    if pn is None:
        for k, v in recipes.items():
            if v["tree"] and os.path.realpath(v["tree"]) == os.path.realpath(os.path.join(ROOT, sp)):
                pn = k; break
    r = recipes.get(pn, {}) if pn else {}
    has_class = any(c in r.get("inherit", "") for c in BUILD_CLASSES)
    is_stub = bool(r) and not has_class
    pinok = "?" if not (head and r.get("srcrev")) else ("ok" if head == r["srcrev"] else "MISMATCH")

    packaged = bool(pn) and pn in pkgdata
    n_pkg = packages_of(pn) if packaged else 0
    if packaged: st["packaged"] += 1

    if is_ref:               status = cstate[comp]["state"] + (" -> " + cstate[comp]["provider"] if cstate[comp].get("provider") else "")
    elif packaged:           status = "DONE"
    elif is_stub:            status = "STUB — no build class"
    elif not r:              status = "NO RECIPE"
    elif not recorded:       status = "NOT IN CONTROL PLANE"
    else:                    status = "RECIPE, NEVER PACKAGED"

    rows.append((runtime, comp, cstat, head[:9] if head else "-", "ok" if acquired else "-",
                 "y" if recorded else "-", pn or "-", pinok, "y" if has_class else ("stub" if r else "-"),
                 str(n_pkg), status))

for c in sorted(lock_l, key=lambda c: (c["runtime"], c["component"])):
    seen_paths.add(c["source_path"])
    add_row(c["runtime"], c["component"], c["source_path"], True)
for t in sorted(glob.glob(os.path.join(ROOT, "Symoneural-*/src/*/source/*"))):
    rel = os.path.relpath(t, ROOT)
    if not os.path.isdir(t) or rel in seen_paths or any(rel.startswith(p + "/") for p in seen_paths):
        continue
    add_row(rel.split("/")[0].replace("Symoneural-", ""), os.path.basename(t), rel, False)

if csv:
    print("runtime,component,committed,head,acquired,recorded,recipe,pin,build_class,packages,status")
    for r in rows: print(",".join(r))
else:
    w = [10, 26, 36, 10, 4, 4, 32, 9, 6, 4, 24]
    hdr = ("RUNTIME","COMPONENT","COMMITTED","HEAD","ACQ","REC","RECIPE","PIN","CLASS","PKGS","STATUS")
    print("  ".join(h.ljust(x) for h, x in zip(hdr, w)))
    print("  ".join("-"*x for x in w))
    last = None
    for r in rows:
        if r[0] != last:
            if last is not None:
                s = per_rt[last]
                print("  %s: sources committed %d/%d · packaged %d/%d" % (last, s["committed"], s["total"], s["packaged"], s["total"] - s["exempt"]))
                print()
            last = r[0]
        print("  ".join(c.ljust(x)[:x] for c, x in zip(r, w)))
    if last is not None:
        s = per_rt[last]
        print("  %s: sources committed %d/%d · packaged %d/%d" % (last, s["committed"], s["total"], s["packaged"], s["total"] - s["exempt"]))

tot = len(lock_l)
ver = sum(1 for c in lock if committed.get(c) == "VERIFIED")
lst = sum(1 for c in lock if str(committed.get(c, "")).startswith("LISTING-VERIFIED"))
pend = tot - ver - lst
pkg = sum(s["packaged"] for s in per_rt.values())
exempt = sum(s["exempt"] for s in per_rt.values())
print()
print("=" * 78)
print("sources committed  : %d of %d   (verified %d · listing-verified %d · pending %d)" % (ver + lst, tot, ver, lst, pend))
print("components packaged: %d of %d   (%d exempt by recorded ruling: %s)" % (pkg, tot - exempt, exempt, ", ".join(sorted(refonly)) or "none"))
print("=" * 78)
PY
rm -f "$AUD"
