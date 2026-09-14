#!/usr/bin/env python3
"""Host-visible process checks for estate operators; never print raw argv.

This is a point-in-time check, not an edit lock. Keep other coders paused.
A private PID namespace is not evidence that the host is quiescent.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
BAKE_NAMES = {"bitbake", "bitbake-server", "bitbake-worker"}


class ProbeError(RuntimeError):
    pass


def is_bitbake(argv, comm):
    # Executable/script positions only, never recipe names or shell text.
    if comm in BAKE_NAMES:
        return True
    if not argv:
        return False
    exe = Path(argv[0]).name
    if exe in BAKE_NAMES:
        return True
    if exe.startswith("python") or exe in {"bash", "sh", "dash"}:
        for arg in argv[1:]:
            if arg in {"-c", "-m"}:
                return False
            if arg.startswith("-"):
                continue
            return Path(arg).name in BAKE_NAMES
    return False


def snapshot(proc=Path("/proc")):
    try:
        init = (proc / "1/comm").read_text().strip()
        if init not in {"systemd", "init"}:
            raise ProbeError("host process visibility unavailable (PID 1 is not init/systemd)")
        rows = {}
        for path in list(proc.iterdir()):
            if not path.name.isdecimal():
                continue
            try:
                if path.stat().st_uid != os.getuid():
                    continue
                argv = (path / "cmdline").read_bytes().decode(errors="replace").split("\0")
                comm = (path / "comm").read_text().strip()
                stat = (path / "stat").read_text().rsplit(")", 1)[1].split()
                bake = is_bitbake(argv, comm)
                try:
                    cwd = Path(os.readlink(path / "cwd"))
                except PermissionError:
                    if bake:
                        raise
                    cwd = None
                rows[int(path.name)] = dict(pid=int(path.name), ppid=int(stat[1]),
                    start=stat[19], cwd=cwd, comm=comm, bake=bake)
            except (FileNotFoundError, ProcessLookupError):
                continue
        return rows
    except OSError as exc:
        raise ProbeError("process inspection failed: " + str(exc)) from exc


def in_estate(row, root=ROOT):
    cwd = row["cwd"]
    return cwd is not None and cwd.is_relative_to(root) and "build" in cwd.relative_to(root).parts


def build_descendants(rows, root=ROOT):
    selected = {pid for pid, row in rows.items() if row["bake"] and in_estate(row, root)}
    while True:
        new = {pid for pid, row in rows.items() if row["ppid"] in selected}
        if new <= selected:
            return selected
        selected |= new


def check(rows, build_dir=None):
    live = [r for r in rows.values() if r["bake"] and
            (build_dir is None or r["cwd"] == build_dir or
             (r["cwd"] is not None and r["cwd"].is_relative_to(build_dir)))]
    for r in live:
        print(f"LIVE: pid={r['pid']} program={r['comm']} cwd={r['cwd']}", file=sys.stderr)
    return 1 if live else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["guard", "check-build", "nice"])
    ap.add_argument("--build-dir", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.action == "check-build" and a.build_dir is None:
        ap.error("check-build requires --build-dir")
    try:
        rows = snapshot()
        if a.action != "nice":
            rc = check(rows, a.build_dir.resolve() if a.action == "check-build" else None)
            if not rc:
                print("No same-user BitBake process observed on the host (point-in-time check; not a lock).")
            return rc
        selected = build_descendants(rows)
        count = 0
        for pid in sorted(selected):
            row = rows[pid]
            if a.dry_run:
                print(f"WOULD LOWER PRIORITY: pid={pid} program={row['comm']}")
                continue
            try:
                stat = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
                if stat[19] != row["start"]:
                    raise ProbeError(f"process identity changed for pid {pid}")
                os.setpriority(os.PRIO_PROCESS, pid, max(10, os.getpriority(os.PRIO_PROCESS, pid)))
                subprocess.run(["ionice", "-c3", "-p", str(pid)], check=True, capture_output=True)
                count += 1
            except (FileNotFoundError, ProcessLookupError):
                continue
        print(f"nice-builds: {'selected ' + str(len(selected)) if a.dry_run else 'adjusted ' + str(count)} estate build process(es)")
        return 0
    except (ProbeError, OSError, subprocess.CalledProcessError) as exc:
        print("REFUSED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
