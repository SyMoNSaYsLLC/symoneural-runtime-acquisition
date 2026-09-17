#!/bin/bash
# pre-publish-audit.sh - run BEFORE any push to a remote.
#
# Treat this repository as if it were public even while it is private: once
# published it is forked, cached and archived, and going private afterwards
# undoes none of that.
#
# Exit 0 = safe to push. Exit 1 = something must be fixed first.
#
# R16 note (2026-09-15): a checker that breaks must never read as "clean". Every
# check below is a function ending in `_pipe_rc "${PIPESTATUS[@]}"`, which looks at
# EVERY stage of the pipeline, not just the last one: a grep that matched nothing
# is status 1 and fine; any stage at 2 or above (git error, bad regex, python
# exception, unreadable source-lock.json) means the checker itself failed, and
# that is reported as CHECK BROKEN and counted as a FAIL with its stderr shown.
# The old `hits=$(... || true)` form turned all of those into "clean" - the
# silent-pass class this estate forbids. (`set -o pipefail` alone is not enough:
# it reports the RIGHTMOST non-zero stage, so git failing at 128 behind a grep
# that returned 1 still came back as 1.)
cd "$(dirname "$0")/.." || exit 1
fail=0
say() { printf '%-52s %s\n' "$1" "$2"; }
errf=$(mktemp "${TMPDIR:-/tmp}/pre-publish-audit.XXXXXX") || exit 1
trap 'rm -f "$errf"' EXIT

# _pipe_rc STATUS... - 0 if every stage exited 0 or 1, else the highest status.
_pipe_rc() { local m=0 s; for s in "$@"; do [ "$s" -gt "$m" ] && m=$s; done; [ "$m" -le 1 ] && return 0; return "$m"; }

# run LABEL FUNC - run FUNC in a subshell, capture stdout in $out and its status
# in $rc. Returns 1 (and records a FAIL) if the checker itself broke.
run() {
    out=$( "$2" 2>"$errf" ); rc=$?
    if [ "$rc" -ge 2 ]; then
        say "$1" "CHECK BROKEN (rc=$rc) - counts as FAIL"
        sed 's/^/    stderr: /' "$errf" | head -5
        fail=1
        return 1
    fi
    return 0
}
# report LABEL OK-WORD [MAXLINES] - after run: hits -> FAIL and print them, none -> OK-WORD
report() {
    if [ -n "$out" ]; then say "$1" "FAIL"; echo "$out" | head -n "${3:-20}"; fail=1
    else say "$1" "$2"; fi
}

# Acquired upstream trees are committed at their pin and verified byte-identical
# to upstream (tools/ingest-tree verify). A tree identical to upstream cannot hold
# a secret of OURS, and upstream test fixtures (librespot, httpx, gstreamer,
# workerd ship test keys and .env samples) would flood the scan with false
# positives that hide a real hit. So the secret and weight scans cover everything
# EXCEPT those paths, and a separate check proves every such path IS a verified
# pin - an unverified tree gets no exemption.
SRC_RE='^Symoneural-[^/]+/src/[^/]+/source/'
NOT_SRC=':(exclude,glob)Symoneural-*/src/*/source/**'
NOT_SELF=':(exclude)tools/pre-publish-audit.sh'

SECRET_NAME_RE='\.env$|\.pem$|\.key$|\.p12$|id_rsa|id_ed25519|\.netrc|credentials\.|developer_settings\.json$|\.npmrc$|\.pypirc$'
# Content shapes. Each requires a VALUE, so a document that names the key (or this
# script) does not match itself. inferenceGatewayApiKey is the one live key on this
# host (~/.config/Claude/developer_settings.json) and the reason `git add .` is banned.
# Checked against tools/ docs/ meta-symoneural/ generated/ acquisition/ config/ and
# the two first-party app trees on 2026-09-15: zero matches, so a hit is a real hit.
SECRET_CONTENT_RE='inferenceGatewayApiKey"?[[:space:]]*:[[:space:]]*"[^"]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}|hf_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}|(SMTP_PASS|SYM_[A-Z_]*TOKEN|TUNNEL_TOKEN|CLIENT_SECRET|ACCOUNTS_SECRET)[[:space:]]*=[[:space:]]*["'"'"']?[A-Za-z0-9+/_-]{12,}'
WEIGHT_RE='\.(gguf|safetensors|onnx|ckpt|pt|pth|h5|tflite|npz|msgpack|engine)$|(^|/)ggml-[^/]*\.bin$|(^|/)(pytorch_model|model|consolidated)([._-][0-9]+-of-[0-9]+)?\.bin$'

