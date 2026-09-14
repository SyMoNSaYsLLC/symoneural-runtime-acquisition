"""ctypes binding to libsymoneural-api — the narrow FFI over the C ABI.

Loads ONE explicit library, checks the ABI major before declaring a single
signature, owns no handles (the ABI is stateless by design: lock and supervisor
state live in the filesystem/kernel), translates status codes to exceptions and
never leaks a filesystem path through an HTTP error (callers format
NativeError.status/strerror, not paths).

Resolution order: $SYM_API_NATIVE (an explicit path, for tests and staging),
then the soname on the loader path (the installed package).
"""

from __future__ import annotations

import ctypes
import ctypes.util
import os
from dataclasses import dataclass

ABI_MAJOR = 1
SONAME = "libsymoneural-api.so.1"
UNIT_MAX = 64


class NativeError(RuntimeError):
    def __init__(self, status: int, strerror: str) -> None:
        super().__init__(f"libsymoneural-api: {strerror} ({status})")
        self.status = status
        self.strerror = strerror


class NativeUnavailable(RuntimeError):
    """The library is not installed here. Callers may fall back to the Python
    implementation of the same protocol (gpulock.py) - the file contract is
    shared, so the two interoperate."""


class _Holder(ctypes.Structure):
    _fields_ = [("unit", ctypes.c_char * UNIT_MAX), ("pid", ctypes.c_int), ("since", ctypes.c_double)]


@dataclass(frozen=True, slots=True)
class Holder:
    unit: str
    pid: int
    since: float


class Native:
    def __init__(self, path: str | None = None) -> None:
        path = path or os.environ.get("SYM_API_NATIVE") or ctypes.util.find_library("symoneural-api") or SONAME
        try:
            self._lib = ctypes.CDLL(path)
        except OSError as e:
            raise NativeUnavailable(str(e)) from None
        L = self._lib
        L.sym_api_abi_version.restype = ctypes.c_uint32
        abi = L.sym_api_abi_version()
        if (abi >> 16) != ABI_MAJOR:
            raise NativeError(-7, f"ABI major {abi >> 16} != {ABI_MAJOR}")
        self.abi_version = abi
        # signatures declared only after the ABI check
        L.sym_api_version_string.restype = ctypes.c_char_p
        L.sym_api_strerror.restype = ctypes.c_char_p
        L.sym_api_strerror.argtypes = [ctypes.c_int]
        L.sym_api_capabilities.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        L.sym_api_lock_path.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        L.sym_api_priority.argtypes = [ctypes.c_char_p]
        L.sym_api_priority_entry.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_int)]
        L.sym_api_lock_current.argtypes = [ctypes.POINTER(_Holder)]
        L.sym_api_lock_acquire.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(_Holder)]
        L.sym_api_lock_release.argtypes = [ctypes.c_char_p, ctypes.c_int]
        L.sym_api_rack_json.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        L.sym_api_selftest.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        self.path = path

    def _check(self, st: int) -> None:
        if st != 0:
            raise NativeError(st, self._lib.sym_api_strerror(st).decode())

    def version(self) -> str:
        return self._lib.sym_api_version_string().decode()

    def capabilities(self) -> list[str]:
        buf = ctypes.create_string_buffer(512)
        self._check(self._lib.sym_api_capabilities(buf, len(buf)))
        return buf.value.decode().split()

    def lock_path(self) -> str:
        buf = ctypes.create_string_buffer(1024)
        self._check(self._lib.sym_api_lock_path(buf, len(buf)))
        return buf.value.decode()

    def priority(self, unit: str) -> int:
        return int(self._lib.sym_api_priority(unit.encode()))

    def priority_table(self) -> dict[str, int]:
        out, i = {}, 0
        buf, prio = ctypes.create_string_buffer(UNIT_MAX), ctypes.c_int()
        while self._lib.sym_api_priority_entry(i, buf, len(buf), ctypes.byref(prio)) == 0:
            out[buf.value.decode()] = prio.value
            i += 1
        return out

    def lock_current(self) -> Holder | None:
        h = _Holder()
        st = self._lib.sym_api_lock_current(ctypes.byref(h))
        if st == -6:            # SYM_API_ENOTHELD
            return None
        self._check(st)
        return Holder(h.unit.decode(), h.pid, h.since)

    def lock_acquire(self, unit: str, timeout_ms: int = 0) -> Holder:
        h = _Holder()
        self._check(self._lib.sym_api_lock_acquire(unit.encode(), int(timeout_ms), ctypes.byref(h)))
        return Holder(h.unit.decode(), h.pid, h.since)

    def lock_release(self, unit: str, force: bool = False) -> bool:
        st = self._lib.sym_api_lock_release(unit.encode(), 1 if force else 0)
        if st == -6:
            return False
        self._check(st)
        return True

    def rack_json(self) -> str:
        buf = ctypes.create_string_buffer(4096)
        self._check(self._lib.sym_api_rack_json(buf, len(buf)))
        return buf.value.decode()

    def selftest(self) -> str:
        buf = ctypes.create_string_buffer(256)
        st = self._lib.sym_api_selftest(buf, len(buf))
        report = buf.value.decode()
        if st != 0:
            raise NativeError(st, report)
        return report


_instance: Native | None = None


def load(path: str | None = None) -> Native:
    """Load once; raise NativeUnavailable if the library is not installed."""
    global _instance
    if _instance is None:
        _instance = Native(path)
    return _instance


def available() -> bool:
    try:
        load()
        return True
    except NativeUnavailable:
        return False
