#!/usr/bin/env python3
"""lib_acq.py - shared, deterministic primitives for the acquisition control plane.

Repository discovery never assumes a particular .git filesystem representation.
Git permits .git to be a directory OR a file (worktrees, submodules), so every
candidate is validated with git itself rather than by stat()-ing a path.

SOURCES-100 (2026-09-13) moved every acquired tree's .git OUT of the tree into a
pin store beside it - Symoneural-<RT>/src/<cat>/.gitpins/<comp>.git - and
committed the tree's files to the estate repository at that pin. A component is
therefore identified by EITHER an in-tree .git (not yet ingested) OR a pin.
Every git question about a component's history goes to whichever exists; the
working-tree question ("was anything written into it?") goes to the estate
repository, which now tracks those files.
"""
import os, subprocess, hashlib, json

ROOT = "/home/google/SymonSaysLLC"
ACQ  = os.environ.get("ACQ_OUT") or os.path.join(ROOT, "acquisition")
# the authoritative records, regardless of where a rescan writes its output
AUTH_ACQ = os.path.join(ROOT, "acquisition")
GEN  = os.path.join(ROOT, "generated")
BOOT = os.path.expanduser("~/symoneural-bootstrap-master")
PINS_DIRNAME = ".gitpins"

LOCKED_STACK = {
    "openembedded-core": "fe7a24bc67118e7e184b5f5247258715e3904e7c",
    "bitbake":           "046a90b0e9b7b914b7a95aec579cdc3fc9c7617a",
    # D1: admitted as a pinned layer. Only meta-oe and meta-python enter
    # bblayers; consumed only for named providers. Pin and bump, never HEAD.
    "meta-openembedded": "43b79d8e372c4f69ebab6c85b39d97b41522080f",
}

HOST_DESIGNATION = {
    "role": "BUILD HOST / REFERENCE MACHINE / SERVER - all of the above",
    "path": ROOT,
    "statement": ("Everything is done here. Acquisition, recipe curation, scanning, "
                  "verification and BUILD all execute on this machine. There is no "
                  "second host."),
    "supersedes": ("Earlier control-plane revisions split evidence into 'research host' "
                   "versus 'accepted reference machine' and filed work done here as "
                   "NON-AUTHORITATIVE. That split was a distinction without a second "
                   "host: no other machine ever existed in this estate. Withdrawn. "
                   "Work performed here is authoritative."),
    "consequence": ("No build, hash or record needs re-performing elsewhere to become "
                    "authoritative."),
}

# Skip classes are by MEANING (build output / cache / vcs internals), never by depth.
SKIP_NAMES = {".git", PINS_DIRNAME, "__pycache__", "node_modules"}
SKIP_PATH_MARKERS = ("/tmp/", "/tmp-glibc/", "/downloads/", "/sstate-cache",
                     "/build/devtool/", "/build/devtool-master/")