# 1. no secret-bearing filenames tracked, now or ever (renames included: no --diff-filter)
c1() { git log --all --pretty=format: --name-only | sort -u | grep -vE "$SRC_RE" | grep -iE "$SECRET_NAME_RE"; _pipe_rc "${PIPESTATUS[@]}"; }
run "secret filenames in history (outside source)" c1 && report "secret filenames in history (outside source)" "clean"
c1b() { git ls-files | grep -E "$SRC_RE" | grep -ciE "$SECRET_NAME_RE"; _pipe_rc "${PIPESTATUS[@]}"; }
run "secret-shaped filenames inside verified source" c1b && say "secret-shaped filenames inside verified source" "${out:-0} (upstream fixtures, informational)"

# 2. no secret-shaped CONTENT in the working tree (outside source, excluding this script)
c2() { git grep -nE "$SECRET_CONTENT_RE" -- . "$NOT_SRC" "$NOT_SELF"; _pipe_rc "${PIPESTATUS[@]}"; }
run "secret content in tree (outside source)" c2 && report "secret content in tree (outside source)" "clean"

# 2b. ...nor anywhere in HISTORY outside source. A key committed and then removed is
#     still one `git log -p` away for anyone who clones. Pathspec-limited so the
#     ingest commits (hundreds of thousands of upstream files) are not diffed.
#     Prints the added lines only; find the commit with `git log -S<fragment> --all`.
c2b() { git log --all -p --pretty=format: -- . "$NOT_SRC" "$NOT_SELF" | grep -E "^\+.*($SECRET_CONTENT_RE)"; _pipe_rc "${PIPESTATUS[@]}"; }
run "secret content in history (outside source)" c2b && report "secret content in history (outside source)" "clean" 40

# 3. nothing from /etc/symoneural mirrored in
c3() { git ls-files | grep -E '(^|/)(api|mail|miner|gateway|spotify|cloudflared)\.env$'; _pipe_rc "${PIPESTATUS[@]}"; }
run "provisioned env files tracked" c3 && report "provisioned env files tracked" "clean"

# 4. no model weights
c4() { git ls-files | grep -vE "$SRC_RE" | grep -iE "$WEIGHT_RE"; _pipe_rc "${PIPESTATUS[@]}"; }
run "model weights tracked (outside source)" c4 && report "model weights tracked (outside source)" "clean"
# upstream fixtures with weight extensions inside verified source are upstream's
# bytes (llama.cpp vocab-only .gguf, pytorch .pt test fixtures); count, do not fail
c4b() { git ls-files | grep -E "$SRC_RE" | grep -ciE "$WEIGHT_RE"; _pipe_rc "${PIPESTATUS[@]}"; }
run "weight-extension files inside verified source" c4b && say "weight-extension files inside verified source" "${out:-0} (upstream fixtures, informational)"
# 4c. magic-byte check on every tracked file > 1 MB outside source: a GGUF or a
#     safetensors blob renamed to dodge the extension list is still a weight.
c4c() {
    git ls-files -z -- . "$NOT_SRC" | while IFS= read -r -d '' f; do
        [ -f "$f" ] || continue
        sz=$(stat -c %s -- "$f" 2>/dev/null) || continue
        [ "$sz" -gt 1048576 ] || continue
        if [ "$(head -c 4 -- "$f" 2>/dev/null)" = "GGUF" ]; then echo "$f (GGUF magic)"; fi
        # safetensors: 8-byte little-endian header length, then a JSON header starting '{'
        if [ "$(head -c 9 -- "$f" 2>/dev/null | tail -c 1)" = "{" ] && head -c 65536 -- "$f" 2>/dev/null | grep -q '"dtype"'; then
            echo "$f (safetensors header)"
        fi
    done
    _pipe_rc "${PIPESTATUS[@]}"
}
run "weight magic bytes in tracked files >1 MB (outside source)" c4c && report "weight magic bytes in tracked files >1 MB (outside source)" "none"

