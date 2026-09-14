#!/usr/bin/env python3
"""check-native-linkage.py - reconstruction v1.1 §69, the native linkage audit.

Audits every first-party / boundary native artifact the reconstruction names:

    libsymoneural-api      symoneural-api-util
    libsymoneural-llm      symoneural-llm
    libllama               libggml

For each it records, FROM THE BUILT ARTIFACT ON DISK (never from a recipe):
    SONAME, NEEDED, RUNPATH/RPATH, machine, exported symbol count

and it enforces the boundary rules the reconstruction states:

  libsymoneural-api depends on libc/POSIX only. Anything else in NEEDED means a
    dependency crept into a library that is supposed to be self-contained.
  libllama must IMPORT ggml, never contain it. llama.cpp vendors a copy of ggml
    under ggml/ and builds it by default; LLAMA_USE_SYSTEM_GGML=ON makes it link
    the canonical tree instead. The test that actually distinguishes the two is
    not the recipe flag but the symbol table: if any ggml_* symbol is DEFINED
    inside libllama there is a second, hidden copy of ggml in the estate, and the
    two can drift. Defined must be 0 and undefined must be > 0.
  No artifact may carry a RUNPATH into a build tree.
  libsymoneural-api and libsymoneural-llm stay INDEPENDENT: neither may appear in
    the other's NEEDED.

Artifacts that do not exist yet are reported NOT STARTED, never PASS.

  tools/check-native-linkage.py [--json out.json]
Exit 0 only if every existing artifact passes every rule that applies to it.
"""
import glob, json, os, re, subprocess, sys

ROOT = "/home/google/SymonSaysLLC"

def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout

def newest(pattern):
    c = sorted(glob.glob(pattern), key=os.path.getmtime)
    return c[-1] if c else None

def elf(path):
    d, h = sh("readelf", "-d", path), sh("readelf", "-h", path)
    return {
        "path": path,
        "machine": (re.search(r"Machine:\s+(.*)", h) or [None, "?"])[1].strip(),
        "soname": (re.findall(r"\(SONAME\)\s+Library soname: \[(.*?)\]", d) or [None])[0],
        "needed": re.findall(r"\(NEEDED\)\s+Shared library: \[(.*?)\]", d),
        "runpath": re.findall(r"\((?:RPATH|RUNPATH)\)\s+Library r(?:un)?path: \[(.*?)\]", d),
    }

def defined(path, pat):
    return [l.split()[-1] for l in sh("nm", "-D", "--defined-only", path).splitlines()
            if len(l.split()) >= 3 and l.split()[1] in "TDBRWiu" and re.match(pat, l.split()[-1])]

def undefined(path, pat):
    return [l.split()[-1] for l in sh("nm", "-D", "--undefined-only", path).splitlines()
            if l.split() and re.match(pat, l.split()[-1])]

# Audit the PACKAGED artifact, not the recipe's image/ directory.
#
# Two traps make image/ the wrong source. First, a task restored from sstate does
# NOT repopulate image/, so that directory can hold a genuinely old artifact while
# the package and the deployed rootfs are current - exactly what happened after the
# rack.c fix: Symoneural-API/.../image still carried subtree b1130376 with popen in
# it while the shipped library was already 898f4dec using posix_spawn. Second, a
# recipe is built under several runtimes' work trees (packagegroup-symoneural-api is
# pulled into the Ravencalc and CLI images too), so a glob hardcoded to one runtime
# can audit whichever copy happens to live there.
#
# The .ipk in the feed is what actually ships. Every feed of every runtime is searched
# and the newest package wins.
FEEDS = "Symoneural-*/build/devtool-master/tmp/deploy/ipk/*/%s"
TARGETS = [
    ("libsymoneural-api",   "symoneural-api_*.ipk",        "usr/lib/libsymoneural-api.so.*.*.*"),
    ("symoneural-api-util", "symoneural-api-util_*.ipk",   "usr/bin/symoneural-api-util"),
    ("libsymoneural-llm",   "symoneural-llm_*.ipk",        "usr/lib/libsymoneural-llm.so.*.*.*"),
    # two runtime packages carry the executables; a "symoneural-llm-*" glob would pick
    # whichever -dev/-dbg/-src ipk is newest and report the runtime as missing
    ("symoneural-llm-util",   "symoneural-llm-util_*.ipk",   "usr/bin/symoneural-llm-util"),
    ("symoneural-llm",        "symoneural-llm-python_*.ipk", "usr/bin/symoneural-llm"),
    ("libllama",            "libllama[0-9]_*.ipk",         "usr/lib/libllama.so.*.*.*"),
    ("libggml",             "symoneural-ggml_*.ipk",       "usr/lib/libggml-base.so.*.*.*"),
]

UNPACK = os.path.join(os.environ.get("TMPDIR", "/tmp"), "native-linkage-unpack")

def unpack(ipk):
    """Extract an .ipk (ar: debian-binary, control.tar.gz, data.tar.<zst|gz|xz>)."""
    d = os.path.join(UNPACK, os.path.basename(ipk)[:-4])
    if os.path.isdir(d):
        return d
    os.makedirs(d, exist_ok=True)
    members = sh("ar", "t", ipk).split()
    data = next((m for m in members if m.startswith("data.tar")), None)
    if not data:
        return None
    flag = {"zst": "--zstd", "gz": "-z", "xz": "-J", "bz2": "-j"}.get(data.rsplit(".", 1)[-1], "")
    rc = subprocess.run("ar p %s %s | tar %s -x -C %s" % (ipk, data, flag, d),
                        shell=True, capture_output=True).returncode
    return d if rc == 0 else None

