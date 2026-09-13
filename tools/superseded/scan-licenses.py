#!/usr/bin/env python3
"""scan-licenses.py - find EVERY licence-bearing file inside each acquired source
tree and compare it against what the curated recipe declares in LIC_FILES_CHKSUM.

Catches the OpenBLAS class of defect: a tree whose top-level LICENSE is BSD-3 but
which vendors LAPACK, LAPACKE, ReLAPACK and the netlib BLAS reference, each under
its own terms. Declaring only the top-level file understates the licence surface.

Emits md5 (for LIC_FILES_CHKSUM) and sha256 (for the source lock) separately.
NON-AUTHORITATIVE: run on the reference machine before any release claim.
"""
import os, re, sys, json, hashlib, argparse

ROOT = "/home/google/SymonSaysLLC"
LIC_RE  = re.compile(r'^(LICEN[CS]E|COPYING|NOTICE|COPYRIGHT)', re.I)
SKIPDIR = {".git", "node_modules", "__pycache__"}

def digests(p):
    b = open(p, "rb").read()
    return hashlib.md5(b).hexdigest(), hashlib.sha256(b).hexdigest()

def tree_licences(root):
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIPDIR]
        for f in fn:
            if LIC_RE.match(f):
                p = os.path.join(dp, f)
                if os.path.isfile(p) and os.path.getsize(p) < 1_000_000:
                    try:
                        m, s = digests(p)
                        out.append({"file": os.path.relpath(p, root), "md5": m, "sha256": s})
                    except OSError:
                        pass
    return sorted(out, key=lambda x: x["file"])

def declared(recipe):
    try:
        t = open(recipe, encoding="utf-8", errors="ignore").read()
    except OSError:
        return set()
    m = re.search(r'LIC_FILES_CHKSUM\s*=\s*"(.*?)"', t, re.S)
    return set(re.findall(r'md5=([0-9a-f]{32})', m.group(1))) if m else set()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write full results here")
    a = ap.parse_args()

    results, gaps = {}, 0
    for rt in sorted(os.listdir(ROOT)):
        if not rt.startswith("Symoneural-"):
            continue
        srcroot = os.path.join(ROOT, rt, "src")
        wsr = os.path.join(ROOT, rt, "build", "devtool-workspace", "recipes")
        if not os.path.isdir(srcroot):
            continue
        for cat in sorted(os.listdir(srcroot)):
            sd = os.path.join(srcroot, cat, "source")
            if not os.path.isdir(sd):
                continue
            for comp in sorted(os.listdir(sd)):
                cp = os.path.join(sd, comp)
                if not os.path.isdir(cp):
                    continue
                lics = tree_licences(cp)
                # find the recipe whose bbappend points at this tree
                decl = set()
                rname = None
                if os.path.isdir(wsr):
                    for r in os.listdir(wsr):
                        ap_ = os.path.join(ROOT, rt, "build", "devtool-workspace",
                                           "appends", r + "_git.bbappend")
                        if os.path.isfile(ap_) and cp in open(ap_).read():
                            rname = r
                            decl = declared(os.path.join(wsr, r, r + "_git.bb"))
                            break
                found = {l["md5"] for l in lics}
                missing = [l for l in lics if l["md5"] not in decl]
                key = "%s/%s" % (rt.replace("Symoneural-", ""), comp)
                results[key] = {"recipe": rname, "licence_files": len(lics),
                                "declared": len(decl), "undeclared": missing}
                if rname and missing:
                    gaps += 1
                    print("GAP  %-34s %2d licence files, %d declared, %d UNDECLARED"
                          % (key, len(lics), len(decl), len(missing)))
                    for m in missing[:6]:
                        print("       %-46s md5=%s" % (m["file"], m["md5"]))
    print("\n%d components have undeclared licence files." % gaps)
    if a.json:
        json.dump(results, open(a.json, "w"), indent=1)

if __name__ == "__main__":
    main()
