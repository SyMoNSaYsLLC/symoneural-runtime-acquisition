# libsymoneural-api — C ABI (v1.0.0)

Header: `Symoneural-API/app/include/symoneural/api.h` (includes `gpulock.h`,
`rack.h`, `unit.h`). C17. Depends on libc/POSIX only (`readelf -d`: NEEDED
`libc.so.6`; SONAME `libsymoneural-api.so.1`). 27 exported `sym_*` symbols.

Version: `SYM_API_ABI_VERSION = (MAJOR<<16)|(MINOR<<8)|PATCH`, `sym_api_abi_version()`,
`sym_api_version_string()`. MAJOR breaks callers; the Python binding refuses a
different MAJOR before declaring any signature.

Errors (`sym_api_status`): `OK 0`, `EINVAL -1`, `ENOSPC -2` (buffer too small,
nothing written — never truncation), `ENOENT -3`, `EIO -4`, `EBUSY -5`,
`ENOTHELD -6`, `EABI -7`; `sym_api_strerror()`.

| Function | Semantics |
|---|---|
| `sym_api_capabilities(buf,cap)` | sorted, space-separated: `gpu-lock priority-table rack-telemetry unit-supervisor` |
| `sym_api_lock_path(buf,cap)` | `$SYM_GPU_LOCK` or `/run/symoneural/gpu.lock` (diagnostics: paths, never contents) |
| `sym_api_priority(unit)` / `sym_api_priority_entry(i,…)` | THE priority table (chat 100, image 100, sigils 90, studio 50, reinforce 50, miner 10; unknown 50); enumerable so Python carries no second copy |
| `sym_api_lock_current/acquire/release` | the file-lock protocol (`gpulock.h`): O_EXCL creation, re-entrant per unit NAME, stale and corrupt holders reaped, bounded wait, cooperative yield |
| `sym_api_rack_json(buf,cap)` | host + GPU telemetry JSON; `ENOSPC` rather than a truncated object |
| `sym_api_selftest(report,cap)` | lock protocol + telemetry against a private path; leaves nothing behind |
| `sym_unit_start/poll/stop/json` (`unit.h`) | argv `execv`, own process group set by BOTH parent and child, GPU lock taken before exec, SIGTERM→10 s→SIGKILL; **no shell interface exists** |

Process semantics: `sym_unit_*` act on children of the calling process; the lock
and supervisor synchronise through the filesystem and kernel, so the library holds
no state and is reentrant. Linux-specific inputs (`/proc`, `/sys`, `nvidia-smi`)
live in `rack.c`; the lock and supervisor are POSIX.

Utility: `symoneural-api-util version|abi|capabilities|units|lock-status|selftest|doctor`
— generic, no customer command.

Tests: `tests/native/test_api.c` (ABI), `tests/python/test_native.py` (ctypes,
cross-language lock proof, util agreement). Build: `CMakeLists.txt` (shared +
static + util + ctest) or `tests/native/Makefile` for the host regression run.

Known deviation still open: `rack.c` reads `nvidia-smi` through `popen()` (a
fixed string, but a shell); target is `posix_spawn` + pipe with an argv.
