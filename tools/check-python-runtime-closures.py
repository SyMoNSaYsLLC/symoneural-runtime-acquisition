#!/usr/bin/env python3
"""check-python-runtime-closures.py - the estate-wide Python runtime closure gate.

OpenEmbedded does not turn a wheel's Requires-Dist into RDEPENDS; the recipe
author must. So a symoneural-* Python package can build, package and look
healthy in pkgdata while `import` fails on the target. This tool derives the
closure FROM THE BUILT WHEELS every time and compares it with what the recipes
declare, what the feeds hold and (optionally) what a clean root has installed.

  tools/check-python-runtime-closures.py --runtime API [--runtime CLI ...] | --all
        [--root <clean-target-root>] [--json out.json] [--emit-dir dir]
        [--extra <dist>=<extra>,...]

Per requirement it reports:
  consumer · requirement · marker · provider · package · declared RDEPENDS ·
  built (feed) · installed (root) · version status · source authority · STATUS

Exit 1 on any of: MISSING RDEPENDS, MISSING PACKAGE, WRONG VERSION,
UNKNOWN PROVIDER, DUPLICATE PROVIDER, UNRESOLVED SOURCE OWNERSHIP.

Sources of truth (all read from disk, none hard-coded):
  wheel METADATA   Symoneural-<RT>/build/devtool-master/tmp/work/*/<pn>/*/image/**/site-packages/*.dist-info/METADATA
  RDEPENDS         .../tmp/pkgdata/<arch>/runtime/<pn>            (post-packaging truth)
  feeds            Symoneural-*/build/devtool-master/tmp/deploy/ipk/*/*.ipk
  estate recipes   meta-symoneural/recipes-*/*/*.bb (active) - retired/ are NOT providers
  layer recipes    ~/symoneural-bootstrap-master/{openembedded-core/meta,meta-openembedded/*}/recipes-*/python/python3-<name>_<ver>.bb
  ownership        acquisition/provider-decisions.json  (rule: own what you ship)
  target env       Python 3.14, linux, x86_64, CPython - read from the built python3 work dir
"""
import argparse, glob, json, os, re, sys
from packaging.requirements import Requirement, InvalidRequirement
from packaging.markers import default_environment
from packaging.specifiers import SpecifierSet
from packaging.version import Version, InvalidVersion
from packaging.utils import canonicalize_name

ROOT = "/home/google/SymonSaysLLC"
BOOT = os.path.expanduser("~/symoneural-bootstrap-master")
RUNTIMES = sorted(d.replace("Symoneural-", "") for d in os.listdir(ROOT) if d.startswith("Symoneural-"))

STATUS_FATAL = ("MISSING RDEPENDS", "MISSING PACKAGE", "WRONG VERSION", "UNKNOWN PROVIDER",
                "DUPLICATE PROVIDER", "UNRESOLVED SOURCE OWNERSHIP")


def norm(name):
    return canonicalize_name(name)


def build_dir(rt):
    return os.path.join(ROOT, "Symoneural-" + rt, "build", "devtool-master")


def target_environment():
    """Marker environment for the TARGET, not the host. Version from the built
    python3 work directory; the rest from the estate's fixed target."""
    pyver = "3.14.7"
    for d in glob.glob(os.path.join(ROOT, "Symoneural-*/build/devtool-master/tmp/work/*/python3/*/")):
        pyver = os.path.basename(d.rstrip("/")); break
    env = default_environment()
    env.update({"python_version": ".".join(pyver.split(".")[:2]), "python_full_version": pyver,
                "sys_platform": "linux", "platform_system": "Linux", "platform_machine": "x86_64",
                "platform_python_implementation": "CPython", "implementation_name": "cpython",
                "os_name": "posix", "platform_release": "", "platform_version": ""})
    return env


def read_metadata(path):
    md = {"Name": None, "Version": None, "Requires-Dist": [], "Provides-Extra": []}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                break          # end of headers; body is the long description
            k, _, v = line.partition(":")
            v = v.strip()
            if k in ("Requires-Dist", "Provides-Extra"):
                md[k].append(v)
            elif k in ("Name", "Version"):
                md[k] = v
    return md


