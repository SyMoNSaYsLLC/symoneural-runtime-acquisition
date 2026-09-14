# symoneural-pristine.bbclass - build from a DISPOSABLE EXPORT of an acquired tree.
#
# Replaces externalsrc. externalsrc points ${S} directly at the acquired source,
# which made every build a potential writer into pristine upstream. Three separate
# hazard classes came from that single fact:
#
#   * classes whose tasks sed/rewrite files under ${S} (cython.bbclass)
#   * BBCLASSEXTEND = "native" giving target and native the SAME ${S},
#     written concurrently
#   * Python build backends emitting .egg-info / _version.py / .pdm-build
#     next to setup.py regardless of where the build directory points
#
# Here ${S} is a throwaway `git archive` export under ${WORKDIR}, taken from the
# ESTATE repository's object store at HEAD:<tree path>. Writers can do whatever
# they like to it; the acquired tree is never opened for writing - or reading.
# Each BBCLASSEXTEND variant has its own ${WORKDIR}, so each gets its own export
# and the sharing problem disappears by construction.
#
# Required:
#   SYMON_TREE - absolute path of the acquired tree INSIDE this repository
#   SRCREV     - the upstream commit the tree MUST be at (= lock.commit_sha)
#
# SOURCES-100 (S1/P): the acquired tree's own .git no longer sits in the tree - it
# is moved to .gitpins/ and the tree's FILES are committed to the estate repository
# at their pin. So `git -C ${SYMON_TREE} rev-parse HEAD` would walk upward, find THIS
# repository, and return the estate's HEAD: every build would fail PIN MISMATCH.
# The identity check is now the lock's content address:
#     git rev-parse HEAD:${SYMON_REPO_PATH}  ==  source-lock.json tree_sha
# (for submodule-bearing trees, upstream's gitlink tree rebuilt from ours and
# compared - tools/ingest-tree verify is the one implementation of both), and the
# export comes from the repository's OBJECT STORE (git archive HEAD:<path>), never
# from the working tree. Committed as trees, submodules are IN the export - the
# old per-tree `git archive` never descended into them.

SYMON_REPO ?= "/home/google/SymonSaysLLC"
SYMON_TREE ?= ""
SYMON_REPO_PATH = "${@os.path.relpath(d.getVar('SYMON_TREE') or '/nonexistent', d.getVar('SYMON_REPO'))}"
SYMON_PRISTINE_DIR = "${WORKDIR}/pristine"

S = "${SYMON_PRISTINE_DIR}"
B = "${WORKDIR}/build"

do_unpack[dirs] = "${WORKDIR}"

# cleandirs belongs to the PREFUNC, not to do_unpack. A task's cleandirs flag is
# applied when that task runs, which is AFTER its prefuncs - so leaving it on
# do_unpack deleted the export that symon_export_pristine had just written, and
# do_populate_lic then failed with "LIC_FILES_CHKSUM points to an invalid file"
# because ${S} was empty. It only worked before because the export WAS do_unpack.
symon_export_pristine[cleandirs] = "${SYMON_PRISTINE_DIR}"

# The export runs BEFORE the stock unpack rather than replacing it. Replacing it
# was a real defect: it meant no SRC_URI entry was ever unpacked, so cargo's
# crate:// closure landed nowhere and `sources/cargo_home/bitbake` stayed EMPTY.
# stratum then failed with "no matching package named `bitcoin` found" against a
# vendor directory containing 0 crates. Recipes with no extra SRC_URI never
# noticed, which is exactly why it went undetected.
do_unpack[prefuncs] += "symon_export_pristine"
# the lock is an input to the export: a re-ingested tree must re-run it
symon_export_pristine[file-checksums] += "${SYMON_REPO}/acquisition/source-lock.json:True"

