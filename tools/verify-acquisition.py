#!/usr/bin/env python3
"""verify-acquisition.py - READ-ONLY verification of the acquisition control plane.

Compiles nothing, fetches nothing, and never writes to acquisition/. Every
documented check is implemented: the scanners are re-run into an isolated
temporary directory and the newly derived records are compared against the
authoritative ones by NORMALISED IDENTITY, not by count. A count can hide one
record removed and one added; an identity set cannot.

Exit 1 on FAIL. WARN never silently passes - it is always printed.
"""
import os, sys, json, tempfile, subprocess, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_acq import ROOT, ACQ, BOOT, LOCKED_STACK, git, load

TOOLS = os.path.dirname(os.path.abspath(__file__))
FAIL, WARN = [], []

def rescan(tmp):
    env = dict(os.environ, ACQ_OUT=tmp)
    # provider scan reads vendor-lock from the same isolated dir
    for s in ("scan-acquisition.py", "scan-dependencies.py", "scan-oe-providers.py",
              "scan-source-collisions.py"):
        r = subprocess.run([sys.executable, os.path.join(TOOLS, s)],
                           capture_output=True, text=True, env=env, cwd=ROOT)
        if r.returncode != 0:
            FAIL.append("rescan %s failed: %s" % (s, r.stderr.strip()[:200]))

def dep_ident(r):
    return (r["owner_runtime"], r["owner_component"], r["declaration_source"],
            r["declaration_path"], r["dependency"], r["declared_version"],
            r["resolved_identity"], r["classification"], r["scope"])

def ident(kind, rec):
    if kind == "source":    return (rec["source_path"], rec["commit_sha"], rec["worktree"])
    if kind == "submodule": return (rec["identity"], rec["commit_sha"], rec["configured_url"])
    if kind == "licence":   return (rec["owner_component"], rec["path"], rec["sha256"])
    if kind == "vendor":    return (rec["location"], rec["name"], rec["scope"])
    if kind == "provider_x": return None
    if kind == "dep":       return dep_ident(rec)
    if kind == "provider":  return (rec["logical_dependency"],
                                    tuple(sorted(p["location"] for p in rec["providers"])))
    if kind == "artifact":  return (rec["source_path"], tuple(rec["declared_capabilities"]))
    if kind == "collision": return (rec["logical_source"], rec["classification"],
                                    tuple(p["path"] for p in rec["providers"]))
    raise KeyError(kind)

SPEC = [("source-lock.json","components","source","source drift"),
        ("submodule-lock.json","entries","submodule","submodule drift"),
        ("dependency-graph.json","dependencies","dep","dependency drift"),
        ("vendor-lock.json","vendored","vendor","vendor drift"),
        ("license-inventory.json","files","licence","license drift"),
        ("provider-collisions.json","collisions","provider","provider drift"),
        ("artifact-plan.json","components","artifact","artifact-capability drift"),
        ("source-collisions.json","entries","collision","source-collision drift")]
RESULTS = {}
TOTALS = {}
RECON = {}
RECON_DETAIL = []
COMPLETE_FAIL = []
AGREE = []
DUP_URL = []
RESIDUE = []

