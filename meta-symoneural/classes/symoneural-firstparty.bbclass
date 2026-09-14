# symoneural-firstparty - build FIRST-PARTY code from the estate repository's object
# store, the way symoneural-pristine builds acquired trees.
#
#   SYMON_FP_PATH  - path of the first-party source directory inside the estate
#                    repository (e.g. Symoneural-API/app)
#
# Identity is the TREE id of HEAD:<SYMON_FP_PATH>, computed at parse time. Two
# consequences that are the point of the class:
#   - ${S} is `git archive <tree>` of what is COMMITTED. An uncommitted edit in the
#     working tree is not built; commit discipline is enforced by construction.
#   - the task hashes depend on that tree id, so a change to the subtree rebuilds
#     the recipe and a change anywhere else in the estate does not.
# SOURCE_DATE_EPOCH is the date of the last estate commit that touched the path.
#
# No SRC_URI, no network: there is nothing to fetch.

SYMON_REPO ?= "/home/google/SymonSaysLLC"
SYMON_FP_PATH ?= ""
SYMON_FP_DIR = "${WORKDIR}/firstparty"

S = "${SYMON_FP_DIR}"
B = "${WORKDIR}/build"

# the tree id is read from the repository at parse time; never serve a cached
# parse whose id is stale
BB_DONT_CACHE = "1"

python () {
    import subprocess, os
    repo, rel = d.getVar("SYMON_REPO"), d.getVar("SYMON_FP_PATH")
    pf = d.getVar("PF")
    if not rel:
        bb.fatal("%s: SYMON_FP_PATH is unset. symoneural-firstparty needs the source path." % pf)
    if not os.path.isdir(os.path.join(repo, rel)):
        bb.fatal("%s: %s/%s is not a directory." % (pf, repo, rel))
    r = subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "-q", "HEAD:%s" % rel],
                       capture_output=True, text=True)
    tree = r.stdout.strip()
    if r.returncode != 0 or len(tree) != 40:
        bb.fatal("%s: HEAD:%s is not a committed tree in %s. Commit the first-party source "
                 "before building it; the working tree is never built." % (pf, rel, repo))
    d.setVar("SYMON_FP_TREE", tree)
    # the ref and HEAD are parse inputs
    for f in (".git/HEAD", ".git/packed-refs"):
        p = os.path.join(repo, f)
        if os.path.exists(p):
            bb.parse.mark_dependency(d, p)
    head = subprocess.run(["git", "-C", repo, "symbolic-ref", "-q", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    if head:
        p = os.path.join(repo, ".git", head)
        if os.path.exists(p):
            bb.parse.mark_dependency(d, p)
}

do_unpack[dirs] = "${WORKDIR}"
symon_export_firstparty[cleandirs] = "${SYMON_FP_DIR}"
do_unpack[prefuncs] += "symon_export_firstparty"

python symon_export_firstparty() {
    import subprocess, os
    repo, rel = d.getVar("SYMON_REPO"), d.getVar("SYMON_FP_PATH")
    tree, dest, pf = d.getVar("SYMON_FP_TREE"), d.getVar("SYMON_FP_DIR"), d.getVar("PF")

    bb.utils.mkdirhier(dest)
    rc = subprocess.run(["bash", "-o", "pipefail", "-c",
                         "git -C '%s' archive '%s' | tar -x -C '%s'" % (repo, tree, dest)]).returncode
    if rc:
        bb.fatal("%s: git archive %s (HEAD:%s) failed (rc=%d)" % (pf, tree[:12], rel, rc))

    got = sum(len(fs) for _, _, fs in os.walk(dest))
    if got == 0:
        bb.fatal("%s: the first-party export at %s is EMPTY." % (pf, dest))

    epoch = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%ct", "HEAD", "--", rel],
                           capture_output=True, text=True).stdout.strip()
    if epoch.isdigit():
        sde = os.path.join(d.getVar("WORKDIR"), "source-date-epoch")
        bb.utils.mkdirhier(sde)
        with open(os.path.join(sde, "__source_date_epoch.txt"), "w") as f:
            f.write(epoch)
        bb.note("%s: SOURCE_DATE_EPOCH %s (last estate commit touching %s)" % (pf, epoch, rel))
    else:
        bb.warn("%s: could not derive SOURCE_DATE_EPOCH for %s" % (pf, rel))

    # the identity travels with the package so an installed root can say what it is
    with open(os.path.join(dest, "SOURCE-TREE"), "w") as f:
        f.write("%s HEAD:%s\n" % (tree, rel))
    bb.note("%s: exported tree %s (HEAD:%s), %d files, to %s" % (pf, tree[:12], rel, got, dest))
}

# VCS-derived versioning has no git to ask under an archive export (see
# symoneural-pristine); first-party pyprojects must declare their version.
export SETUPTOOLS_SCM_PRETEND_VERSION = "${PV}"
