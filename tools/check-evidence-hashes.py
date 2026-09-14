#!/usr/bin/env python3
"""Check saved evidence against its original hashes; never refresh expected hashes.

Exit 1 for a missing/mismatched artifact, malformed record, or no coverage.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent


def audit(root, manifests):
    rows = []
    for manifest in manifests:
        count = 0
        for number, line in enumerate(manifest.read_text().splitlines(), 1):
            if not line.strip() or line.startswith("#"):
                continue
            match = re.fullmatch(r"([0-9a-f]{64})\s+\*?(.+)", line)
            row = dict(manifest=str(manifest), line=number)
            count += 1
            if not match:
                rows.append(dict(row, status="MALFORMED")); continue
            expected, filename = match.groups()
            path = root / filename
            row.update(path=filename, expected=expected)
            if not path.resolve().is_relative_to(root.resolve()):
                rows.append(dict(row, status="OUTSIDE REPOSITORY")); continue
            if not path.is_file():
                rows.append(dict(row, status="MISSING")); continue
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for data in iter(lambda: stream.read(1048576), b""):
                    digest.update(data)
            actual = digest.hexdigest()
            rows.append(dict(row, actual=actual, status="MATCH" if actual == expected else "MISMATCH"))
        if not count:
            rows.append(dict(manifest=str(manifest), status="EMPTY MANIFEST"))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, help="write this audit result, not new expected hashes")
    a = ap.parse_args()
    try:
        rows = audit(ROOT, sorted((ROOT / "generated/evidence").glob("*/*SHA256SUMS")))
        counts = dict(Counter(r["status"] for r in rows))
        for row in rows:
            if row["status"] != "MATCH":
                print(row["status"], row.get("path", row["manifest"]))
        rc = 0 if rows and all(row["status"] == "MATCH" for row in rows) else 1
        print("COUNTS:", json.dumps(counts, sort_keys=True))
        print("RESULT:", "PASS" if not rc else "FAIL / NO CURRENT PROOF")
        if a.json:
            a.json.write_text(json.dumps(dict(rows=rows, counts=counts, exit_code=rc), indent=2) + "\n")
        return rc
    except (ValueError, OSError) as exc:
        print("FAIL:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
