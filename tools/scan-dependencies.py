#!/usr/bin/env python3
"""scan-dependencies.py - dependency graph, vendor register, licence inventory,
artifact capabilities. READ-ONLY, deterministic, NO arbitrary depth limits.

Classification comes from the DECLARING MANIFEST. A lockfile establishes
resolution, not architectural directness, so a Cargo.lock entry with no source
URL is WORKSPACE-LOCAL - never DIRECT.
"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_acq import ROOT, components, dump, md5_file, sha256_file, SKIP_NAMES, is_component_submodule

VENDOR_DIRS = {"vendor","vendored","third_party","thirdparty","3rdparty","external",
               "externals","extern","deps","subprojects","contrib","bundled","_vendor"}
INLINE = {"ply","bs4","simplediff","progressbar","pyinotify","six","packaging",
          "nlohmann","cpp-httplib","fmt","spdlog","gtest","googletest","stb","xxhash",
          "array_api_compat","array_api_extra","catch2","miniz"}
# Meson's subprojects/packagefiles holds PATCH/OVERLAY material applied onto
# downloaded wraps (.patch files and per-package overlay dirs). It is not a
# vendored upstream project and must not be recorded as one.
NOT_VENDOR = {"packagefiles"}
LIC = re.compile(r'^(LICEN[CS]E|COPYING|NOTICE|COPYRIGHT)', re.I)
TESTY = re.compile(r'(^|/)(tests?|testing|_test|benchmarks?)(/|$)', re.I)
DOCCY = re.compile(r'(^|/)(docs?|documentation|examples?)(/|$)', re.I)

def scope_for(relpath, hint=None):
    if hint: return hint
    if "_vendor" in relpath.split(os.sep): return "PRIVATE-VENDORED"
    if TESTY.search(relpath): return "TEST-ONLY"
    if DOCCY.search(relpath): return "DOC-ONLY"
    return "UNKNOWN"

deps, vend, lics, arts = [], [], [], []
reclassified_submodule = []   # vendor candidates that are really git submodules
_vend_seen = set()   # a directory may match BOTH the vendor-dir rule and
                     # the inline-name rule; it is still one finding.

def D(rt, comp, name, cls, ver, url, ev, scope, declpath=None):
    """declpath distinguishes the SAME package declared at DIFFERENT positions.
    npm nests one package at many node_modules paths, sometimes at different
    versions; collapsing the path made those records share one identity and hid
    version changes from the verifier."""
    deps.append({"owner_runtime": rt, "owner_component": comp, "dependency": name,
                 "declaration_path": declpath or name,
                 "classification": cls, "scope": scope,
                 "declared_version": ver or "UNKNOWN",
                 "resolved_identity": url or "UNKNOWN",
                 "upstream_url": url or "UNKNOWN", "declaration_source": ev})

for c in components():
    rt, comp, path = c["runtime"], c["component"], c["abspath"]
    caps, native = set(), 0
    for dp, dn, fn in os.walk(path):
        dn[:] = sorted(d for d in dn if d not in SKIP_NAMES)
        rel = "" if dp == path else os.path.relpath(dp, path)
        base = os.path.basename(dp)
        depth = 0 if not rel else rel.count(os.sep) + 1

        for f in sorted(fn):
            fp, ev = os.path.join(dp, f), os.path.join(rel, f) if rel else f
            if f.endswith((".c",".cc",".cpp",".cxx",".pyx",".rs")): native += 1
            # A licence may be a FILE named LICENSE/COPYING/... or a FILE INSIDE a
            # directory named License/ whose members are named for the licence
            # itself (sv2-spec ships License/BSD-3-Clause and License/CC0-1.0).
            in_lic_dir = LIC.match(os.path.basename(dp) or "")
            if LIC.match(f) or in_lic_dir:
                try:
                    if os.path.getsize(fp) <= 1_000_000:
                        lics.append({"owner_runtime": rt, "owner_component": comp,
                            "path": ev, "sha256": sha256_file(fp), "md5": md5_file(fp),
                            "apparent_scope": "TOP-LEVEL" if depth == 0 else "NESTED/DEPENDENCY",
                            "declared_identifier": "UNRESOLVED", "status": "UNRESOLVED"})
                except OSError: pass
            try:
                if f == ".gitmodules":
                    t = open(fp, encoding="utf-8", errors="ignore").read()
                    for m in re.finditer(r'\[submodule "([^"]+)"\](.*?)(?=\[submodule|\Z)', t, re.S):
                        pm = re.search(r'path\s*=\s*(\S+)', m.group(2))
                        um = re.search(r'url\s*=\s*(\S+)', m.group(2))
                        D(rt, comp, pm.group(1) if pm else m.group(1), "SUBMODULE", None,
                          um.group(1) if um else None, ev,
                          scope_for(pm.group(1) if pm else rel))
                elif f == "Cargo.toml":
                    t = open(fp, encoding="utf-8", errors="ignore").read()
                    for sec, sc in (("dependencies","RUNTIME/SHIP"),
                                    ("build-dependencies","BUILD-ONLY"),
                                    ("dev-dependencies","DEV-ONLY")):
                        m = re.search(r'^\[%s\]\n(.*?)(?=^\[|\Z)' % re.escape(sec), t, re.S|re.M)
                        if not m: continue
                        for dm in re.finditer(r'^([A-Za-z0-9_\-]+)\s*=', m.group(1), re.M):
                            D(rt, comp, dm.group(1), "DIRECT-DECLARED", None, None,
                              ev+" ["+sec+"]", sc)
                    if "cdylib" in t: caps.add("RUST-CDYLIB")
                    if re.search(r'^\[\[bin\]\]', t, re.M): caps.add("EXECUTABLE")
                    if re.search(r'^\[lib\]', t, re.M): caps.add("RUST-RLIB")
                elif f == "Cargo.lock":
                    t = open(fp, encoding="utf-8", errors="ignore").read()
                    for blk in t.split("[[package]]")[1:]:
                        n = re.search(r'^name = "(.+)"', blk, re.M)
                        v = re.search(r'^version = "(.+)"', blk, re.M)
                        s = re.search(r'^source = "(.+)"', blk, re.M)
                        if not (n and v): continue
                        if not s:
                            cls, url = "WORKSPACE-LOCAL", None   # NOT "DIRECT"
                        elif s.group(1).startswith("registry+"):
                            cls, url = "PACKAGE-MANAGED", s.group(1)
                        else:
                            cls, url = "BUILD-FETCH", s.group(1)
                        D(rt, comp, n.group(1), cls, v.group(1), url, ev, scope_for(rel))
                elif f == "package.json":
                    caps.add("NODE-BUNDLE")
                    try: j = json.load(open(fp, encoding="utf-8", errors="ignore"))
                    except Exception: j = {}
                    for k, sc in (("dependencies","RUNTIME/SHIP"),
                                  ("devDependencies","DEV-ONLY"),
                                  ("peerDependencies","RUNTIME/SHIP"),
                                  ("optionalDependencies","UNKNOWN")):
                        for dn_, dv in (j.get(k) or {}).items():
                            D(rt, comp, dn_, "DIRECT-DECLARED", dv, None, ev+" ["+k+"]", sc)
                elif f in ("package-lock.json",):
                    try: j = json.load(open(fp, encoding="utf-8", errors="ignore"))
                    except Exception: j = {}
                    for k2, v2 in (j.get("packages") or {}).items():
                        if not k2: continue
                        sc = "DEV-ONLY" if v2.get("dev") else ("TEST-ONLY"
                             if TESTY.search(k2) else "UNKNOWN")
                        D(rt, comp, k2.split("node_modules/")[-1], "PACKAGE-MANAGED",
                          v2.get("version"), v2.get("resolved"), ev, sc, declpath=k2)
                elif f == "pyproject.toml":
                    caps.add("PYTHON-PACKAGE")
                    t = open(fp, encoding="utf-8", errors="ignore").read()
                    bs = re.search(r'\[build-system\].*?requires\s*=\s*\[(.*?)\]', t, re.S)
                    if bs:
                        for d in re.findall(r'"([^"]+)"', bs.group(1)):
                            D(rt, comp, d, "DIRECT-DECLARED", None, None,
                              ev+" [build-system]", "BUILD-ONLY")
                    pr = re.search(r'^dependencies\s*=\s*\[(.*?)\]', t, re.S|re.M)
                    if pr:
                        for d in re.findall(r'"([^"]+)"', pr.group(1)):
                            D(rt, comp, d, "DIRECT-DECLARED", None, None,
                              ev+" [project.dependencies]", "RUNTIME/SHIP")
                    # optional-dependencies holds SEVERAL named extras groups and the
                    # same package legitimately appears in more than one. The group
                    # name is part of the declaration identity, not noise.
                    for om in re.finditer(r'^\[project\.optional-dependencies\](.*?)(?=^\[[a-z]|\Z)', t, re.S|re.M):
                        for gm in re.finditer(r'^\s*([A-Za-z0-9_\-\.]+)\s*=\s*\[(.*?)\]',
                                              om.group(1), re.S|re.M):
                            grp = gm.group(1)
                            for d in re.findall(r'"([^"]+)"', gm.group(2)):
                                D(rt, comp, d, "DIRECT-DECLARED", None, None,
                                  ev+" [optional-dependencies."+grp+"]", "UNKNOWN",
                                  declpath=grp+"::"+d)
                elif f == "setup.py":
                    caps.add("PYTHON-PACKAGE")
                elif f.endswith(".wrap") and "subprojects" in dp:
                    t = open(fp, encoding="utf-8", errors="ignore").read()
                    u = re.search(r'(?:url|source_url)\s*=\s*(\S+)', t)
                    r = re.search(r'revision\s*=\s*(\S+)', t)
                    D(rt, comp, f[:-5], "BUILD-FETCH", r.group(1) if r else None,
                      u.group(1) if u else None, ev, scope_for(rel))
                elif f == "meson.build":
                    t = open(fp, encoding="utf-8", errors="ignore").read()
                    if "shared_library" in t or re.search(r'\blibrary\s*\(', t):
                        caps.add("SHARED-LIBRARY")
                    if re.search(r'\bexecutable\s*\(', t): caps.add("EXECUTABLE")
                elif f == "CMakeLists.txt":
                    t = open(fp, encoding="utf-8", errors="ignore").read()
                    # one CMakeLists may declare the same target more than once in
                    # different conditional branches; the occurrence ordinal keeps
                    # those distinct declarations distinguishable.
                    for i, m in enumerate(re.finditer(
                            r'(FetchContent_Declare|ExternalProject_Add)\s*\(\s*([A-Za-z0-9_\-]+)', t)):
                        D(rt, comp, m.group(2), "BUILD-FETCH", None, None,
                          ev+" ["+m.group(1)+"]", scope_for(rel),
                          declpath="%s#%d" % (m.group(2), i))
                    if depth == 0:
                        if re.search(r'add_library\s*\(', t): caps.add("STATIC-LIBRARY|SHARED-LIBRARY")
                        if re.search(r'add_executable\s*\(', t): caps.add("EXECUTABLE")
                elif f in ("WORKSPACE","WORKSPACE.bazel","MODULE.bazel"):
                    D(rt, comp, "<bazel-workspace>", "BUILD-FETCH", None, None, ev, "BUILD-ONLY")
            except Exception:
                pass

        if base.lower() in VENDOR_DIRS:
            for ch in sorted(dn):
                cp = os.path.join(dp, ch)
                lr = os.path.relpath(cp, path)
                if cp in _vend_seen or ch.lower() in NOT_VENDOR: continue
                _vend_seen.add(cp)
                # A path that is itself a git work tree is a SUBMODULE, not a
                # vendored copy. It already has its own lock entry, upstream URL
                # and SHA; recording it again under VENDORED double-counts one
                # source copy under two classifications.
                if is_component_submodule(cp):
                    reclassified_submodule.append({
                        "owning_upstream": "%s/%s" % (rt, comp),
                        "owner_source_path": c["source_path"],
                        "location": os.path.relpath(cp, ROOT), "relpath": lr,
                        "name": ch, "reclassified_from": "VENDORED",
                        "reclassified_to": "SUBMODULE",
                        "reason": "path is a recorded submodule (in-tree .git or lock row); see submodule-lock.json"})
                    continue
                vend.append({"owning_upstream": "%s/%s" % (rt, comp),
                    "owner_source_path": c["source_path"],
                    "location": os.path.relpath(cp, ROOT), "relpath": lr, "name": ch,
                    "version": "UNKNOWN", "upstream_project": "UNKNOWN",
                    "scope": scope_for(lr),
                    "licence_evidence": sorted(x for x in os.listdir(cp) if LIC.match(x)) or [],
                    "decision": "UNRESOLVED"})
        elif base.lower() in INLINE and dp not in _vend_seen \
             and not is_component_submodule(dp) and (
             any(x == "__init__.py" for x in fn)
             or any(x.endswith((".h",".hpp",".c",".cpp")) for x in fn)):
            _vend_seen.add(dp)
            vend.append({"owning_upstream": "%s/%s" % (rt, comp),
                "owner_source_path": c["source_path"],
                "location": os.path.relpath(dp, ROOT), "relpath": rel, "name": base,
                "version": "UNKNOWN", "upstream_project": "UNKNOWN",
                "scope": scope_for(rel),
                "licence_evidence": sorted(x for x in fn if LIC.match(x)) or [],
                "decision": "UNRESOLVED"})

    if "PYTHON-PACKAGE" in caps and native > 0: caps.add("PYTHON-EXTENSION")
    arts.append({"runtime": rt, "component": comp, "source_path": c["source_path"],
                 "declared_capabilities": sorted(caps) or ["UNKNOWN"],
                 "native_source_files": native, "symoneural_decision": "NOT-YET-DECIDED"})

deps.sort(key=lambda x: (x["owner_runtime"], x["owner_component"],
                         x["declaration_source"], x["declaration_path"],
                         x["dependency"], x["declared_version"],
                         x["resolved_identity"], x["classification"], x["scope"]))
vend.sort(key=lambda x: x["location"])
lics.sort(key=lambda x: (x["owner_component"], x["path"]))
arts.sort(key=lambda x: x["source_path"])

dump({"schema":"symoneural-dependency-graph/2","dependencies":deps}, "dependency-graph.json")
reclassified_submodule.sort(key=lambda x: x["location"])
dump({"schema":"symoneural-vendor-lock/3",
      "note":"A vendor candidate whose path is itself a git work tree is recorded as "
             "SUBMODULE in submodule-lock.json, not here. Those reclassifications are "
             "listed under reclassified_as_submodule so the correction is visible "
             "rather than appearing as a silent count reduction.",
      "reclassified_as_submodule": reclassified_submodule,
      "vendored":vend}, "vendor-lock.json")
dump({"schema":"symoneural-license-inventory/2",
      "note":"LICENSE expression and LIC_FILES_CHKSUM coverage are separate concepts. "
             "This is drift evidence, not a licensing conclusion.","files":lics},
     "license-inventory.json")
dump({"schema":"symoneural-artifact-plan/2",
      "note":"Declared upstream capability only. No SyMoNeuRaL artifact decision here.",
      "components":arts}, "artifact-plan.json")

from collections import Counter
print("dependencies %d %s" % (len(deps), dict(Counter(d["classification"] for d in deps))))
print("scopes         %s" % dict(Counter(d["scope"] for d in deps)))
print("vendored %d, licences %d, artifacts %d" % (len(vend), len(lics), len(arts)))
