#!/usr/bin/env python3
"""Small, testable safety checks shared by clean-root-proof."""
import argparse
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def new_root(runtime, requested=None, parent=None):
    base = Path(parent or tempfile.gettempdir()).resolve()
    target = Path(requested) if requested else None
    if target is not None:
        if not target.is_absolute():
            raise ValueError("proof destination must be absolute")
        # Reject existing paths including broken symlinks, without ever deleting.
        if os.path.lexists(target):
            raise ValueError("proof destination already exists; choose a NEW directory")
        base = target.parent.resolve(strict=True)
        target = base / target.name
    if base == ROOT or base.is_relative_to(ROOT):
        raise ValueError("proof extraction inside the estate is forbidden")
    if target is not None:
        target.mkdir(mode=0o700)
        return target
    return Path(tempfile.mkdtemp(prefix=f"symoneural-{runtime.lower()}-proof-", dir=base))


def driver_version_valid(driver):
    return re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", driver) is not None


def driver_package_matches(driver, package, version, library):
    if not driver_version_valid(driver):
        return False
    # A matching version on an unrelated package is not driver provenance.
    name = Path(library).name
    if not (name.startswith("libnvidia-") or re.match(r"libcuda\.so(?:\.|$)", name)):
        return False
    package = package.split(":", 1)[0]
    if not (package.startswith("libnvidia-") or package in {"libcuda1", "nvidia-driver-cuda", "cuda-drivers"}):
        return False
    upstream = version.split(":", 1)[-1].rsplit("-", 1)[0]
    return upstream == driver


def trace_libraries(root):
    """Inspect initialization records, not arbitrary mappings; fail without data."""
    inside, outside, traces, launchers = set(), set(), 0, 0
    prefix = str(root) + "/"
    for filename in (root / "tmp").glob("ld-debug.*"):
        if not filename.name[len("ld-debug."):].isdigit():
            continue
        traces += 1
        paths = [m.group(1).strip() for m in re.finditer(r"calling init:\s+([^\n]+)", filename.read_text(errors="replace"))]
        internal = {p for p in paths if p.startswith(prefix)}
        external = set(paths) - internal
        inside.update(internal)
        # The shell interpreter of the subprocess wrapper precedes the target
        # loader in the same PID; no other external libraries are exempt.
        host_shell = {"/lib64/ld-linux-x86-64.so.2", "/lib/x86_64-linux-gnu/libc.so.6"}
        target_loaders = {str(root / p) for p in ("lib/ld-linux-x86-64.so.2", "lib64/ld-linux-x86-64.so.2")}
        if external and internal & target_loaders:
            first_target = min(i for i, p in enumerate(paths) if p in target_loaders)
            # Driver libraries can initialize after the transition in S2 mode.
            # They do not invalidate the earlier shell launch; retain them for
            # separate ownership/version validation. A host libc seen after the
            # transition is never exempt, even if it also appeared before it.
            shell = {p for p in external & host_shell
                     if all(i < first_target for i, name in enumerate(paths) if name == p)}
            if shell:
                launchers += 1
                external -= shell
        outside.update(external)
    if not traces or not inside:
        raise ValueError("no target-library loader trace evidence")
    return dict(inside=inside, outside=outside, traces=traces, launchers=launchers)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sp = ap.add_subparsers(dest="action", required=True)
    root = sp.add_parser("new-root")
    root.add_argument("runtime")
    root.add_argument("destination", nargs="?")
    driver = sp.add_parser("driver-package")
    for arg in ("driver", "package", "version", "library"):
        driver.add_argument(arg)
    trace = sp.add_parser("trace-libraries")
    trace.add_argument("root", type=Path)
    args = ap.parse_args()
    try:
        if args.action == "new-root":
            print(new_root(args.runtime, args.destination, os.environ.get("TMPDIR")))
            return 0
        if args.action == "trace-libraries":
            result = trace_libraries(args.root)
            print(f"  {len(result['inside'])} distinct target-library initialization paths across {result['traces']} traced processes; {result['launchers']} shell-launcher transitions", file=sys.stderr)
            for path in sorted(result["outside"]):
                print(path)
            return 0
        return 0 if driver_package_matches(args.driver, args.package, args.version, args.library) else 1
    except (ValueError, OSError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