def main():
    # ---- build-stack identity
    for name, sha in sorted(LOCKED_STACK.items()):
        d = os.path.join(BOOT, name)
        if not os.path.isdir(d):
            FAIL.append("build-stack missing: %s" % name); continue
        cur = git(d, "rev-parse", "HEAD")
        if cur != sha:
            FAIL.append("build-stack %s changed: %s != %s" % (name, cur[:12], sha[:12]))
    RESULTS["build-stack drift"] = "checked"

    # ---- hard source/recipe existence checks against authority
    sl = load("source-lock.json")
    for c in sl["components"]:
        p = os.path.join(ROOT, c["source_path"])
        if not os.path.isdir(p):
            FAIL.append("registered source DISAPPEARED: %s" % c["source_path"]); continue
        for k in ("recipe_path", "bbappend_path"):
            v = c[k]
            if v != "NOT-APPLICABLE" and not os.path.isfile(os.path.join(ROOT, v)):
                FAIL.append("registered %s DISAPPEARED: %s" % (k, v))
        # Ignored residue is still residue. oe-workdir / oe-logs / __pycache__ /
        # build/ inside an acquired tree means something wrote into pristine
        # source and .gitignore merely hid it. A FINDING, never a silent pass.
        ig = [l[3:] for l in git(p, "status", "--short", "--ignored").splitlines()
              if l.startswith("!!")]
        if ig:
            RESIDUE.append((c["source_path"], ig))
    if not sl["census"]["sets_identical"]:
        FAIL.append("repository census methods disagree")

    # ---- identity-level drift for every documented record
    tmp = tempfile.mkdtemp(prefix="symon-verify-")
    try:
        rescan(tmp)
        for fn, key, kind, label in SPEC:
            try:
                old = {ident(kind, r) for r in load(fn)[key]}
                new = {ident(kind, r) for r in load(fn, base=tmp)[key]}
            except Exception as e:
                FAIL.append("%s: comparison failed: %s" % (label, e))
                RESULTS[label] = "ERROR"; continue
            add, rem = new - old, old - new
            if not add and not rem:
                RESULTS[label] = "clean (%d identities)" % len(old)
            else:
                RESULTS[label] = "DRIFT +%d/-%d" % (len(add), len(rem))
                hard = kind in ("source", "submodule")
                msg = "%s: %d added, %d removed" % (label, len(add), len(rem))
                for x in sorted(add)[:2]: msg += "\n        + %s" % (x,)
                for x in sorted(rem)[:2]: msg += "\n        - %s" % (x,)
                (FAIL if hard else WARN).append(msg)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- INVARIANT: identity_count == record_count for every structured record
    for fn, key, kind, label in SPEC:
        try:
            recs = load(fn)[key]
            ids = {ident(kind, r) for r in recs}
            TOTALS[label] = len(recs)
            if len(ids) != len(recs):
                FAIL.append("identity key LOSSY for %s: %d records collapse to %d identities"
                            % (fn, len(recs), len(ids)))
        except Exception as e:
            FAIL.append("identity invariant check failed for %s: %s" % (fn, e))

    # ---- SECTION 2: completeness reconciliation, intent vs reality
    try:
        mf = load("source-manifest.json")["entries"]
    except Exception as e:
        FAIL.append("source-manifest.json unreadable: %s" % e); mf = []
    on_disk = {c["source_path"]: c for c in sl["components"]}
    by_comp = {}
    for c in sl["components"]:
        by_comp[(c["runtime"], c["component"])] = c
    declared = set()
    sub_by_owner = {}
    for e in load("submodule-lock.json")["entries"]:
        sub_by_owner.setdefault(e["owner_source_path"], []).append(e)
    lic_owners = {f["owner_component"] for f in load("license-inventory.json")["files"]}

    for m in mf:
        keyc = (m["runtime"], m["component"])
        c = by_comp.get(keyc)
        st = m["acquisition_state"]
        if st == "DEFERRED":
            state = "DEFERRED"
        elif m["intended_revision"] == "UNRESOLVED":
            state = "INTENT-UNRESOLVED"
        elif c is None:
            state = "MISSING"
        elif c["commit_sha"] != m["intended_revision"]:
            state = "PRESENT-REVISION-MISMATCH"
        else:
            state = "PRESENT-AT-INTENDED-REVISION"
        RECON[state] = RECON.get(state, 0) + 1
        RECON_DETAIL.append((state, m["runtime"], m["component"]))
        if c: declared.add(c["source_path"])
        if state in ("MISSING", "PRESENT-REVISION-MISMATCH", "INTENT-UNRESOLVED"):
            COMPLETE_FAIL.append("%s: %s/%s" % (state, m["runtime"], m["component"]))
        # an uninitialised submodule IS a missing source
        if c:
            for e in sub_by_owner.get(c["source_path"], []):
                if e["init_state"] != "AT-RECORDED-COMMIT":
                    COMPLETE_FAIL.append("submodule %s in %s/%s is %s"
                        % (e["submodule_path"], m["runtime"], m["component"], e["init_state"]))
            if c["component"] not in lic_owners:
                COMPLETE_FAIL.append("LICENCE-EVIDENCE-ABSENT: %s/%s"
                                     % (m["runtime"], m["component"]))
    for sp in sorted(set(on_disk) - declared):
        RECON["EXTRA-UNDECLARED"] = RECON.get("EXTRA-UNDECLARED", 0) + 1
        WARN.append("EXTRA / INTENT-UNDECLARED on disk: %s" % sp)

    # ---- SECTION 9d: a top-level upstream must not be acquired twice.
    # Two runtimes independently pulling the same upstream means two revisions
    # that can silently diverge. Currently zero such cases exist; this makes that
    # a rule rather than luck.
    byurl = {}
    for c in sl["components"]:
        u = (c["upstream_url"] or "UNKNOWN").lower().rstrip("/")
        if u.endswith(".git"): u = u[:-4]
        if u == "unknown": continue
        byurl.setdefault(u, []).append(c)
    DUP_URL.extend((u, v) for u, v in sorted(byurl.items()) if len(v) > 1)
    for u, v in DUP_URL:
        COMPLETE_FAIL.append("DUPLICATE top-level upstream URL in %d runtimes: %s (%s)"
            % (len({x["runtime"] for x in v}), u,
               ", ".join("%s/%s" % (x["runtime"], x["component"]) for x in v)))

    # ---- SECTION 6: report totals must equal verifier totals
    try:
        md = open(os.path.join(ROOT, "Symoneural-Runtime-Aquisition.md")).read()
        import re as _re
        claims = {
            "source drift": _re.search(r'\|\s*\*\*TOTAL\*\*\s*\|\s*\*\*(\d+)\*\*', md),
            "dependency drift": _re.search(r'manifests:\s*\*\*(\d+)\*\*', md),
            "submodule drift": _re.search(r'Entries:\s*\*\*(\d+)\*\*', md),
            "license drift": _re.search(r'Licence-bearing files:\s*\*\*(\d+)\*\*', md),
        }
        for label, m2 in claims.items():
            if not m2:
                WARN.append("report agreement: could not locate the %s total in the report" % label)
                continue
            claimed, actual = int(m2.group(1)), TOTALS.get(label)
            AGREE.append((label, claimed, actual, claimed == actual))
            if claimed != actual:
                FAIL.append("report/verifier DISAGREE on %s: report=%d verifier=%d"
                            % (label, claimed, actual))
    except FileNotFoundError:
        WARN.append("report agreement: report not generated yet")

    print("SyMoNeuRaL acquisition verification (read-only)")
    print("  components : %d" % len(sl["components"]))
    for _, _, _, label in SPEC:
        print("  %-28s %s" % (label + ":", RESULTS.get(label, "not run")))
    print("  %-28s %s" % ("build-stack drift:", RESULTS["build-stack drift"]))
    for w in WARN: print("  WARN: %s" % w)
    for f in FAIL: print("  FAIL: %s" % f)
    print("  duplicate top-level upstream URLs: %d (must be 0)" % len(DUP_URL))
    print("  acquired trees carrying ignored residue: %d" % len(RESIDUE))
    for sp, items in RESIDUE[:8]:
        print("     %-52s %s" % (sp.split("/source/")[-1], ", ".join(items[:3])))
    print("  -- completeness reconciliation --")
    for k in ("PRESENT-AT-INTENDED-REVISION","PRESENT-REVISION-MISMATCH","MISSING",
              "EXTRA-UNDECLARED","INTENT-UNRESOLVED","DEFERRED"):
        print("  %-30s %d" % (k+":", RECON.get(k, 0)))
    if AGREE:
        print("  -- report agreement --")
        for l,c2,a2,ok2 in AGREE:
            print("  %-30s report=%-6s verifier=%-6s %s" % (l+":", c2, a2, "OK" if ok2 else "MISMATCH"))
    for c2 in COMPLETE_FAIL[:10]: print("  COMPLETENESS-FAIL: %s" % c2)
    if len(COMPLETE_FAIL) > 10: print("  ... %d more completeness failures" % (len(COMPLETE_FAIL)-10))
    for sp,_ in RESIDUE: WARN.append("ignored residue in acquired tree: %s" % sp)
    verdict = "FAIL" if FAIL else ("PASS-WITH-WARNINGS" if WARN else "PASS")
    comp = "FAIL" if COMPLETE_FAIL else "PASS"
    print("  CONTROL-PLANE RESULT:      %s" % verdict)
    print("  ESTATE-COMPLETENESS RESULT: %s" % comp)
    return 1 if FAIL else 0

if __name__ == "__main__":
    sys.exit(main())