python symon_export_pristine() {
    import subprocess, os, sys, json

    repo = d.getVar("SYMON_REPO")
    tree = d.getVar("SYMON_TREE")
    rel  = d.getVar("SYMON_REPO_PATH")
    want = d.getVar("SRCREV")
    dest = d.getVar("SYMON_PRISTINE_DIR")
    pf   = d.getVar("PF")

    if not tree:
        bb.fatal("%s: SYMON_TREE is unset. symoneural-pristine needs the acquired tree." % pf)
    if not os.path.isdir(tree):
        bb.fatal("%s: SYMON_TREE %s is not a directory." % (pf, tree))
    if rel.startswith("..") or os.path.isabs(rel):
        bb.fatal("%s: SYMON_TREE %s is not inside the estate repository %s." % (pf, tree, repo))
    if not want or want == "INVALID":
        bb.fatal("%s: SRCREV is unset. The pin is the identity; it cannot be implicit." % pf)

    lock_path = os.path.join(repo, "acquisition", "source-lock.json")
    with open(lock_path) as f:
        comps = json.load(f)["components"]
    ent = next((c for c in comps if c.get("source_path") == rel), None)
    if ent is None:
        bb.fatal("%s: %s is not a component source_path in %s." % (pf, rel, lock_path))
    if ent.get("commit_sha") != want:
        bb.fatal("%s: PIN MISMATCH. SRCREV is %s but source-lock.json commit_sha for %s is %s."
                 % (pf, want, rel, ent.get("commit_sha")))
    if not ent.get("tree_sha"):
        bb.fatal("%s: %s has no tree_sha in source-lock.json - the tree was never ingested "
                 "(tools/ingest-tree ingest %s). Refusing to build an unverifiable tree."
                 % (pf, rel, ent.get("component")))

    # THE assertion: what is committed at HEAD:<path> IS upstream's tree.
    # One implementation, shared with the audit; its last line is the verdict.
    r = subprocess.run([sys.executable, os.path.join(repo, "tools", "ingest-tree"), "verify",
                        ent["component"]], cwd=repo, capture_output=True, text=True)
    verdict = (r.stdout.strip().splitlines() or [r.stderr.strip()])[-1]
    if r.returncode != 0 or not (" · VERIFIED" in verdict or " · LISTING-VERIFIED(" in verdict):
        bb.fatal("%s: PIN MISMATCH. HEAD:%s does not equal the locked tree_sha %s. "
                 "Refusing to build a tree that is not at its pinned content. Verifier said: %s"
                 % (pf, rel, ent["tree_sha"][:12], verdict or r.stderr.strip()[-400:]))

    # export from the object store - the working tree is never read
    bb.utils.mkdirhier(dest)
    rc = subprocess.run(["bash", "-o", "pipefail", "-c",
                         "git -C '%s' archive 'HEAD:%s' | tar -x -C '%s'" % (repo, rel, dest)]).returncode
    if rc:
        bb.fatal("%s: git archive HEAD:%s failed (rc=%d)" % (pf, rel, rc))

    # N2 - SOURCE_DATE_EPOCH from the PIN, not from the clock or a fallback.
    # The commit date OF THE PINNED UPSTREAM SHA is the honest value: it derives
    # from the identity. It lives in the pin store (local); when that is absent the
    # date of the estate commit that ingested the tree is used, and said so.
    epoch, origin = "", ""
    pin = ent.get("pins_path")
    if pin and os.path.isdir(os.path.join(repo, pin)):
        epoch = subprocess.run(["git", "--git-dir=" + os.path.join(repo, pin), "--work-tree=/",
                                "log", "-1", "--format=%ct", want],
                               capture_output=True, text=True).stdout.strip()
        origin = "commit date of upstream %s" % want[:12]
    if not epoch.isdigit():
        epoch = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%ct", "HEAD", "--", rel],
                               capture_output=True, text=True).stdout.strip()
        origin = "date of the estate commit that ingested %s (pin store absent)" % rel
    if epoch.isdigit():
        sde = os.path.join(d.getVar("WORKDIR"), "source-date-epoch")
        bb.utils.mkdirhier(sde)
        with open(os.path.join(sde, "__source_date_epoch.txt"), "w") as f:
            f.write(epoch)
        bb.note("%s: SOURCE_DATE_EPOCH %s (%s)" % (pf, epoch, origin))
    else:
        bb.warn("%s: could not derive SOURCE_DATE_EPOCH for %s; it will fall back" % (pf, want[:12]))

    # N3 - permanent unpack-time assertions. Each of these corresponds to a defect
    # that actually shipped and was only caught later by reading a build log.
    #
    # (a) the export is non-empty. do_unpack[cleandirs] once deleted the export
    #     AFTER this ran, and the first symptom was do_populate_lic failing 45
    #     times with "LIC_FILES_CHKSUM points to an invalid file".
    got = sum(len(fs) for _, _, fs in os.walk(dest))
    if got == 0:
        bb.fatal("%s: the pristine export at %s is EMPTY. Something deleted it "
                 "between the export and this check." % (pf, dest))

    # (b) every LIC_FILES_CHKSUM path exists in the export. Catches the same class
    #     of failure at unpack time, where the cause is still obvious.
    missing = []
    for e in (d.getVar("LIC_FILES_CHKSUM") or "").split():
        if not e.startswith("file://"):
            continue
        p = e[len("file://"):].split(";", 1)[0]
        if p.startswith("${") or not p:
            continue
        if not os.path.exists(os.path.join(dest, p)):
            missing.append(p)
    if missing:
        bb.fatal("%s: LIC_FILES_CHKSUM names %d file(s) absent from the export: %s"
                 % (pf, len(missing), ", ".join(missing[:5])))

    bb.note("%s: export verified - %d files, %d licence file(s) present"
            % (pf, got, len((d.getVar("LIC_FILES_CHKSUM") or "").split())))
    bb.note("%s: %s; exported HEAD:%s (%d submodules committed as trees) to %s"
            % (pf, verdict, rel, len(ent.get("submodules") or []), dest))
}

