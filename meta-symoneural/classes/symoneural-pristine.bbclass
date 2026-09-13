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
do_unpack[cleandirs] = "${SYMON_PRISTINE_DIR}"
do_unpack[network] = "0"

python do_unpack() {
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

# There is nothing to fetch: the tree is already acquired and verified.
do_fetch[noexec] = "1"
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