# 5. every tracked acquired-source tree is a component in source-lock.json WITH a
#    recorded tree_sha (i.e. it went in through tools/ingest-tree and is verifiable
#    from a clone). A tracked source tree that is not a verified pin is a defect:
#    it gets none of the exemptions above.
c5() {
    git ls-files | grep -E "$SRC_RE" | sed -E 's|^(Symoneural-[^/]+/src/[^/]+/source/[^/]+)/.*|\1|' | sort -u \
    | python3 -c '
import json,sys
try:
    lock=json.load(open("acquisition/source-lock.json"))["components"]
    ok={c["source_path"] for c in lock if c.get("tree_sha")}
except Exception as e:
    # exit 3, never 1: an uncaught exception exits 1, which _pipe_rc reads as
    # "grep found nothing" - the silent pass this script exists to prevent
    print("source-lock.json unreadable or malformed: %s" % e, file=sys.stderr); sys.exit(3)
# bitbake: the tree IS .../bitbake/source, so any child dir of it maps to that path
ok_prefix={p for p in ok}
hits=0
for line in sys.stdin:
    d=line.strip()
    if d in ok or any(d.startswith(p+"/") for p in ok_prefix): continue
    print(d); hits+=1
sys.exit(0 if hits else 1)
'
    _pipe_rc "${PIPESTATUS[@]}"
}
run "tracked source trees without a verified pin" c5 && report "tracked source trees without a verified pin" "none" 10

# 6. size sanity - GitHub soft-warns at 1 GB, hard limits a single file at 100 MB,
#    and refuses a single push over 2 GiB of pack data.
#    du exits 1 on a dangling symlink inside an upstream tree and xargs then exits
#    123; neither is a broken checker, so only git's and awk's statuses are judged.
c6() {
    local ps
    git ls-files -z | xargs -0 -r du -k --apparent-size 2>/dev/null | awk -F'\t' '$1>102400{print $2}'
    ps=("${PIPESTATUS[@]}")
    [ "${ps[0]}" -le 1 ] || return "${ps[0]}"
    [ "${ps[2]}" -le 1 ] || return "${ps[2]}"
    return 0
}
run "files over 100 MB" c6 && report "files over 100 MB" "none"
say "tracked size" "$(git ls-files -z | du -ch --files0-from=- 2>/dev/null | tail -1 | cut -f1)"
if git rev-parse --verify -q origin/main >/dev/null 2>&1; then
    ahead=$(git rev-list --count origin/main..HEAD 2>/dev/null) || ahead="?"
    say "commits ahead of origin/main" "${ahead}"
    # Pack size of what a push would send. > 2 GiB is refused by GitHub outright;
    # push in batches (git push origin <sha>:main) if so. Informational.
    if [ "$ahead" != "?" ] && [ "$ahead" -gt 0 ]; then
        pushbytes=$(printf 'HEAD\n^origin/main\n' | git pack-objects --revs --stdout -q 2>/dev/null | wc -c)
        say "pack bytes a push would send" "$(numfmt --to=iec "${pushbytes:-0}" 2>/dev/null || echo "${pushbytes:-?}")"
        [ "${pushbytes:-0}" -gt 2147483648 ] && say "  push exceeds GitHub 2 GiB pack limit" "BATCH THE PUSH"
    fi
else
    say "commits ahead of origin/main" "no origin/main ref (fetch first)"
fi

# 7. the .gitignore secret rules must actually be present
grep -q '^\*\.env$' .gitignore && say ".gitignore denies *.env" "yes" \
  || { say ".gitignore denies *.env" "FAIL"; fail=1; }
grep -q '^developer_settings\.json$' .gitignore && say ".gitignore denies developer_settings.json" "yes" \
  || { say ".gitignore denies developer_settings.json" "FAIL"; fail=1; }