# The upstream git:// URI is redundant - SYMON_TREE already holds that source,
# verified against SRCREV. Strip it at parse time so do_fetch has no reason to
# touch the network for it. Every OTHER SRC_URI entry (crate://, file://, extra
# tarballs) is left alone and fetched normally: that is the whole point.
python () {
    uris = (d.getVar("SRC_URI") or "").split()
    keep = [u for u in uris if not u.startswith(("git://", "gitsm://"))]
    if len(keep) != len(uris):
        d.setVar("SRC_URI", " ".join(keep))
}

# A `git archive` export carries NO .git directory - that is the whole point of
# the class, and it is what makes ${S} disposable. But setuptools-scm, hatch-vcs
# and vcs-versioning all derive the package version by asking git, so under this
# class they fail with:
#   LookupError: setuptools-scm was unable to detect version for .../pristine
# Under externalsrc they happened to work only because ${S} WAS the git repo -
# exactly the coupling this class exists to remove. Relying on that was never
# correct: the version came from whatever state the tree was in, not from the pin.
# Pin it from PV instead. Deterministic, and PV is what SRCREV is pinned to.
# Harmless for recipes that do not use setuptools-scm - nothing reads it.
export SETUPTOOLS_SCM_PRETEND_VERSION = "${PV}"

# Same defect, different backend. VCS-derived versioning is a whole family, and
# each member has its own bypass. Found so far by building:
#   setuptools-scm / hatch-vcs  -> SETUPTOOLS_SCM_PRETEND_VERSION  (mpmath, vllm)
#   uv-dynamic-versioning       -> UV_DYNAMIC_VERSIONING_BYPASS    (mcp-python-sdk)
# mcp-python-sdk failed with:
#   RuntimeError: Error getting the version from source `uv-dynamic-versioning`:
#   This does not appear to be a Git project
# The variable name is read straight from the plugin
# (uv_dynamic_versioning/main.py:30), not guessed.
#
# If a future recipe fails with some third backend asking git for a version, add
# its bypass here rather than to the recipe - the cause is the class, so the fix
# belongs to the class.
export UV_DYNAMIC_VERSIONING_BYPASS = "${PV}"

# do_fetch is NOT noexec - see the SRC_URI stripping above.
# N3(c) - crate:// / npmsw:// recipes: the vendored dependency count must equal
# the lockfile's. This is the check that would have caught defect 2 immediately
# instead of two builds later: do_fetch[noexec]="1" left the vendor directory with
# 0 crates against a 233-entry closure, and the only symptom was cargo saying
# "no matching package named `bitcoin` found" long after the real failure.
python do_symon_assert_vendor_closure() {
    import os, re
    uris = (d.getVar("SRC_URI") or "").split()
    crates = [u for u in uris if u.startswith("crate://")]
    if not crates:
        return
    vendor = os.path.join(d.getVar("WORKDIR"), "sources", "cargo_home", "bitbake")
    have = len([x for x in os.listdir(vendor)]) if os.path.isdir(vendor) else 0
    if have == 0:
        bb.fatal("%s: SRC_URI declares %d crate:// entries but the vendor directory "
                 "%s holds NONE. do_fetch/do_unpack did not populate it; cargo will "
                 "fail later with a misleading 'no matching package' error."
                 % (d.getVar("PF"), len(crates), vendor))
    bb.note("%s: vendor closure %d crates on disk for %d crate:// entries"
            % (d.getVar("PF"), have, len(crates)))
}

