"""The GPU lock — one card, several units that each want all of it.

15.92 GiB. A chat weight set and an image weight set do not both fit, so the
lock hands the card to exactly one surface at a time. This module is the whole
arbitration policy; nothing else may take the device.

Design rules, each paid for:

  1. The lock is a FILE, not a process. A crashed holder must not strand the
     card, and a lock held in memory dies with the process that owns it.
  2. Interactive units OUTRANK revenue. The miner yields to chat, always.
     Revenue that makes a user wait is not revenue, it is a complaint.
  3. Acquisition is bounded. An unbounded wait is a hang wearing a queue's
     clothes.
  4. The holder is recorded with its PID and start time, so a stale lock is
     distinguishable from a live one WITHOUT guessing.
"""

from __future__ import annotations

import errno
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

LOCK_PATH = Path(os.environ.get("SYM_GPU_LOCK", "/run/symoneural/gpu.lock"))

# Higher wins. Interactive surfaces outrank batch ones.
PRIORITY: dict[str, int] = {
    "chat": 100,
    "image": 100,
    "sigils": 90,
    "studio": 50,
    "reinforce": 50,
    "miner": 10,
}


class LockBusy(Exception):
    """The card is held by someone with at least equal claim."""

    def __init__(self, holder: str, since: float) -> None:
        super().__init__(f"GPU held by {holder}")
        self.holder = holder
        self.held_for_s = time.time() - since


@dataclass(frozen=True, slots=True)
class Holder:
    unit: str
    pid: int
    since: float

    @property
    def alive(self) -> bool:
        """Is the recorded PID still running?

        A lock file whose owner is gone is stale, and treating it as live is how
        a card stays idle while units queue behind a corpse.
        """
        try:
            os.kill(self.pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True          # exists, owned by another user
        return True

    def to_dict(self) -> dict:
        return {
            "unit": self.unit,
            "pid": self.pid,
            "since": self.since,
            "held_for_s": round(time.time() - self.since, 1),
            "alive": self.alive,
        }


def _read() -> Holder | None:
    try:
        raw = json.loads(LOCK_PATH.read_text())
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        _reap_corrupt()
        return None
    try:
        return Holder(unit=raw["unit"], pid=int(raw["pid"]), since=float(raw["since"]))
    except (KeyError, TypeError, ValueError):
        _reap_corrupt()
        return None              # corrupt = absent, not fatal


def _reap_corrupt() -> None:
    """Absent means the file must go: with it left in place, O_EXCL creation
    fails with EEXIST until the deadline and the card is stranded behind
    garbage. Same rule as the C half."""
    try:
        LOCK_PATH.unlink()
    except FileNotFoundError:
        pass


def current() -> Holder | None:
    """Who holds the card. Reaps a stale record rather than reporting it."""
    holder = _read()
    if holder is None:
        return None
    if not holder.alive:
        release(holder.unit, force=True)
        return None
    return holder


def priority(unit: str) -> int:
    return PRIORITY.get(unit, 50)


def acquire(unit: str, *, timeout_s: float = 30.0, poll_s: float = 0.25) -> Holder:
    """Take the card for `unit`, waiting up to `timeout_s`.

    A higher-priority unit does NOT preempt by force - it waits, and the holder
    is expected to yield. Killing a holder mid-inference corrupts its output and
    leaves VRAM allocated; a cooperative yield does neither.
    """
    deadline = time.time() + timeout_s
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)

    while True:
        holder = current()
        if holder is None:
            try:
                fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
                # lost the race; fall through and retry
            else:
                with os.fdopen(fd, "w") as fh:
                    mine = Holder(unit=unit, pid=os.getpid(), since=time.time())
                    json.dump({"unit": mine.unit, "pid": mine.pid, "since": mine.since}, fh)
                return mine
        elif holder.unit == unit:
            return holder        # re-entrant for the same unit

        if time.time() >= deadline:
            raise LockBusy(holder.unit if holder else "unknown",
                           holder.since if holder else time.time())
        time.sleep(poll_s)


def release(unit: str, *, force: bool = False) -> bool:
    """Release the card. Refuses to release another unit's lock unless forced.

    `force` exists only for reaping a dead holder - never for jumping a queue.
    """
    holder = _read()
    if holder is None:
        return False
    if holder.unit != unit and not force:
        return False
    try:
        LOCK_PATH.unlink()
    except FileNotFoundError:
        return False
    return True


class hold:
    """Context manager: acquire on enter, always release on exit."""

    def __init__(self, unit: str, timeout_s: float = 30.0) -> None:
        self.unit = unit
        self.timeout_s = timeout_s
        self.holder: Holder | None = None

    def __enter__(self) -> Holder:
        self.holder = acquire(self.unit, timeout_s=self.timeout_s)
        return self.holder

    def __exit__(self, *exc) -> bool:
        release(self.unit)
        return False             # never swallow the exception
