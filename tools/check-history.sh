#!/bin/bash
# check-history.sh - has this been tried before, and did it fail?
#
# RULE (Garrett, 2026-09-13): "whatever decisions you make it needs to be somehow
# brought into history and proven it hasn't already failed or caused issues. We
# shall not make the same error twice. Our next mistake best be a new one."
#
# 134 Claude transcripts / ~372 MB span 2026-08 to now. That corpus holds the
# record of what was already tried. Finding one prior decision in it took four
# manual searches; this makes it one command.
#
# Run BEFORE committing to any approach:
#     tools/check-history.sh 'nvidia-driver-userspace'
#     tools/check-history.sh 'do_rootfs'
#     tools/check-history.sh 'gpt-oss' --failures
#
# Exit 0 always: absence of a hit is NOT proof of safety, only absence of record.

H=/home/google/.claude/projects
[ -d "$H" ] || { echo "no transcript corpus at $H"; exit 0; }
TERM_="$1"; shift
[ -z "$TERM_" ] && { echo "usage: $0 <term> [--failures]"; exit 0; }
ONLYFAIL=0; [ "$1" = "--failures" ] && ONLYFAIL=1

FILES=$(find "$H" -name '*.jsonl' -size +20k 2>/dev/null)
echo "=== '$TERM_' across $(echo "$FILES" | wc -l) transcripts ==="

# 1. where and when
echo
echo "--- sessions mentioning it (newest first) ---"
for f in $FILES; do
  n=$(grep -ci -- "$TERM_" "$f" 2>/dev/null)
  [ "${n:-0}" -gt 0 ] && printf '%s  %5d  %s\n' "$(date -r "$f" +%Y-%m-%d)" "$n" "${f#$H/}"
done | sort -r | head -12

# 2. did it fail - the part that matters
echo
echo "--- FAILURE CONTEXT (the reason for this tool) ---"
grep -hoiE "[^\"\\\\]{0,90}${TERM_}[^\"\\\\]{0,70}(fail|error|refus|reject|cannot|unable|broke|wrong|revert|rollback)[^\"\\\\]{0,90}" $FILES 2>/dev/null \
  | sed 's/\\n/ /g' | sort -u | head -12 | sed 's/^/  ! /'
grep -hoiE "[^\"\\\\]{0,90}(fail|error|refus|reject|cannot|unable|broke|wrong|revert|rollback)[^\"\\\\]{0,70}${TERM_}[^\"\\\\]{0,90}" $FILES 2>/dev/null \
  | sed 's/\\n/ /g' | sort -u | head -12 | sed 's/^/  ! /'

if [ "$ONLYFAIL" = "0" ]; then
  echo
  echo "--- decisions / conclusions mentioning it ---"
  grep -hoiE "[^\"\\\\]{0,80}${TERM_}[^\"\\\\]{0,60}(decided|decision|instead|rather than|do not|never|must not|chose)[^\"\\\\]{0,90}" $FILES 2>/dev/null \
    | sed 's/\\n/ /g' | sort -u | head -8 | sed 's/^/  > /'
fi

echo
echo "NOTE: no hits means no RECORD of it failing - not proof it is safe."
exit 0
