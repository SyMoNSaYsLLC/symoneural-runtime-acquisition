#!/bin/bash
# pre-publish-audit.sh - run BEFORE any push to a remote.
#
# Treat this repository as if it were public even while it is private: once
# published it is forked, cached and archived, and going private afterwards
# undoes none of that.
#
# Exit 0 = safe to push. Exit 1 = something must be fixed first.
cd "$(dirname "$0")/.." || exit 1
fail=0
say() { printf '%-52s %s\n' "$1" "$2"; }

# Acquired upstream trees are committed at their pin and verified byte-identical
# to upstream (tools/ingest-tree verify). A tree identical to upstream cannot hold
# a secret of OURS, and upstream test fixtures (librespot, httpx, gstreamer,
# workerd ship test keys and .env samples) would flood the scan with false
# positives that hide a real hit. So the secret and weight scans cover everything
# EXCEPT those paths, and a separate check proves every such path IS a verified
# pin - an unverified tree gets no exemption.
SRC_RE='^Symoneural-[^/]+/src/[^/]+/source/'
NOT_SRC=':(exclude,glob)Symoneural-*/src/*/source/**'

# 1. no secret-bearing filenames tracked, now or ever
hits=$(git log --all --pretty=format: --name-only --diff-filter=A 2>/dev/null \
       | sort -u | grep -iE '\.env$|\.pem$|\.key$|\.p12$|id_rsa|id_ed25519|\.netrc|credentials\.' || true)
[ -n "$hits" ] && { say "secret filenames in history" "FAIL"; echo "$hits"; fail=1; } \
               || say "secret filenames in history" "clean"

# 2. no secret-shaped assignments in the working tree
hits=$(git grep -nE '(SMTP_PASS|SYM_[A-Z_]*TOKEN|TUNNEL_TOKEN|CLIENT_SECRET|ACCOUNTS_SECRET)[[:space:]]*=[[:space:]]*["'"'"']?[A-Za-z0-9+/_-]{12,}' -- . "$NOT_SRC" 2>/dev/null || true)
[ -n "$hits" ] && { say "secret assignments in tree (outside source)" "FAIL"; echo "$hits"; fail=1; } \
               || say "secret assignments in tree (outside source)" "clean"

# 3. nothing from /etc/symoneural mirrored in
hits=$(git ls-files | grep -E '(^|/)(api|mail|miner|gateway|spotify|cloudflared)\.env$' || true)
[ -n "$hits" ] && { say "provisioned env files tracked" "FAIL"; echo "$hits"; fail=1; } \
               || say "provisioned env files tracked" "clean"

# 4. no model weights
hits=$(git ls-files | grep -vE "$SRC_RE" | grep -iE '\.(gguf|safetensors|onnx|ckpt|pt|pth)$' || true)
[ -n "$hits" ] && { say "model weights tracked (outside source)" "FAIL"; echo "$hits"; fail=1; } \
               || say "model weights tracked (outside source)" "clean"
# upstream fixtures with weight extensions inside verified source are upstream's
# bytes (llama.cpp vocab-only .gguf, pytorch .pt test fixtures); count, do not fail
n=$(git ls-files | grep -E "$SRC_RE" | grep -ciE '\.(gguf|safetensors|onnx|ckpt|pt|pth)$' || true)
say "weight-extension files inside verified source" "${n:-0} (upstream fixtures, informational)"

# 5. every tracked acquired-source tree is a component in source-lock.json WITH a
#    recorded tree_sha (i.e. it went in through tools/ingest-tree and is verifiable
#    from a clone). A tracked source tree that is not a verified pin is a defect:
#    it gets none of the exemptions above.
hits=$(git ls-files | grep -E "$SRC_RE" | sed -E 's|^(Symoneural-[^/]+/src/[^/]+/source/[^/]+)/.*|\1|' | sort -u \
       | python3 -c '
import json,sys
lock=json.load(open("acquisition/source-lock.json"))["components"]
ok={c["source_path"] for c in lock if c.get("tree_sha")}
# bitbake: the tree IS .../bitbake/source, so any child dir of it maps to that path
ok_prefix={p for p in ok}
for line in sys.stdin:
    d=line.strip()
    if d in ok or any(d.startswith(p+"/") for p in ok_prefix): continue
    print(d)
' || true)
[ -n "$hits" ] && { say "tracked source trees without a verified pin" "FAIL"; echo "$hits" | head -10; fail=1; } \
               || say "tracked source trees without a verified pin" "none"

# 6. size sanity - GitHub soft-warns at 1 GB, hard limits a single file at 100 MB
big=$(git ls-files -z | xargs -0 du -k 2>/dev/null | awk '$1>102400{print $2}' || true)
[ -n "$big" ] && { say "files over 100 MB" "FAIL"; echo "$big"; fail=1; } \
               || say "files over 100 MB" "none"
say "tracked size" "$(git ls-files -z | du -ch --files0-from=- 2>/dev/null | tail -1 | cut -f1)"

# 7. the .gitignore secret rules must actually be present
grep -q '^\*\.env$' .gitignore && say ".gitignore denies *.env" "yes" \
  || { say ".gitignore denies *.env" "FAIL"; fail=1; }

echo
[ $fail -eq 0 ] && echo "AUDIT PASS - safe to push" || echo "AUDIT FAIL - fix the above before pushing"
exit $fail
