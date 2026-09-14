"""Reconstruct upstream Git tree identities in memory; no index/object writes."""
import hashlib
import os
import re
import subprocess


class TreeIdentityError(RuntimeError):
    pass


def rebuilt_tree(root, treeish, children):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1")

    def git(*args):
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, env=env)
        if result.returncode:
            raise TreeIdentityError("git " + args[0] + " failed (rc=" + str(result.returncode) + ")")
        return result.stdout

    oid = git("rev-parse", "--verify", treeish).decode().strip()
    if not re.fullmatch("[0-9a-f]{40}", oid):
        raise TreeIdentityError("expected a SHA-1 Git tree identity")
    replacements = dict(children)
    if len(replacements) != len(children):
        raise TreeIdentityError("duplicate submodule replacement")
    for path, commit in replacements.items():
        if any(p in {"", ".", ".."} for p in path.split("/")) or not re.fullmatch("[0-9a-f]{40}", commit):
            raise TreeIdentityError("invalid submodule replacement")

    def visit(tree, changes):
        if not changes:
            return tree
        data = git("cat-file", "tree", tree)
        if hashlib.sha1(b"tree " + str(len(data)).encode() + b"\0" + data).hexdigest() != tree:
            raise TreeIdentityError("tree object hash mismatch")
        entries, found, pos = [], set(), 0
        while pos < len(data):
            space = data.index(b" ", pos)
            zero = data.index(b"\0", space + 1)
            mode, name = data[pos:space], data[space + 1:zero]
            sha = data[zero + 1:zero + 21].hex()
            pos = zero + 21
            text = name.decode("utf-8", "surrogateescape")
            if text in changes:
                mode, sha = b"160000", changes[text]
                found.add(text)
            else:
                inner = {p[len(text) + 1:]: v for p, v in changes.items() if p.startswith(text + "/")}
                if inner:
                    if mode != b"40000":
                        raise TreeIdentityError("submodule ancestor is not a directory")
                    sha = visit(sha, inner)
                    found.update(text + "/" + p for p in inner)
            entries.append((mode, name, sha))
        if found != set(changes):
            raise TreeIdentityError("recorded submodule path is missing from committed tree")
        entries.sort(key=lambda entry: entry[1] + (b"/" if entry[0] == b"40000" else b""))
        data = b"".join(mode + b" " + name + b"\0" + bytes.fromhex(sha) for mode, name, sha in entries)
        return hashlib.sha1(b"tree " + str(len(data)).encode() + b"\0" + data).hexdigest()

    return visit(oid, replacements)