def git(d, *a, timeout=300):
    try:
        r = subprocess.run(["git", "-C", d, *a], capture_output=True,
                           text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""

def git_pin(pin, *a, timeout=300):
    """git against a pin store. --work-tree=/ because a repository moved out
    from under its work tree keeps a relative core.worktree that points
    nowhere, and git refuses to start ("cannot chdir") without one that exists."""
    try:
        r = subprocess.run(["git", "--git-dir=" + pin, "--work-tree=/", *a],
                           capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""

def pin_path(source_path):
    """Symoneural-<RT>/src/<cat>/.gitpins/<comp>.git for a component's source path.
    The bitbake tree IS Symoneural-Build/src/bitbake/source, so a path ending in
    `source` names its category as the component."""
    parts = source_path.strip("/").split("/")
    if len(parts) < 4 or parts[1] != "src":
        return None
    comp = parts[-1] if parts[-1] != "source" else parts[2]
    return os.path.join(ROOT, parts[0], parts[1], parts[2], PINS_DIRNAME, comp + ".git")

def has_intree_git(abspath):
    return os.path.exists(os.path.join(abspath, ".git"))

def gitdir_for(abspath):
    """The repository holding a component's history: the in-tree .git if it is
    still there, otherwise its pin. None if neither exists."""
    if has_intree_git(abspath):
        return os.path.join(abspath, ".git")
    pin = pin_path(os.path.relpath(abspath, ROOT))
    return pin if pin and os.path.isdir(pin) else None

def git_at(abspath, *a):
    """Ask a component's own history a question, whichever form it is in."""
    if has_intree_git(abspath):
        return git(abspath, *a)
    pin = pin_path(os.path.relpath(abspath, ROOT))
    if pin and os.path.isdir(pin):
        return git_pin(pin, *a)
    return ""

def is_git_root(p):
    """True only if p is the TOP of a work tree - validated by git, not by stat."""
    if not os.path.isdir(p):
        return False
    if git(p, "rev-parse", "--is-inside-work-tree") != "true":
        return False
    top = git(p, "rev-parse", "--show-toplevel")
    try:
        return bool(top) and os.path.samefile(top, p)
    except OSError:
        return False

def runtimes():
    return sorted(d for d in os.listdir(ROOT) if d.startswith("Symoneural-"))

def _src_roots():
    for rt in runtimes():
        s = os.path.join(ROOT, rt, "src")
        if os.path.isdir(s):
            yield rt, s

def is_submodule(p):
    """True if p is a submodule work tree of some superproject (in-tree form).

    Representation-independent: a submodule's .git is a FILE while a standalone
    clone's is a DIRECTORY, but we never test that. git itself reports the
    superproject, which is authoritative for both forms."""
    return bool(git(p, "rev-parse", "--show-superproject-working-tree"))

def _pinned_component(dp):
    """dp is a pinned component if its computed pin store exists. A directory
    named `source` is only itself the component (bitbake layout) when it holds
    no `<category>` child - otherwise the child is the component and the pin
    with the category's name belongs to it."""
    rel = os.path.relpath(dp, ROOT)
    parts = rel.split("/")
    if parts[-1] == "source" and len(parts) >= 3 and os.path.isdir(os.path.join(dp, parts[2])):
        return False
    pin = pin_path(rel)
    return bool(pin) and os.path.isdir(pin)

def census_a():
    """METHOD A - filesystem candidate discovery.

    Walks each runtime's src/ and accepts a directory as a component if it
    carries a '.git' ENTRY validated by git (in-tree form, excluding submodules)
    OR if a pin store exists for it (ingested form). Descent stops at a component:
    nested submodules belong to submodule-lock, not here."""
    found = set()
    for rt, src in _src_roots():
        for dp, dn, fn in os.walk(src):
            entries = set(dn) | set(fn)        # capture BEFORE pruning: .git is
            dn[:] = sorted(d for d in dn if d not in SKIP_NAMES)   # in SKIP_NAMES
            if ".git" in entries and is_git_root(dp) and not is_submodule(dp):
                found.add(os.path.relpath(dp, ROOT)); dn[:] = []; continue
            if _pinned_component(dp):
                found.add(os.path.relpath(dp, ROOT)); dn[:] = []
    return found

def census_b():
    """METHOD B - independent census from the PIN STORES plus git's own view.

    Shares no discovery logic with METHOD A: it never looks for a '.git' entry
    under a component. Pinned components are enumerated from
    src/<cat>/.gitpins/<comp>.git and mapped back to their tree; not-yet-ingested
    components are found by asking git for each directory's work-tree top and
    keeping those that ARE their own top. The parent repository root is not a
    component - acquired trees are now inside the parent work tree - so meeting
    the parent top must NOT terminate the walk."""
    parent = os.path.realpath(ROOT)
    tops = set()
    for rt, src in _src_roots():
        for cat in sorted(os.listdir(src)):
            pins = os.path.join(src, cat, PINS_DIRNAME)
            if not os.path.isdir(pins):
                continue
            for entry in sorted(os.listdir(pins)):
                if not entry.endswith(".git") or entry.endswith(".submodules"):
                    continue
                comp = entry[:-4]
                cand = os.path.join(src, cat, "source", comp)
                if not os.path.isdir(cand) and comp == cat:
                    cand = os.path.join(src, cat, "source")
                if os.path.isdir(cand):
                    tops.add(os.path.relpath(cand, ROOT))
        for dp, dn, fn in os.walk(src):
            dn[:] = sorted(d for d in dn if d not in SKIP_NAMES)
            rel = os.path.relpath(dp, ROOT)
            if rel in tops:
                dn[:] = []                      # pinned component: do not descend
                continue
            top = git(dp, "rev-parse", "--show-toplevel")
            if not top:
                continue
            rp = os.path.realpath(top)
            if rp == parent:
                continue                       # parent repo: keep descending
            if os.path.samefile(rp, dp) and not is_submodule(dp):
                tops.add(rel)
                dn[:] = []
    return tops

def components():
    """Authoritative component list, derived from the agreed census."""
    out = []
    for rel in sorted(census_a()):
        parts = rel.split(os.sep)
        rt = parts[0].replace("Symoneural-", "")
        sub = parts[2:]                    # after <runtime>/src
        cat = sub[0] if sub else "UNKNOWN"
        name = sub[-1] if sub and sub[-1] != "source" else cat
        out.append({"runtime": rt, "category": cat, "component": name,
                    "source_path": rel, "abspath": os.path.join(ROOT, rel)})
    return out

_LOCK_SUBS = None
def _lock_submodules():
    """source_path -> set(submodule relpaths), from the authoritative lock.
    Recorded at ingest from upstream's gitlinks (tools/ingest-tree)."""
    global _LOCK_SUBS
    if _LOCK_SUBS is None:
        _LOCK_SUBS = {}
        try:
            for c in load("source-lock.json", base=AUTH_ACQ)["components"]:
                _LOCK_SUBS[c["source_path"]] = {s["path"] for s in c.get("submodules", [])}
        except Exception:
            pass
    return _LOCK_SUBS

def is_component_submodule(abspath):
    """True if abspath is a submodule of an acquired component: either it still
    carries its own .git entry (in-tree form) or the lock records it as a
    submodule path of the component that contains it (ingested form, where the
    files are committed content and the .git lives in the pin store)."""
    if os.path.exists(os.path.join(abspath, ".git")):
        return True
    rel = os.path.relpath(abspath, ROOT)
    for sp, subs in _lock_submodules().items():
        if rel.startswith(sp + "/") and rel[len(sp) + 1:] in subs:
            return True
    return False

def rebuilt_tree(treeish, children):
    """Hash of <treeish> after replacing each (relpath, commit_sha) in children
    with a 160000 gitlink - i.e. what upstream's tree looks like where ours holds
    submodule CONTENT. No index or object-store writes, even for nested trees."""
    from git_tree_identity import rebuilt_tree as reconstruct
    return reconstruct(ROOT, treeish, children)

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def dump(obj, name):
    """Deterministic serialisation: sorted keys, fixed separators, no timestamps."""
    os.makedirs(ACQ, exist_ok=True)
    with open(os.path.join(ACQ, name), "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")

def load(name, base=None):
    with open(os.path.join(base or ACQ, name)) as f:
        return json.load(f)
