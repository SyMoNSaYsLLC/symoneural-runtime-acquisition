# SUPERSEDED-BY-V1.1

These tools and records were the v1 prototypes. They are retained as history and
are **not executed** by the scanner suite.

- `scan-licenses.py`, `scan-vendored.py`, `scan-vendored-inline.py`
  replaced by `tools/scan-dependencies.py`, which produces
  `acquisition/license-inventory.json` and `acquisition/vendor-lock.json`.
- `VENDORED-REGISTER.md` was a hand-maintained register competing with the
  generated `acquisition/vendor-lock.json`. A second, non-generated authority
  for the same facts is a hazard; `vendor-lock.json` is authoritative.

`control-plane.json` records these under `superseded_tools`, so scanner identity
describes what actually produced a result.