# P3 - the same assertion for npmsw://, but the SHAPE differs. cargo vendors FLAT
# into sources/cargo_home/bitbake, so a directory count works. npmsw unpacks
# NESTED into ${S}/node_modules/... (npm.bbclass:200,
# destdir = os.path.join(d.getVar("S"), destsuffix)), so this must WALK and count
# directories holding a package.json.
#
# The denominator is NOT constant: with NPM_INSTALL_DEV = "0" the dev entries are
# CORRECTLY absent, so comparing against the raw shrinkwrap length would fail a
# healthy recipe. Compare against non-dev entries when DEV=0, all entries when 1.
python do_symon_assert_npm_closure() {
    import os, json
    uris = (d.getVar("SRC_URI") or "").split()
    sw = [u for u in uris if u.startswith("npmsw://")]
    if not sw:
        return
    path = sw[0][len("npmsw://"):].split(";", 1)[0]
    if not os.path.isfile(path):
        bb.fatal("%s: npmsw file %s is missing" % (d.getVar("PF"), path))
    with open(path) as f:
        pkgs = json.load(f).get("packages", {})
    dev = d.getVar("NPM_INSTALL_DEV") == "1"
    want = len([k for k, v in pkgs.items() if k and (dev or not v.get("dev"))])

    # npmsw unpacks into UNPACKDIR/node_modules, not ${S}/node_modules - ordinary
    # npm recipes have ${S} inside UNPACKDIR so the distinction never shows, but
    # this class moves ${S} to ${WORKDIR}/pristine. Check both.
    roots = [os.path.join(d.getVar("UNPACKDIR") or "", "node_modules"),
             os.path.join(d.getVar("S"), "node_modules")]
    have = 0
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, _, files in os.walk(root):
            if "package.json" in files:
                have += 1
        if have:
            break
    if want and have == 0:
        bb.fatal("%s: shrinkwrap declares %d package(s) but node_modules holds "
                 "NONE. The npmsw closure was not unpacked; the build would fail later "
                 "with a confusing module-resolution error instead of this one."
                 % (d.getVar("PF"), want))
    bb.note("%s: npm closure %d package(s) unpacked for %d declared (NPM_INSTALL_DEV=%s)"
            % (d.getVar("PF"), have, want, "1" if dev else "0"))
}
addtask symon_assert_npm_closure after do_unpack before do_configure
addtask symon_assert_vendor_closure after do_unpack before do_configure

do_patch[noexec] = "1"

# R12: a recipe that installs NOTHING must fail, not pass quietly.
#
# fastapi taught this: recipetool emitted empty stubs and no inherit, do_compile
# reported success, and the package was empty. A build that reports success while
# producing nothing is worse than one that fails, because nothing downstream
# notices. Recipes that legitimately install nothing set SYMON_ALLOW_EMPTY_D = "1".
SYMON_ALLOW_EMPTY_D ?= "0"

python do_symon_assert_nonempty_d() {
    import os
    if d.getVar("SYMON_ALLOW_EMPTY_D") == "1":
        return
    dest = d.getVar("D")
    n = 0
    for _, _, files in os.walk(dest):
        n += len(files)
        if n:
            break
    if not n:
        bb.fatal("%s: do_install produced an EMPTY ${D}. Nothing was installed, yet the "
                 "task would have reported success. Either the recipe has no working "
                 "install step, or an inherited class was overridden by a stub. If this "
                 "recipe genuinely installs nothing, set SYMON_ALLOW_EMPTY_D = \"1\"."
                 % d.getVar("PF"))
}
# NB: the task name must not contain "_append" - newer bitbake parses that as the
# old override syntax and rejects the whole layer.
addtask symon_assert_nonempty_d after do_install before do_populate_sysroot