grep -q '^\*\.gguf$' .gitignore && say ".gitignore denies *.gguf" "yes" \
  || { say ".gitignore denies *.gguf" "FAIL"; fail=1; }
grep -q '^\*\*/\.gitpins/$' .gitignore && say ".gitignore denies **/.gitpins/" "yes" \
  || { say ".gitignore denies **/.gitpins/" "FAIL"; fail=1; }

# 8. untracked material that a forbidden `git add .` would sweep in (informational).
#    quarantine/ trees and displaced pins live here on purpose; they must stay untracked.
c8() { git status --porcelain --untracked-files=normal | grep -E '^\?\?'; _pipe_rc "${PIPESTATUS[@]}"; }
if run "untracked paths (git add . hazard)" c8; then
    if [ -n "$out" ]; then
        say "untracked paths (git add . hazard)" "$(echo "$out" | wc -l) - listed, informational"
        echo "$out" | head -10 | sed 's/^/    /'
    else
        say "untracked paths (git add . hazard)" "none"
    fi
fi

# 9. a GIT REPOSITORY NESTED INSIDE THIS WORKTREE.
#    On 17 September a clone of THIS repository (same origin, over HTTPS) was made
#    into this repository's own working tree. It was 41 commits behind, held nothing
#    unique, and cost 5.6 GB; had anyone run `git add .` it would also have been a
#    second copy of the estate inside the estate. This check exists so that shape is
#    caught by a command instead of by noticing.
#
#    Scope is deliberate. `find` over the whole tree is wrong twice: it takes 7 s and
#    it reports thousands of upstream .git directories that bitbake unpacks under
#    */build/*/tmp/work/. What matters is a repository git is NOT ignoring - that is
#    exactly the set `git add .` could sweep in - plus anything at the top level,
#    which is where the mistake actually landed.
#
#    A nested repository that IS ignored (FreeToken/, a deliberate working clone with
#    absolute-path venv shebangs) is reported and does not fail: being in .gitignore
#    is the record that it is on purpose. That is the rule to keep - fence it first,
#    or the audit fails.
_c9scan() {
    local d p untracked rc
    for d in */; do
        [ -e "${d}.git" ] || continue
        if git check-ignore -q -- "$d"; then
            echo "FENCED  ${d%/} - nested repository, denied by .gitignore, deliberate"
        else
            echo "HAZARD  ${d%/} - nested repository at the top level, NOT ignored"
        fi
    done
    # rc read directly, never through the pipe: git failing at 128 behind a while
    # loop would otherwise come back as a clean scan (the R16 note at the top).
    untracked=$(git ls-files -o --exclude-standard --directory 2>&1); rc=$?
    if [ "$rc" -ge 2 ]; then printf '%s\n' "$untracked" >&2; return "$rc"; fi
    while IFS= read -r p; do
        [ -n "$p" ] && [ -d "$p" ] || continue
        find "$p" -maxdepth 4 -name .git -print 2>/dev/null \
          | sed -e 's|/\.git$||' -e 's|^|HAZARD  |' -e 's|$| - nested repository under an untracked path|'
    done <<< "$untracked"
    return 0
}
# both detectors can name the same directory; keep the first line per path (the
# top-level one, whose message is the more specific of the two).
c9() { _c9scan | awk '!seen[$2]++'; _pipe_rc "${PIPESTATUS[@]}"; }
if run "git repositories nested in this worktree" c9; then
    if echo "$out" | grep -q '^HAZARD'; then
        say "git repositories nested in this worktree" "FAIL"
        echo "$out" | sed 's/^/    /' | head -20
        echo "    move it outside this tree, or add it to .gitignore if it is deliberate"
        fail=1
    elif [ -n "$out" ]; then
        say "git repositories nested in this worktree" "$(echo "$out" | wc -l) fenced, informational"
        echo "$out" | sed 's/^/    /' | head -10
    else
        say "git repositories nested in this worktree" "none"
    fi
fi

echo
[ $fail -eq 0 ] && echo "AUDIT PASS - safe to push" || echo "AUDIT FAIL - fix the above before pushing"
exit $fail
