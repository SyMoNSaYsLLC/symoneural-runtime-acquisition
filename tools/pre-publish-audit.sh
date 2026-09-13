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

# 1. no secret-bearing filenames tracked, now or ever
hits=$(git log --all --pretty=format: --name-only --diff-filter=A 2>/dev/null \
       | sort -u | grep -iE '\.env$|\.pem$|\.key$|\.p12$|id_rsa|id_ed25519|\.netrc|credentials\.' || true)
[ -n "$hits" ] && { say "secret filenames in history" "FAIL"; echo "$hits"; fail=1; } \
               || say "secret filenames in history" "clean"

# 2. no secret-shaped assignments in the working tree
hits=$(git grep -nE '(SMTP_PASS|SYM_[A-Z_]*TOKEN|TUNNEL_TOKEN|CLIENT_SECRET|ACCOUNTS_SECRET)[[:space:]]*=[[:space:]]*["'"'"']?[A-Za-z0-9+/_-]{12,}' -- . 2>/dev/null || true)
[ -n "$hits" ] && { say "secret assignments in tree" "FAIL"; echo "$hits"; fail=1; } \
               || say "secret assignments in tree" "clean"

# 3. nothing from /etc/symoneural mirrored in
hits=$(git ls-files | grep -E '(^|/)(api|mail|miner|gateway|spotify|cloudflared)\.env$' || true)
[ -n "$hits" ] && { say "provisioned env files tracked" "FAIL"; echo "$hits"; fail=1; } \
               || say "provisioned env files tracked" "clean"

# 4. no model weights
hits=$(git ls-files | grep -iE '\.(gguf|safetensors|onnx|ckpt|pt|pth)$' || true)
[ -n "$hits" ] && { say "model weights tracked" "FAIL"; echo "$hits"; fail=1; } \
               || say "model weights tracked" "clean"

# 5. no acquired upstream source (it belongs to its own upstream, and is pinned)
hits=$(git ls-files | grep -E '^Symoneural-[^/]+/src/[^/]+/source/' || true)
[ -n "$hits" ] && { say "acquired upstream source tracked" "FAIL"; echo "$hits" | head -5; fail=1; } \
               || say "acquired upstream source tracked" "clean"

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
