# Repository layout, and the clone that ended up inside the repository

**17 September 2026.** Garrett: *"SymonSaysLLC was originally a repo and then we created
the runtime acquisition repo, i cloned the runtime acquisition folder into the symonsaysllc
folder and i probably shouldnt have. Do what is most professional and organized to mitigate
that error i made."*

---

## 1. The finding: there is one repository, not two

The description says two repositories. Disk says one repository with two checkouts.

```
$ git -C /home/google/SymonSaysLLC remote get-url origin
git@github.com:SyMoNSaYsLLC/symoneural-runtime-acquisition.git

$ git -C /home/google/symoneural-runtime-acquisition-github-769b4f3ae remote get-url origin
https://github.com/SyMoNSaYsLLC/symoneural-runtime-acquisition.git
```

Same GitHub repository — `SyMoNSaYsLLC/symoneural-runtime-acquisition` — reached over SSH
from the working tree and over HTTPS by the clone. So `SymonSaysLLC/` **is** the runtime
acquisition repository; the clone placed inside it was a second, older checkout of itself.

That reframes the whole thing. There was never a two-repository merge problem to solve.
There was a duplicate checkout to remove, and the only real question was whether it held
anything the working tree did not.

## 2. It held nothing unique — four commands, not an inference

| Question | Command | Result |
|---|---|---|
| Does it have work the main tree lacks? | `git -C <clone> rev-list 769b4f3ae --not <main>/HEAD` | **empty** |
| Is its HEAD contained in the main tree? | `git -C <main> merge-base --is-ancestor 769b4f3ae HEAD` | **rc=0**, main is **42 commits** ahead (at the 17 Sep evidence capture; it only grows) |
| Any branches, stashes, dirty files? | `for-each-ref` / `stash list` / `status --porcelain` | one ref `main`, **no stash**, **pristine tree** |
| Anything orphaned by a reset or amend? | `git -C <clone> fsck --unreachable --dangling --no-reflogs` | **rc=0, no output** |

And the reflog closes it — the clone was never worked in at all:

```
769b4f3ae refs/heads/main@{0}: clone: from https://github.com/SyMoNSaYsLLC/...
769b4f3ae refs/remotes/origin/HEAD@{0}: clone: ...
769b4f3ae HEAD@{0}: clone: ...
```

Three entries, all `clone:`. No commit, no reset, no amend, no fetch.

`fsck` is in that table on purpose: `rev-list` only walks *reachable* objects, so on its own
it cannot authorise deleting 5.6 GB. `fsck --unreachable` is what rules out an orphan.

## 3. What was done, and what was not

**Moved, not deleted** (estate rule: never delete his files; move and say where):

```
was:  /home/google/SymonSaysLLC/symoneural-runtime-acquisition/
now:  /home/google/symoneural-runtime-acquisition-github-769b4f3ae/   (5.6 GB, HEAD 769b4f3ae)
```

The name carries the commit so the directory says what it is without being opened.

**Never in history.** `git log --all -- 'symoneural-runtime-acquisition*'` is empty and no
tracked path matches; there is no gitlink (mode `160000`) in the index, no `.git/modules`,
and no submodule configuration. The nested clone never reached a commit, so nothing has to
be rewritten and nothing leaked into the pack that is pushed.

**Not done, deliberately:** the working tree was **not** renamed to match the repository
name. `SymonSaysLLC/` is referenced by absolute path in `bblayers.conf` for every runtime,
in `SYMON_TREE` in every pristine recipe, and in the fstab mount for `models/`. Renaming it
is a structural change nobody asked for, on a tree 42 commits ahead of origin. Recorded as
an observation; stopped there.

## 4. The 5.6 GB is Garrett's to delete

It is provably redundant, and it is still his. The command is written out in
`~/Desktop/github/2026-09-17-redundant-clone-removal.md` rather than run here.

## 5. So it cannot happen silently again

`tools/pre-publish-audit.sh` gained check 9, **"git repositories nested in this worktree"**.

The rule it enforces: *a nested repository must be denied by `.gitignore`, or the audit
fails.* Being in `.gitignore` is the record that it is on purpose — and it is also what
stops a forbidden `git add .` from sweeping a second copy of the estate into a commit.
Today that is one line, `FENCED FreeToken`, which is the 6.8 GB working clone deliberately
left in place because its console scripts carry absolute shebangs into that path.

Two things the check does **not** do, both learned the hard way:

- **It does not `find` the whole tree.** That takes 7.5 s and reports thousands of upstream
  `.git` directories that bitbake unpacks under `*/build/*/tmp/work/`. It scans the top
  level (where the mistake actually landed) plus every untracked, non-ignored path — which
  is exactly the set `git add .` could reach. Audit runtime is unchanged at ~16 s.
- **It does not read `.gitmodules`.** Inside this sandbox `.gitmodules` is a character
  special device (a bubblewrap `/dev/null` bind-mount) and `git config -f .gitmodules`
  returns *Permission denied*. A check that read it would fail forever on a file that does
  not exist outside the sandbox.

And it takes its exit status directly (`rc=$?` after the command), never through a pipe —
the same R16 discipline as the rest of the script.

**Proven both ways, today:**

| Case | Result |
|---|---|
| Clean tree | `git repositories nested in this worktree   1 fenced, informational` → **AUDIT PASS, rc=0** |
| `git init zz-audit-selftest-nested` at the top level | `HAZARD zz-audit-selftest-nested - nested repository at the top level, NOT ignored` → **AUDIT FAIL, rc=1** |

The throwaway repository created for the negative test was removed in the same command.

## 6. The layout rule going forward

One repository, one working tree: `/home/google/SymonSaysLLC`, origin
`SyMoNSaYsLLC/symoneural-runtime-acquisition`.

- Need a second checkout of the estate? Put it **beside** the tree, never inside:
  `~/symoneural-<purpose>-<sha>/`. Or use `git worktree add ../<name>`, which shares one
  object store instead of copying 5.6 GB.
- Need a third-party working clone inside the tree (the FreeToken case)? Add the deny to
  `.gitignore` in the same change that creates it, with a comment saying why it is in here
  rather than outside. The audit then reports it as FENCED and passes.
- Anything else nested fails the audit before it can reach a push.
