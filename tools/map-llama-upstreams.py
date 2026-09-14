#!/usr/bin/env python3
"""map-llama-upstreams.py - L0: what the pinned llama.cpp IS made of, from disk.

Answers, with evidence paths: the llama.cpp pin and its tags; the ggml revision
it embeds (scripts/sync-ggml.last) and whether the canonical ggml tree at that
revision is present and IDENTICAL to the vendored copy; the vendored third-party
closure (vendor/); every build-time network fetch and the option that gates it;
and the library-only build plan that avoids all of them.

  tools/map-llama-upstreams.py [--json out.json]
"""
import glob, json, os, re, subprocess, sys
ROOT = "/home/google/SymonSaysLLC"
LL = os.path.join(ROOT, "Symoneural-LLM/src/inference/source/llama.cpp")
GG = os.path.join(ROOT, "Symoneural-LLM/src/inference/source/ggml")

def git_pin(pin, *a):
    r = subprocess.run(["git", "--git-dir=" + pin, "--work-tree=/", *a], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""

def main():
    lock = {c["component"]: c for c in json.load(open(os.path.join(ROOT, "acquisition/source-lock.json")))["components"]}
    out = {"schema": "symoneural-llama-upstream-map/1"}
    ll = lock.get("llama.cpp", {})
    pin = os.path.join(ROOT, ll.get("pins_path", ""))
    out["llama_cpp"] = {"commit": ll.get("commit_sha"), "tree": ll.get("tree_sha"), "tags": git_pin(pin, "tag", "--points-at", ll.get("commit_sha", "HEAD")).split(),
                        "date": git_pin(pin, "log", "-1", "--format=%ad", "--date=short", ll.get("commit_sha", "HEAD")),
                        "release_status": "b-tag build (b10809) plus v0.4.0 release tag at the same commit" if "v0.4.0" in git_pin(pin, "tag", "--points-at", ll.get("commit_sha", "HEAD")) else "b-tag build",
                        "source_path": ll.get("source_path")}
    sync = open(os.path.join(LL, "scripts/sync-ggml.last")).read().strip()
    ver = {}
    for k in ("MAJOR", "MINOR", "PATCH"):
        m = re.search(r"set\(GGML_VERSION_%s (\d+)\)" % k, open(os.path.join(LL, "ggml/CMakeLists.txt")).read())
        ver[k.lower()] = int(m.group(1)) if m else None
    gg = lock.get("ggml", {})
    ident = None
    if os.path.isdir(GG):
        diffs = {}
        for d in ("include", "src", "cmake"):
            r = subprocess.run(["diff", "-rq", os.path.join(GG, d), os.path.join(LL, "ggml", d)], capture_output=True, text=True)
            diffs[d] = len([l for l in r.stdout.splitlines() if l.strip()])
        r = subprocess.run(["diff", "-q", os.path.join(GG, "CMakeLists.txt"), os.path.join(LL, "ggml/CMakeLists.txt")], capture_output=True)
        diffs["CMakeLists.txt"] = 0 if r.returncode == 0 else 1
        ident = {"differences": diffs, "identical": all(v == 0 for v in diffs.values())}
    out["ggml"] = {"embedded_sync_commit": sync, "embedded_version": "%(major)s.%(minor)s.%(patch)s" % ver,
                   "canonical_upstream": "https://github.com/ggml-org/ggml", "canonical_tree_present": os.path.isdir(GG),
                   "canonical_commit": gg.get("commit_sha"), "canonical_tags": git_pin(os.path.join(ROOT, gg.get("pins_path", "")), "tag", "--points-at", gg.get("commit_sha", "HEAD")).split() if gg else [],
                   "canonical_matches_sync": bool(gg) and gg.get("commit_sha") == sync,
                   "vendored_vs_canonical": ident,
                   "compatibility_evidence": "vendored llama.cpp/ggml/{include,src,cmake,CMakeLists.txt} diff -rq against canonical ggml at the sync commit" }
    vend = sorted(d for d in os.listdir(os.path.join(LL, "vendor")) if os.path.isdir(os.path.join(LL, "vendor", d)))
    out["vendored_closure"] = {"dir": "vendor/", "entries": vend, "sync_tool": "scripts/sync_vendor.py",
                               "note": "header-only/bundled C/C++ (cpp-httplib, nlohmann json, miniaudio, stb, sheredom utf8, hash) used by tools/server and examples; libllama itself needs none of them except as the build selects"}
    fetches = []
    ua = os.path.join(LL, "scripts/ui-assets.cmake")
    if os.path.isfile(ua):
        t = open(ua).read()
        fetches.append({"where": "scripts/ui-assets.cmake", "what": "tools/server WebUI dist.tar.gz (+ .sha256) from a GitHub release or Hugging Face bucket at CONFIGURE time",
                        "gated_by": "LLAMA_USE_PREBUILT_UI (default ON) together with LLAMA_BUILD_SERVER (default ${LLAMA_STANDALONE}); LLAMA_BUILD_UI builds it from tools/ui with npm instead",
                        "evidence": "file(DOWNLOAD ...dist.tar.gz?download=true ...) at line %d" % (t[:t.find("file(DOWNLOAD")].count("\n") + 1)})
    for f in glob.glob(os.path.join(LL, "**/CMakeLists.txt"), recursive=True) + glob.glob(os.path.join(LL, "cmake/*.cmake")):
        try: t = open(f, errors="replace").read()
        except OSError: continue
        for kw in ("FetchContent_Declare", "ExternalProject_Add", "file(DOWNLOAD"):
            if kw in t and "ui-assets" not in f:
                fetches.append({"where": os.path.relpath(f, LL), "what": kw, "gated_by": "see file"})
    out["network_fetches"] = fetches
    out["library_only_build_plan"] = {
        "libggml": {"source": "canonical ggml tree at the sync commit", "cmake": ["-DGGML_BUILD_TESTS=OFF", "-DGGML_BUILD_EXAMPLES=OFF", "-DBUILD_SHARED_LIBS=ON", "-DGGML_NATIVE=OFF", "(CUDA later: -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120 from the estate toolkit)"]},
        "libllama": {"source": "llama.cpp tree", "cmake": ["-DLLAMA_USE_SYSTEM_GGML=ON", "-DLLAMA_BUILD_COMMON=OFF", "-DLLAMA_BUILD_TESTS=OFF", "-DLLAMA_BUILD_TOOLS=OFF", "-DLLAMA_BUILD_EXAMPLES=OFF", "-DLLAMA_BUILD_SERVER=OFF", "-DLLAMA_BUILD_UI=OFF", "-DLLAMA_USE_PREBUILT_UI=OFF", "-DLLAMA_CURL=OFF", "-DBUILD_SHARED_LIBS=ON"], "result": "libllama.so + include/llama.h; no server, no WebUI, no network"},
        "reference_llama_server": {"purpose": "differential test target only", "requirement": "if built, LLAMA_USE_PREBUILT_UI=OFF and LLAMA_BUILD_UI=OFF (no UI) or a separately pinned+checksummed dist.tar.gz via SRC_URI; never a product dependency"},
        "libsymoneural_llm": {"on_top_of": "libllama + libggml", "abi": "C (docs/inference/C-ABI.md)"}}
    js = json.dumps(out, indent=1, sort_keys=True)
    if "--json" in sys.argv:
        open(sys.argv[sys.argv.index("--json") + 1], "w").write(js + "\n")
    print("llama.cpp  %s  tags=%s  %s" % ((out["llama_cpp"]["commit"] or "?")[:12], ",".join(out["llama_cpp"]["tags"]), out["llama_cpp"]["date"]))
    g = out["ggml"]
    print("ggml       embedded %s (sync %s)  canonical present=%s at %s tags=%s  matches_sync=%s" % (g["embedded_version"], sync[:12], g["canonical_tree_present"], (g["canonical_commit"] or "?")[:12], ",".join(g["canonical_tags"]), g["canonical_matches_sync"]))
    if ident: print("           vendored vs canonical: %s  %s" % ("IDENTICAL" if ident["identical"] else "DIFFERS", ident["differences"]))
    print("vendor/    %s" % ", ".join(vend))
    for f in fetches: print("FETCH      %s: %s [%s]" % (f["where"], f["what"][:90], f["gated_by"][:70]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
