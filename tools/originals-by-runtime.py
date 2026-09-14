#!/usr/bin/env python3
"""originals-by-runtime.py - every ORIGINAL upstream source sectioned by its future symoneural
runtime, with build status. Reads the curated and derived records and runs tools/audit-workscope.sh
for the per-component status; writes generated/ORIGINALS-BY-RUNTIME.md (and any extra --out paths).
Nothing is renamed or moved: this is a VIEW of the estate as committed."""
import collections
import glob
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ["API", "Adaptive-Fabric", "Build", "CLI", "Common", "Crypto", "Live", "LLM", "Platform", "Ravencalc", "Remix", "Streamer", "Web"]
PROOF = {"API": "generated/evidence/api", "CLI": "generated/evidence/cli", "Common": "generated/evidence/common",
         "LLM": "generated/evidence/llm", "Ravencalc": "generated/evidence/ravencalc", "Platform": "generated/evidence/platform"}


def load(name):
    with open(os.path.join(ROOT, "acquisition", name)) as f:
        return json.load(f)


def main():
    outs = sys.argv[1:] or []
    lock = {c["component"]: c for c in load("source-lock.json")["components"]}
    man = {e["component"]: e for e in load("source-manifest.json")["entries"]}
    state = {c["component"]: c for c in load("component-state.json")["components"]}
    pend = load("pending-acquisitions.json")
    audit_run = subprocess.run([os.path.join(ROOT, "tools/audit-workscope.sh")], capture_output=True, text=True, cwd=ROOT)
    audit = {}
    for line in audit_run.stdout.splitlines():
        m = re.match(r"^(\S+)\s+(\S+)\s+(VERIFIED|LISTING-VERIFIED\S*|NOT-IN-LOCK|-)\s+\S+\s+\S+\s+\S+\s+(\S+)\s+\S+\s+(\S+)\s+(\d+)\s+(.*\S)\s*$", line)
        if m:
            audit[m.group(2)] = m.group(7).strip()
    by = collections.defaultdict(list)
    for comp, c in lock.items():
        by[c["runtime"]].append(c)
    out = []
    out.append("# SyMoNeuRaL: the ORIGINAL upstream sources, sectioned by future runtime\n")
    out.append("Generated %s by tools/originals-by-runtime.py from acquisition/source-lock.json, source-manifest.json,\n"
               "component-state.json, pending-acquisitions.json and a live run of tools/audit-workscope.sh (rc=%d). Nothing\n"
               "was renamed or moved: every row is an upstream project committed at its pin under\n"
               "`Symoneural-<Runtime>/src/<category>/source/<component>/` and verified byte-identical to upstream.\n" % (time.strftime("%Y-%m-%d %H:%M %Z"), audit_run.returncode))
    out.append("\nBuild-status vocabulary (audit): PKGDATA EXISTS = an estate package was produced from this tree in the runtime's\n"
               "build directory (historical pkgdata; QA and consumer proofs are recorded separately under generated/evidence/);\n"
               "BUILT INTO <recipe> = compiled into that recipe's executable (dependency tree, no package of its own);\n"
               "RECIPE, NEVER PACKAGED = recipe exists, nothing built; STUB = placeholder recipe without a build class;\n"
               "REFERENCE_ONLY / RETIRED_TO_PROVIDER = acquired, pinned, committed; never built for a target, by recorded ruling.\n")
    total = 0
    for rt in ORDER:
        rows = sorted(by.get(rt, []), key=lambda c: c["component"])
        imgs = sorted(glob.glob(os.path.join(ROOT, "Symoneural-%s/build/devtool-master/tmp/deploy/images/*/symoneural-image-*.rootfs-*.tar.gz" % rt)))
        out.append("\n## Symoneural-%s  (%d upstream source%s)\n" % (rt, len(rows), "" if len(rows) == 1 else "s"))
        if imgs:
            out.append("Image on disk: `%s`; runtime proofs: `%s/`\n" % (os.path.basename(imgs[-1]), PROOF.get(rt, "-")))
        out.append("| Upstream original | Upstream | Version / tag | Commit | Licence (recipe) | State | Build status |")
        out.append("|---|---|---|---|---|---|---|")
        for c in rows:
            m = man.get(c["component"], {})
            s = state.get(c["component"], {})
            ver = m.get("intended_tag_version") or c.get("declared_version_PV") or "-"
            lic = c.get("recipe_LICENSE") if c.get("recipe_LICENSE") not in (None, "NOT-APPLICABLE") else "-"
            if lic == "-":
                prow = next((r for r in pend.get("rows", []) if r["component"] == c["component"]), None)
                if prow and prow.get("licence_expected"):
                    lic = prow["licence_expected"].split(" (")[0].split(" - ")[0][:40] + " (curated)"
            url = (c.get("upstream_url") or m.get("upstream_url") or "-").replace("https://github.com/", "gh:")
            out.append("| %s | %s | %s | `%s` | %s | %s | %s |" % (c["component"], url, ver, c["commit_sha"][:12], lic, s.get("state", "-"), audit.get(c["component"], "(not in audit)")))
            total += 1
        pend_rows = [r for r in pend.get("rows", []) if (r.get("runtime") or "").split(" ")[0] == rt and r["component"] not in lock]
        for r in pend_rows:
            why = (r.get("ruling") or r.get("notes") or "").strip()
            out.append(("\n- Pending (NOT ACQUIRED): %s %s `%s` %s" % (r["component"], r.get("tag", ""), r["sha"][:12], (r.get("upstream_url") or "").replace("https://github.com/", "gh:"))).rstrip()
                       + ((" — " + why[:200]) if why else ""))
        if rt == "Platform":
            out.append("\n- BINARY-EXTERNAL build inputs (not sources): Debian linux-headers/kbuild/image 6.12.107+deb13-amd64 (6.12.107-1) pinned by sha256 — Debian profile only. External providers still missing for a fresh-machine GPU: NVIDIA driver userspace and GSP firmware 615.71.09 (BLOCKED); acpi_call kernel module for AWCC (NOT ACQUIRED).")
        if rt in ("LLM", "Common"):
            out.append("\n- BINARY-EXTERNAL inputs (not sources): cuda-toolkit-bin 13.4.1 (NVIDIA EULA)%s — pinned by NVIDIA debian13 index sha256." % (", cudnn-bin 9.25.1.1 (NVIDIA SLA)" if rt == "Common" else ""))
        if rt == "Crypto":
            out.append("\n- Pending: kawpowminer — DEFERRED to P11 / Phase 20e (GPL-3.0 product/distribution ruling required).")
    out.append("\n\n## Planned runtimes without a source directory yet\n")
    out.append("Named in the estate records as future consumers but with no `Symoneural-<Runtime>/` directory and no acquired source: **Tune** (CuPy / cuda-python), **Diffuse** (diffusers; ComfyUI was rejected: GPL-3.0), **Studio**.\n")
    out.append("\n## Recorded as NOT ACQUIRED (by ruling)\n")
    for r in pend.get("not_acquired", []):
        out.append("- %s: %s" % (r["component"], r["reason"]))
    out.append("\n\nTotal upstream originals committed: %d. Runtime directories on disk: %d." % (total, len(glob.glob(os.path.join(ROOT, "Symoneural-*/")))))
    text = "\n".join(l.rstrip() for l in out) + "\n"
    targets = [os.path.join(ROOT, "generated/ORIGINALS-BY-RUNTIME.md")] + outs
    for t in targets:
        with open(t, "w") as f:
            f.write(text)
        print("written", t, "(%d rows)" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