def source_tree_of(root):
    """The committed subtree a first-party artifact was exported from. symoneural-
    firstparty ships it as <datadir>/<pn>/SOURCE-TREE, so the audit can say WHICH
    revision it measured instead of implying it measured HEAD."""
    for f in glob.glob(os.path.join(root, "usr/share/*/SOURCE-TREE")):
        return open(f).read().strip()
    return None

report, failures, missing = {}, [], []
for name, ipk_glob, inner in TARGETS:
    ipk = newest(FEEDS % ipk_glob)
    if not ipk:
        report[name] = {"state": "NOT STARTED", "reason": "no package matches %s in any feed" % ipk_glob}
        missing.append(name); continue
    root = unpack(ipk)
    p = newest(os.path.join(root, inner)) if root else None
    if not p:
        report[name] = {"state": "NOT STARTED", "reason": "%s holds no %s" % (os.path.basename(ipk), inner)}
        missing.append(name); continue
    e = elf(p); e["state"] = "BUILT"
    e["package"] = os.path.relpath(ipk, ROOT)
    e["exported_symbols"] = len(defined(p, r".*"))
    st = source_tree_of(root)
    if st:
        e["source_tree"] = st
        want = sh("git", "-C", ROOT, "rev-parse", "HEAD:" + st.split("HEAD:")[-1]).strip()
        e["source_tree_is_head"] = (st.split()[0] == want)
        if not e["source_tree_is_head"]:
            failures.append("%s: the PACKAGED artifact was built from subtree %s but "
                            "HEAD:%s is now %s - the package is STALE"
                            % (name, st.split()[0][:12], st.split("HEAD:")[-1], want[:12]))
    report[name] = e
    if e["runpath"] and any("SymonSaysLLC" in r or "/tmp/" in r for r in e["runpath"]):
        failures.append("%s: RUNPATH points into a build tree: %s" % (name, e["runpath"]))

api, llm = report.get("libsymoneural-api", {}), report.get("libsymoneural-llm", {})
if api.get("state") == "BUILT":
    extra = [n for n in api["needed"] if n not in ("libc.so.6", "ld-linux-x86-64.so.2")]
    api["rule_libc_only"] = "PASS" if not extra else "FAIL: also needs %s" % extra
    if extra: failures.append("libsymoneural-api is not libc-only: %s" % extra)
if llm.get("state") == "BUILT" and api.get("state") == "BUILT":
    crossed = [n for n in llm["needed"] if "symoneural-api" in n] + \
              [n for n in api["needed"] if "symoneural-llm" in n]
    llm["rule_independent_of_api"] = "PASS" if not crossed else "FAIL: %s" % crossed
    if crossed: failures.append("the API and LLM native libraries are not independent: %s" % crossed)

ll = report.get("libllama", {})
if ll.get("state") == "BUILT":
    d, u = defined(ll["path"], r"ggml_"), undefined(ll["path"], r"ggml_")
    ll["ggml_symbols_defined_inside"] = len(d)
    ll["ggml_symbols_imported"] = len(u)
    ok = len(d) == 0 and len(u) > 0
    ll["rule_no_embedded_ggml"] = ("PASS: imports %d ggml symbols, defines none" % len(u)) if ok else \
        ("FAIL: %d ggml_* symbols are DEFINED inside libllama - a hidden second copy" % len(d))
    if not ok: failures.append(ll["rule_no_embedded_ggml"])
    gg = report.get("libggml", {})
    if gg.get("state") == "BUILT":
        ll["links_shared_libggml"] = "PASS" if any(n.startswith("libggml") for n in ll["needed"]) \
            else "FAIL: libggml is absent from NEEDED"
        if not any(n.startswith("libggml") for n in ll["needed"]):
            failures.append("libllama does not link the shared libggml")
        gg["defines_ggml_symbols"] = len(defined(gg["path"], r"ggml_"))

print("native linkage audit (reconstruction v1.1 §69)\n")
for name, r in report.items():
    if r.get("state") != "BUILT":
        print("  %-22s NOT STARTED  (%s)" % (name, r["reason"].split(" matches ")[0])); continue
    print("  %s" % name)
    print("      package   %s" % r.get("package", "?"))
    print("      soname    %s   machine %s" % (r["soname"] or "-", r["machine"]))
    print("      needed    %s" % " ".join(r["needed"]))
    print("      runpath   %s" % (" ".join(r["runpath"]) or "-"))
    print("      exported  %d symbols" % r["exported_symbols"])
    if r.get("source_tree"):
        print("      built from %s  (== HEAD: %s)" % (r["source_tree"], r.get("source_tree_is_head")))
    for k, v in r.items():
        if k.startswith("rule_") or k.startswith("links_") or k.startswith("ggml_symbols") or k.startswith("defines_"):
            print("      %-24s %s" % (k, v))
if missing:
    print("\n  NOT STARTED: %s" % ", ".join(missing))
print("\nRESULT: %s" % ("PASS" if not failures else "FAIL"))
for f in failures:
    print("  - %s" % f)
if "--json" in sys.argv:
    out = sys.argv[sys.argv.index("--json") + 1]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"artifacts": report, "failures": failures, "not_started": missing},
              open(out, "w"), indent=1, sort_keys=True)
    print("wrote %s" % out)
sys.exit(1 if failures else 0)
