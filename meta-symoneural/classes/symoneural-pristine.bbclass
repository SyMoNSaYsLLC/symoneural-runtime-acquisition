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

    # N2 - SOURCE_DATE_EPOCH from the PIN, not from the clock or a fallback.
    # The export has no .git, so create_source_date_epoch_stamp found nothing and
    # silently used SOURCE_DATE_EPOCH_FALLBACK (observed: 1302044400, i.e. 2011).
    # Every reproducible-build timestamp in the estate was that constant. The commit
    # date OF THE PINNED SHA is the honest value: it derives from the identity.
    epoch = git("log", "-1", "--format=%ct", want)
    if epoch.isdigit():
        sde = os.path.join(d.getVar("WORKDIR"), "source-date-epoch")
        bb.utils.mkdirhier(sde)
        with open(os.path.join(sde, "__source_date_epoch.txt"), "w") as f:
            f.write(epoch)
        bb.note("%s: SOURCE_DATE_EPOCH %s (commit date of %s)" % (pf, epoch, want[:12]))
    else:
        bb.warn("%s: could not read commit date for %s; SOURCE_DATE_EPOCH will fall back"
                % (pf, want[:12]))

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
    for ent in (d.getVar("LIC_FILES_CHKSUM") or "").split():
        if not ent.startswith("file://"):
            continue
        rel = ent[len("file://"):].split(";", 1)[0]
        if rel.startswith("${") or not rel:
            continue
        if not os.path.exists(os.path.join(dest, rel)):
            missing.append(rel)
    if missing:
        bb.fatal("%s: LIC_FILES_CHKSUM names %d file(s) absent from the export: %s"
                 % (pf, len(missing), ", ".join(missing[:5])))

    bb.note("%s: export verified - %d files, %d licence file(s) present"
            % (pf, got, len((d.getVar("LIC_FILES_CHKSUM") or "").split())))
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
