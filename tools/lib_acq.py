#!/usr/bin/env python3
"""lib_acq.py - shared, deterministic primitives for the acquisition control plane.

Repository discovery never assumes a particular .git filesystem representation.
Git permits .git to be a directory OR a file (worktrees, submodules), so every
candidate is validated with git itself rather than by stat()-ing a path.
"""
import os, subprocess, hashlib, json

ROOT = "/home/google/SymonSaysLLC"
ACQ  = os.environ.get("ACQ_OUT") or os.path.join(ROOT, "acquisition")
GEN  = os.path.join(ROOT, "generated")
BOOT = os.path.expanduser("~/symoneural-bootstrap-master")

LOCKED_STACK = {
    "openembedded-core": "fe7a24bc67118e7e184b5f5247258715e3904e7c",
    "bitbake":           "046a90b0e9b7b914b7a95aec579cdc3fc9c7617a",
}

# Skip classes are by MEANING (build output / cache / vcs internals), never by depth.
SKIP_NAMES = {".git", "__pycache__", "node_modules"}
SKIP_PATH_MARKERS = ("/tmp/", "/tmp-glibc/", "/downloads/", "/sstate-cache",
                     "/build/devtool/", "/build/devtool-master/")

def git(d, *a, timeout=300):
    try:
        r = subprocess.run(["git", "-C", d, *a], capture_output=True,
                           text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
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
    """True if p is a submodule work tree of some superproject.

    Representation-independent: a submodule's .git is a FILE while a standalone
    clone's is a DIRECTORY, but we never test that. git itself reports the
    superproject, which is authoritative for both forms."""
    return bool(git(p, "rev-parse", "--show-superproject-working-tree"))

def census_a():
    """METHOD A - filesystem candidate discovery.

    Looks for a '.git' ENTRY (file or directory, both are legal), validates it
    with git rev-parse, then excludes submodules. Records top-level acquired
    sources only; nested submodules belong to submodule-lock."""
    found = set()
    for rt, src in _src_roots():
        for dp, dn, fn in os.walk(src):
            entries = set(dn) | set(fn)        # capture BEFORE pruning: .git is
            dn[:] = sorted(d for d in dn if d not in SKIP_NAMES)   # in SKIP_NAMES
            if ".git" in entries:
                if is_git_root(dp) and not is_submodule(dp):
                    found.add(os.path.relpath(dp, ROOT))
                    dn[:] = []
    return found

def census_b():
    """METHOD B - independent git-driven census.

    Shares no logic with METHOD A: it never looks for a '.git' entry. It asks git
    for the work-tree top of each directory and keeps those that ARE their own
    top. The parent repository root is explicitly not a component - acquired
    trees live inside the parent work tree but are not part of it - so finding
    the parent top must NOT terminate the walk."""
    parent = os.path.realpath(ROOT)
    tops = set()
    for rt, src in _src_roots():
        for dp, dn, fn in os.walk(src):
            dn[:] = sorted(d for d in dn if d not in SKIP_NAMES)
            top = git(dp, "rev-parse", "--show-toplevel")
            if not top:
                continue
            rp = os.path.realpath(top)
            if rp == parent:
                continue                       # parent repo: keep descending
            if os.path.samefile(rp, dp) and not is_submodule(dp):
                tops.add(os.path.relpath(rp, ROOT))
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