def built_wheels(rt):
    """pn -> dist-info METADATA for every symoneural-* wheel built in this runtime's dir."""
    out = {}
    pat = os.path.join(build_dir(rt), "tmp/work/*/symoneural-*/*/image/usr/lib/python3*/site-packages/*.dist-info/METADATA")
    for p in sorted(glob.glob(pat)):
        pn = re.search(r"/work/[^/]+/(symoneural-[^/]+)/", p).group(1)
        out[pn] = read_metadata(p)
        out[pn]["_path"] = os.path.relpath(p, ROOT)
    return out


def pkgdata_rdepends(rt, pn):
    """RDEPENDS of the main package after packaging, from pkgdata/runtime."""
    for p in glob.glob(os.path.join(build_dir(rt), "tmp/pkgdata/*/runtime/%s" % pn)):
        for line in open(p, errors="replace"):
            if line.startswith("RDEPENDS:"):
                return set(re.sub(r"\([^)]*\)", "", line.split(":", 2)[2]).split())
    return None   # not packaged


def recipe_rdepends(pn):
    """RDEPENDS:${PN} lines from the recipe text (for unpackaged recipes)."""
    for rp in glob.glob(os.path.join(ROOT, "meta-symoneural/recipes-*/%s/*.bb" % pn)):
        txt = open(rp, errors="replace").read()
        names = set()
        for m in re.finditer(r'^RDEPENDS:\$\{PN\}[^=]*=\s*"([^"]*)"', txt, re.M):
            names |= set(m.group(1).replace("\\", " ").split())
        return names
    return set()


def estate_recipes():
    """active pn -> recipe path (retired/ excluded: a retired recipe provides nothing)."""
    out = {}
    for rp in glob.glob(os.path.join(ROOT, "meta-symoneural/recipes-*/*/*.bb")):
        out[os.path.basename(rp).split("_")[0]] = os.path.relpath(rp, ROOT)
    return out


def layer_recipes():
    """python3-<norm> -> (layer, version, path) for the pinned layers."""
    out = {}
    for layer, pat in (("oe-core", "openembedded-core/meta/recipes-*/python/python3-*_*.bb"),
                       ("meta-python", "meta-openembedded/meta-python/recipes-*/python/python3-*_*.bb"),
                       ("meta-oe", "meta-openembedded/meta-oe/recipes-*/*/python3-*_*.bb")):
        for rp in glob.glob(os.path.join(BOOT, pat)):
            base = os.path.basename(rp)[:-3]
            pn, _, ver = base.rpartition("_")
            key = "python3-" + norm(pn[len("python3-"):])
            out.setdefault(key, (layer, ver, os.path.relpath(rp, BOOT)))
    return out


def feed_packages():
    """package name -> [(version, ipk path)] across every runtime feed."""
    out = {}
    for p in glob.glob(os.path.join(ROOT, "Symoneural-*/build/devtool-master/tmp/deploy/ipk/*/*.ipk")):
        b = os.path.basename(p)[:-4]
        name, _, rest = b.partition("_")
        ver = rest.split("_")[0].split("-r")[0] if rest else ""
        out.setdefault(name, []).append((ver, os.path.relpath(p, ROOT)))
    return out


def root_installed(root):
    """dist name -> version from a clean target root's site-packages."""
    out = {}
    if not root:
        return out
    for p in glob.glob(os.path.join(root, "usr/lib/python3*/site-packages/*.dist-info/METADATA")):
        md = read_metadata(p)
        if md["Name"]:
            out[norm(md["Name"])] = md["Version"]
    return out


