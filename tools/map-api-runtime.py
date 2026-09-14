#!/usr/bin/env python3
"""map-api-runtime.py - one machine-readable map of what the API runtime IS.

Reads disk only: source-lock (direct + Tier-B trees), provider-decisions (Python
runtime providers), the built wheels' METADATA (edges), recipes (RDEPENDS, classes),
pkgdata (packaged state), first-party files, the unit registry and the application
definitions. Output is JSON; the human table is a view of it.

  tools/map-api-runtime.py [--json out.json]
"""
import glob, json, os, re, sys, subprocess
ROOT = "/home/google/SymonSaysLLC"
sys.path.insert(0, os.path.join(ROOT, "Symoneural-API", "app"))

def load(p):
    return json.load(open(os.path.join(ROOT, p)))

def main():
    out = {"schema": "symoneural-api-runtime-map/1", "head": subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()}
    lock = load("acquisition/source-lock.json")["components"]
    api = [c for c in lock if c["runtime"] == "API"]
    prov = {r["distribution"]: r for r in load("acquisition/provider-decisions.json").get("python_runtime_providers", [])}
    direct = {"fastapi", "starlette", "uvicorn", "pydantic", "httpx", "httpcore"}
    out["tier_a_direct"] = [dict(component=c["component"], commit=c["commit_sha"], tree=c["tree_sha"], pv=c["declared_version_PV"],
                                 licence=c["recipe_LICENSE"], recipe=c["recipe_name"], source_path=c["source_path"]) for c in api if c["component"] in direct]
    out["tier_b_runtime"] = [dict(component=c["component"], commit=c["commit_sha"], tree=c["tree_sha"], pv=c["declared_version_PV"],
                                  licence=c["recipe_LICENSE"], recipe=c["recipe_name"], source_path=c["source_path"],
                                  provider_decision=prov.get(c["component"], {}).get("selected_provider", "UNRECORDED")) for c in api if c["component"] not in direct]
    out["tier_b_shared_providers"] = [dict(distribution=d, **{k: v for k, v in r.items() if k != "distribution"}) for d, r in prov.items() if "shared provider" in str(r.get("selected_provider", ""))]
    # Tier C: build classes and native DEPENDS of every API recipe
    tier_c = {}
    for rp in glob.glob(os.path.join(ROOT, "meta-symoneural/recipes-api/*/*.bb")):
        t = open(rp).read()
        pn = os.path.basename(rp).split("_")[0]
        tier_c[pn] = {"inherit": " ".join(re.findall(r"^inherit\s+(.*)$", t, re.M)).split(),
                      "DEPENDS": sorted(set(sum((m.group(1).replace("\\", " ").split() for m in re.finditer(r'^DEPENDS[^=]*=\s*"([^"]*)"', t, re.M)), []))),
                      "RDEPENDS": sorted(set(sum((m.group(1).replace("\\", " ").split() for m in re.finditer(r'^RDEPENDS:\$\{PN\}[^=]*=\s*"([^"]*)"', t, re.M)), [])))}
    out["tier_c_build_only"] = {"classification": "BUILD_REQUIRED - borrowed from pinned layers, never on the target",
                                "families": sorted({c for r in tier_c.values() for c in r["inherit"] if c.startswith(("python_", "setuptools", "cargo"))} | {d for r in tier_c.values() for d in r["DEPENDS"]}),
                                "per_recipe": tier_c}
    # edges from built wheels
    edges = []
    for md in glob.glob(os.path.join(ROOT, "Symoneural-API/build/devtool-master/tmp/work/*/symoneural-*/*/image/usr/lib/python3*/site-packages/*.dist-info/METADATA")):
        pn = re.search(r"/work/[^/]+/(symoneural-[^/]+)/", md).group(1)
        for line in open(md, errors="replace"):
            if line.startswith("Requires-Dist:") and "extra ==" not in line:
                edges.append({"from": pn, "requires": line.split(":", 1)[1].strip()})
    out["wheel_edges"] = edges
    # packaged state
    pk = {}
    for f in glob.glob(os.path.join(ROOT, "Symoneural-API/build/devtool-master/tmp/pkgdata/*/symoneural-*")):
        if os.path.isfile(f): pk[os.path.basename(f)] = True
    out["packaged"] = sorted(pk)
    # first-party
    app = os.path.join(ROOT, "Symoneural-API/app")
    out["first_party"] = {"c": sorted(os.path.relpath(p, ROOT) for p in glob.glob(app + "/src/*.c") + glob.glob(app + "/include/symoneural/*.h")),
                          "python": sorted(os.path.relpath(p, ROOT) for p in glob.glob(app + "/symoneural_api/*.py")),
                          "tests": sorted(os.path.relpath(p, ROOT) for p in glob.glob(app + "/tests/*/*"))}
    try:
        from symoneural_api import units
        out["units"] = [{"unit": u.name, "resource": str(u.resource), "port": u.port, "backed_by": list(u.backed_by), "token_env": u.token_env} for u in units.REGISTRY.values()]
    except Exception as e:
        out["units"] = "import failed: %s" % e
    try:
        from symoneural_api import applications
        out["applications"] = [a.to_public() for a in applications.REGISTRY.values()]
    except Exception:
        out["applications"] = "no application registry yet"
    out["recipes_services_packagegroups"] = {
        "recipes": sorted(os.path.basename(p).split("_")[0] for p in glob.glob(os.path.join(ROOT, "meta-symoneural/recipes-api/*/*.bb"))),
        "packagegroups": sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(ROOT, "meta-symoneural/recipes-core/packagegroups/*.bb"))),
        "images": sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(ROOT, "meta-symoneural/recipes-core/images/*.bb"))),
        "services": sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "meta-symoneural/**/*.service"), recursive=True))}
    out["external_secrets_config"] = {"provisioned_by": "symoneural-secrets (/etc/symoneural, values never in git)",
                                      "env_names": sorted({u["token_env"] for u in out["units"]} | {"SYM_OWNER_TOKEN", "SYM_GPU_LOCK", "SYMONEURAL_HOST", "SYMONEURAL_PORT"}) if isinstance(out["units"], list) else []}
    out["counts"] = {"tier_a": len(out["tier_a_direct"]), "tier_b_trees": len(out["tier_b_runtime"]), "tier_b_shared": len(out["tier_b_shared_providers"]),
                     "upstream_runtime_sources": len(out["tier_a_direct"]) + len(out["tier_b_runtime"]) + len([s for s in out["tier_b_shared_providers"] if s["distribution"] == "pydantic-core"])}
    js = json.dumps(out, indent=1, sort_keys=True)
    if "--json" in sys.argv:
        open(sys.argv[sys.argv.index("--json") + 1], "w").write(js + "\n")
    c = out["counts"]
    print("API runtime map @ %s" % out["head"])
    print("  Tier A direct sources       : %d" % c["tier_a"])
    print("  Tier B runtime trees        : %d  (+ %d shared providers from owned trees)" % (c["tier_b_trees"], c["tier_b_shared"]))
    print("  upstream runtime sources    : %d" % c["upstream_runtime_sources"])
    print("  wheel edges (non-extra)     : %d" % len(edges))
    print("  packaged symoneural-* (pkgdata): %d" % len(out["packaged"]))
    print("  first-party C/Python/tests  : %d / %d / %d files" % (len(out["first_party"]["c"]), len(out["first_party"]["python"]), len(out["first_party"]["tests"])))
    print("  units: %s" % (", ".join(u["unit"] for u in out["units"]) if isinstance(out["units"], list) else out["units"]))
    print("  applications: %s" % (", ".join(a["application_id"] for a in out["applications"]) if isinstance(out["applications"], list) else out["applications"]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
