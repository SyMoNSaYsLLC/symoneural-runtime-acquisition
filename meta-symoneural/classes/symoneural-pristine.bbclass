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
# Here ${S} is a throwaway `git archive` export under ${WORKDIR}. Writers can do
# whatever they like to it; the acquired tree is never opened for writing at all.
# Each BBCLASSEXTEND variant has its own ${WORKDIR}, so each gets its own export
# and the sharing problem disappears by construction.
#
# Required:
#   SYMON_TREE - absolute path to the acquired git tree
#   SRCREV     - the commit the tree MUST be at

SYMON_TREE ?= ""
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

python symon_export_pristine() {
    import subprocess, os

    tree = d.getVar("SYMON_TREE")
    want = d.getVar("SRCREV")
    dest = d.getVar("SYMON_PRISTINE_DIR")
    pf   = d.getVar("PF")

    if not tree:
        bb.fatal("%s: SYMON_TREE is unset. symoneural-pristine needs the acquired tree." % pf)
    if not os.path.isdir(os.path.join(tree, ".git")) and not os.path.isfile(os.path.join(tree, ".git")):
        bb.fatal("%s: SYMON_TREE %s is not a git work tree." % (pf, tree))
    if not want or want == "INVALID":
        bb.fatal("%s: SRCREV is unset. The pin is the identity; it cannot be implicit." % pf)

    def git(*a):
        return subprocess.run(("git", "-C", tree) + a, capture_output=True,
                              text=True).stdout.strip()

    have = git("rev-parse", "HEAD")
    if have != want:
        # The whole point of the class: a tree that has drifted from its pin must
        # not build. Silently building the wrong commit is the failure this prevents.
        bb.fatal("%s: PIN MISMATCH. %s is at %s but SRCREV says %s. "
                 "Refusing to build a tree that is not at its pinned revision."
                 % (pf, tree, have or "<unknown>", want))

    bb.utils.mkdirhier(dest)
    # Export the tree itself...
    rc = subprocess.run("git -C %s archive HEAD | tar -x -C %s" % (tree, dest),
                        shell=True).returncode
    if rc:
        bb.fatal("%s: git archive of %s failed (rc=%d)" % (pf, tree, rc))

    # ...then every INITIALISED submodule at its own path. git archive does not
    # recurse into submodules, so each is exported separately or the export is
    # silently incomplete.
    n = 0
    out = subprocess.run(("git", "-C", tree, "submodule", "status", "--recursive"),
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        if not line.strip() or line[0] == "-":
            continue                      # "-" = not initialised, nothing to export
        parts = line[1:].split()
        if len(parts) < 2:
            continue
        sp = parts[1]
        sub = os.path.join(tree, sp)
        tgt = os.path.join(dest, sp)
        if not os.path.isdir(sub):
            continue
        bb.utils.mkdirhier(tgt)
        rc = subprocess.run("git -C %s archive HEAD | tar -x -C %s" % (sub, tgt),
                            shell=True).returncode
        if rc:
            bb.fatal("%s: git archive of submodule %s failed (rc=%d)" % (pf, sp, rc))
        n += 1

    bb.note("%s: exported pristine tree at %s (+%d submodules) to %s"
            % (pf, want[:12], n, dest))
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
do_patch[noexec] = "1"

# R12: a recipe that installs NOTHING must fail, not pass quietly.
#
# fastapi taught this: recipetool emitted empty stubs and no inherit, do_compile
# reported success, and the package was empty. A build that reports success while
# producing nothing is worse than one that fails, because nothing downstream
# notices. Recipes that legitimately install nothing set SYMON_ALLOW_EMPTY_D = "1".
SYMON_ALLOW_EMPTY_D ?= "0"

python symon_assert_nonempty_d() {
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