def ownership_decisions():
    """logical name -> selected_provider, from the curated record."""
    try:
        d = json.load(open(os.path.join(ROOT, "acquisition/provider-decisions.json")))
    except Exception:
        return {}
    out = {}
    for row in d.get("decisions", []):
        out[norm(row["logical"])] = row.get("selected_provider")
    for row in d.get("python_runtime_providers", []):
        out[norm(row["distribution"])] = row.get("selected_provider")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runtime", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--root", help="clean target root to check installed distributions against")
    ap.add_argument("--json", help="write the full machine-readable result here")
    ap.add_argument("--emit-dir", help="write <RT>-RUNTIME-CLOSURE.json and <RT>-BUILD-CLOSURE.json here")
    ap.add_argument("--extra", action="append", default=[], help="dist=extra1,extra2 to select an extra as RUNTIME REQUIRED")
    a = ap.parse_args()
    rts = RUNTIMES if a.all else a.runtime
    if not rts:
        ap.error("--runtime <RT> or --all")

    env = target_environment()
    selected_extras = {}
    for e in a.extra:
        d, _, xs = e.partition("=")
        selected_extras[norm(d)] = set(x.strip() for x in xs.split(",") if x.strip())
    est = estate_recipes()
    layers = layer_recipes()
    feeds = feed_packages()
    installed = root_installed(a.root)
    owned = ownership_decisions()

    # dist -> estate pn, from every built wheel in every runtime (a dist name is
    # not the recipe name: mcp -> symoneural-mcp-python-sdk, anthropic -> symoneural-anthropic-sdk-python)
    dist_to_pn = {}
    all_wheels = {}
    for rt in RUNTIMES:
        for pn, md in built_wheels(rt).items():
            all_wheels[(rt, pn)] = md
            if md["Name"]:
                dist_to_pn[norm(md["Name"])] = pn

    def provider_for(dist):
        n = norm(dist)
        cands = []
        pn = dist_to_pn.get(n) or ("symoneural-" + n if "symoneural-" + n in est else None)
        if pn and pn in est:
            cands.append(("SYMONEURAL", pn, None))
        lk = "python3-" + n
        if lk in layers:
            cands.append(("LAYER:" + layers[lk][0], lk, layers[lk][1]))
        return cands

    # extras a CONSUMER asks of a dependency (mcp -> pyjwt[crypto]) become selected
    # extras when that dependency's own wheel is evaluated, so its extra-gated
    # requirements (cryptography) surface as RUNTIME REQUIRED instead of hiding.
    # Only requirement lines that APPLY on the target count: an extra-gated line
    # such as fastapi's `uvicorn[standard]; extra == "standard"` must not select
    # uvicorn[standard] unless some consumer actually asked fastapi[standard].
    # (Consumer extras of the consumer itself are honoured through selected_extras.)
    requested_extras = {}
    for (rt0, pn0), md0 in all_wheels.items():
        own_extras = selected_extras.get(norm(md0.get("Name") or pn0), set())
        for req_s in md0["Requires-Dist"]:
            try:
                r0 = Requirement(req_s)
            except InvalidRequirement:
                continue
            if not r0.extras:
                continue
            if r0.marker is not None and not any(
                    r0.marker.evaluate(dict(env, extra=x)) for x in (own_extras or {""})):
                continue
            requested_extras.setdefault(norm(r0.name), set()).update(r0.extras)
    for d, xs in requested_extras.items():
        selected_extras.setdefault(d, set()).update(xs)

    rows, edges, fatal = [], [], []
    per_rt_closure = {}
    for rt in rts:
        wheels = built_wheels(rt)
        runtime_closure, build_closure = {}, {}
        for pn, md in sorted(wheels.items()):
            dist = md["Name"] or pn
            declared = pkgdata_rdepends(rt, pn)
            packaged = declared is not None
            if declared is None:
                declared = recipe_rdepends(pn)
            for req_s in md["Requires-Dist"]:
                try:
                    req = Requirement(req_s)
                except InvalidRequirement:
                    rows.append(dict(runtime=rt, consumer=pn, requirement=req_s, status="UNPARSEABLE REQUIREMENT"))
                    fatal.append("UNPARSEABLE"); continue
                # markers: evaluate for the target; extras only if deliberately selected
                extras = selected_extras.get(norm(dist), set())
                applies = True
                if req.marker is not None:
                    applies = any(req.marker.evaluate(dict(env, extra=x)) for x in (extras or {""}))
                extra_of = None
                if req.marker is not None and "extra" in str(req.marker):
                    m = re.search(r'extra\s*==\s*["\']([^"\']+)', str(req.marker))
                    extra_of = m.group(1) if m else "?"
                if not applies:
                    rows.append(dict(runtime=rt, consumer=pn, requirement=req_s, distribution=norm(req.name),
                                     marker=str(req.marker), classification=("EXTRA:%s NOT SELECTED" % extra_of) if extra_of else "MARKER FALSE FOR TARGET",
                                     status="NOT REQUIRED"))
                    continue
                cands = provider_for(req.name)
                sym = [c for c in cands if c[0] == "SYMONEURAL"]
                lay = [c for c in cands if c[0] != "SYMONEURAL"]
                n = norm(req.name)
                decision = owned.get(n)
                # choose: an estate recipe wins; else the layer only if a decision permits borrowing
                if sym:
                    provider, package, pver = sym[0]
                    authority = "SYMONEURAL-OWNED" if decision in (None, "SYMONEURAL-OWNED") else decision
                    if decision is None:
                        authority = "SYMONEURAL-OWNED (recipe exists; record the decision)"
                elif lay and decision and decision.startswith(("LAYER", "OE-CORE", "META-")):
                    provider, package, pver = lay[0]
                    authority = decision
                elif lay:
                    provider, package, pver = lay[0]
                    authority = "UNRESOLVED SOURCE OWNERSHIP (layer has %s %s; rule says own what you ship)" % (package, pver)
                else:
                    provider, package, pver, authority = "UNKNOWN", None, None, "UNKNOWN PROVIDER"
                in_rdepends = bool(package) and package in declared
                built = feeds.get(package, []) if package else []
                # version: prefer the feed's version, else the layer recipe version
                have_ver = built[0][0] if built else (pver or (all_wheels.get((rt, package), {}) or {}).get("Version"))
                if not have_ver and package in dist_to_pn.values():
                    for (r2, p2), m2 in all_wheels.items():
                        if p2 == package: have_ver = m2["Version"]
                ver_ok = None
                if have_ver and req.specifier:
                    try:
                        ver_ok = req.specifier.contains(Version(have_ver), prereleases=True)
                    except InvalidVersion:
                        ver_ok = None
                inst = installed.get(n)
                inst_ok = None
                if a.root:
                    inst_ok = bool(inst) and (not req.specifier or req.specifier.contains(Version(inst), prereleases=True))
                dup = len({c[1] for c in cands if feeds.get(c[1])}) > 1
                if provider == "UNKNOWN":
                    status = "UNKNOWN PROVIDER"
                elif authority.startswith("UNRESOLVED"):
                    status = "UNRESOLVED SOURCE OWNERSHIP"
                elif dup:
                    status = "DUPLICATE PROVIDER"
                elif not in_rdepends:
                    status = "MISSING RDEPENDS"
                elif not built:
                    status = "MISSING PACKAGE"
                elif ver_ok is False:
                    status = "WRONG VERSION"
                elif a.root and not inst_ok:
                    status = "MISSING PACKAGE" if not inst else "WRONG VERSION"
                else:
                    status = "PASS"
                if status in STATUS_FATAL:
                    fatal.append(status)
                rows.append(dict(runtime=rt, consumer=pn, consumer_dist=dist, consumer_version=md["Version"],
                                 requirement=req_s, distribution=n, specifier=str(req.specifier) or "any",
                                 marker=str(req.marker) if req.marker else "", provider=provider, package=package,
                                 provider_version=have_ver, declared_rdepends=in_rdepends, built=bool(built),
                                 built_ipk=built[0][1] if built else None, installed_version=inst,
                                 version_satisfied=ver_ok, source_authority=authority, packaged=packaged, status=status))
                edges.append((pn, n, str(req.specifier) or "any"))
                runtime_closure.setdefault(n, {"distribution": n, "provider": provider, "package": package,
                                               "version": have_ver, "constraints": [], "consumers": [], "authority": authority})
                runtime_closure[n]["constraints"].append(str(req.specifier) or "any")
                runtime_closure[n]["consumers"].append(pn)
            # build closure: the recipe's DEPENDS + inherit classes (host/sysroot side)
            for rp in glob.glob(os.path.join(ROOT, "meta-symoneural/recipes-*/%s/*.bb" % pn)):
                txt = open(rp, errors="replace").read()
                deps = set()
                for m in re.finditer(r'^DEPENDS[^=]*=\s*"([^"]*)"', txt, re.M):
                    deps |= set(m.group(1).replace("\\", " ").split())
                inh = " ".join(re.findall(r"^inherit\s+(.*)$", txt, re.M)).split()
                build_closure[pn] = {"DEPENDS": sorted(deps), "inherit": inh, "classification": "BUILD_REQUIRED"}
        per_rt_closure[rt] = {"runtime_closure": runtime_closure, "build_closure": build_closure,
                              "direct_wheels": {pn: {"distribution": md["Name"], "version": md["Version"], "metadata": md["_path"]}
                                                for pn, md in wheels.items()}}

    # ---- report
    w = [8, 32, 22, 14, 8, 5, 5, 4, 12]
    print("RUNTIME   CONSUMER                          DISTRIBUTION            SPEC           PROVIDER  RDEP  BUILT VER  STATUS")
    for r in rows:
        if r["status"] == "NOT REQUIRED":
            continue
        print("%-9s %-33s %-23s %-14s %-9s %-5s %-5s %-4s %s" % (
            r["runtime"], r["consumer"][:33], r.get("distribution", "?")[:23], r.get("specifier", "")[:14],
            (r.get("provider") or "?")[:9], "y" if r.get("declared_rdepends") else "-", "y" if r.get("built") else "-",
            {True: "ok", False: "BAD", None: "?"}[r.get("version_satisfied")], r["status"]))
    not_req = [r for r in rows if r["status"] == "NOT REQUIRED"]
    print()
    if requested_extras:
        print("extras selected by consumers (evaluated as RUNTIME REQUIRED): " + ", ".join("%s[%s]" % (d, ",".join(sorted(x))) for d, x in sorted(requested_extras.items())))
    print("not required for the target (extras not selected / marker false): %d" % len(not_req))
    import collections
    c = collections.Counter(r["status"] for r in rows if r["status"] != "NOT REQUIRED")
    for k, v in sorted(c.items()):
        print("  %-34s %d" % (k, v))
    for rt, cl in per_rt_closure.items():
        n_direct = len(cl["direct_wheels"]); n_trans = len(cl["runtime_closure"])
        print("%s: %d direct wheels, %d distinct runtime requirements -> %d upstream runtime sources (direct + transitive first level)"
              % (rt, n_direct, n_trans, n_direct + len([d for d in cl["runtime_closure"] if d not in {norm(x["distribution"] or "") for x in cl["direct_wheels"].values()}])))

    if a.emit_dir:
        os.makedirs(a.emit_dir, exist_ok=True)
        for rt, cl in per_rt_closure.items():
            json.dump({"schema": "symoneural-runtime-closure/1", "runtime": rt, "target_environment": env,
                       "direct": cl["direct_wheels"], "requirements": cl["runtime_closure"],
                       "edges": [e for e in edges if e[0] in cl["direct_wheels"]]},
                      open(os.path.join(a.emit_dir, "%s-RUNTIME-CLOSURE.json" % rt), "w"), indent=1, sort_keys=True)
            json.dump({"schema": "symoneural-build-closure/1", "runtime": rt, "recipes": cl["build_closure"],
                       "note": "what the build host/sysroot needs to produce the packages; never installed on the target"},
                      open(os.path.join(a.emit_dir, "%s-BUILD-CLOSURE.json" % rt), "w"), indent=1, sort_keys=True)
        print("closure manifests written to", a.emit_dir)
    if a.json:
        json.dump({"schema": "symoneural-python-closure-check/1", "target_environment": env, "rows": rows,
                   "edges": edges, "fatal": sorted(set(fatal))}, open(a.json, "w"), indent=1, sort_keys=True)
    print("RESULT:", "FAIL (%s)" % ", ".join(sorted(set(fatal))) if fatal else "PASS")
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main())
