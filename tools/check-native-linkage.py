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

W = "Symoneural-%s/build/devtool-master/tmp/work/*/%s/*/image"
TARGETS = [
    ("libsymoneural-api",  W % ("API", "symoneural-api")       + "/usr/lib/libsymoneural-api.so.*.*.*"),
    ("symoneural-api-util",W % ("API", "symoneural-api")       + "/usr/bin/symoneural-api-util"),
    ("libsymoneural-llm",  W % ("LLM", "symoneural-llm*")      + "/usr/lib/libsymoneural-llm.so.*.*.*"),
    ("symoneural-llm",     W % ("LLM", "symoneural-llm*")      + "/usr/bin/symoneural-llm*"),
    ("libllama",           W % ("LLM", "symoneural-llama-cpp") + "/usr/lib/libllama.so.*.*.*"),
    ("libggml",            W % ("LLM", "symoneural-ggml")      + "/usr/lib/libggml-base.so.*.*.*"),
]

report, failures, missing = {}, [], []
for name, pattern in TARGETS:
    p = newest(pattern)
    if not p:
        report[name] = {"state": "NOT STARTED", "reason": "no built artifact matches %s" % pattern}
        missing.append(name); continue
    e = elf(p); e["state"] = "BUILT"
    e["exported_symbols"] = len(defined(p, r".*"))
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
    print("      path      %s" % r["path"].replace(ROOT + "/", ""))
    print("      soname    %s   machine %s" % (r["soname"] or "-", r["machine"]))
    print("      needed    %s" % " ".join(r["needed"]))
    print("      runpath   %s" % (" ".join(r["runpath"]) or "-"))
    print("      exported  %d symbols" % r["exported_symbols"])
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
