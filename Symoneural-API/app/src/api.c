/* api.c — the stable ABI surface of libsymoneural-api. Thin by design: it maps
 * the primitives in gpulock.c / rack.c / unit.c onto stable status codes and
 * bounded buffers, and holds the ONE priority table.
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */
#define _POSIX_C_SOURCE 200809L
#include "symoneural/api.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

uint32_t sym_api_abi_version(void) { return SYM_API_ABI_VERSION; }

const char *sym_api_version_string(void)
{
    static char v[16];
    snprintf(v, sizeof v, "%d.%d.%d", SYM_API_ABI_MAJOR, SYM_API_ABI_MINOR, SYM_API_ABI_PATCH);
    return v;
}

const char *sym_api_strerror(int st)
{
    switch (st) {
    case SYM_API_OK:       return "ok";
    case SYM_API_EINVAL:   return "invalid argument";
    case SYM_API_ENOSPC:   return "buffer too small";
    case SYM_API_ENOENT:   return "no such entry";
    case SYM_API_EIO:      return "I/O error";
    case SYM_API_EBUSY:    return "GPU held by another unit";
    case SYM_API_ENOTHELD: return "lock not held by this unit";
    case SYM_API_EABI:     return "ABI mismatch";
    }
    return "unknown";
}

static int put(char *buf, size_t cap, const char *s)
{
    if (buf == NULL || cap == 0) return SYM_API_EINVAL;
    size_t n = strlen(s);
    if (n + 1 > cap) return SYM_API_ENOSPC;
    memcpy(buf, s, n + 1);
    return SYM_API_OK;
}

int sym_api_capabilities(char *buf, size_t cap)
{
    /* sorted, stable; a new capability is appended in order and bumps MINOR */
    return put(buf, cap, "gpu-lock priority-table rack-telemetry unit-supervisor");
}

int sym_api_lock_path(char *buf, size_t cap) { return put(buf, cap, sym_gpulock_path()); }

int sym_api_priority(const char *unit) { return sym_gpulock_priority(unit); }

int sym_api_priority_entry(int index, char *unit, size_t cap, int *priority)
{
    const char *name; int prio;
    if (sym_gpulock_priority_table(index, &name, &prio) != 0) return SYM_API_ENOENT;
    if (unit == NULL || priority == NULL) return SYM_API_EINVAL;
    int rc = put(unit, cap, name);
    if (rc) return rc;
    *priority = prio;
    return SYM_API_OK;
}

static int map_lock(sym_lock_status st)
{
    switch (st) {
    case SYM_LOCK_OK:       return SYM_API_OK;
    case SYM_LOCK_BUSY:     return SYM_API_EBUSY;
    case SYM_LOCK_IO:       return SYM_API_EIO;
    case SYM_LOCK_CORRUPT:  return SYM_API_EIO;
    case SYM_LOCK_NOT_HELD: return SYM_API_ENOTHELD;
    case SYM_LOCK_INVALID:  return SYM_API_EINVAL;
    }
    return SYM_API_EIO;
}

int sym_api_lock_current(sym_lock_holder *h) { return map_lock(sym_gpulock_current(h)); }
int sym_api_lock_acquire(const char *unit, int timeout_ms, sym_lock_holder *h) { return map_lock(sym_gpulock_acquire(unit, timeout_ms, h)); }
int sym_api_lock_release(const char *unit, int force) { return map_lock(sym_gpulock_release(unit, force != 0)); }

int sym_api_rack_json(char *buf, size_t cap)
{
    if (buf == NULL || cap == 0) return SYM_API_EINVAL;
    return sym_rack_json(buf, cap) < 0 ? SYM_API_ENOSPC : SYM_API_OK;
}

int sym_api_selftest(char *report, size_t cap)
{
    /* private lock path: never the production one */
    char path[256];
    const char *td = getenv("TMPDIR");
    snprintf(path, sizeof path, "%s/symoneural-selftest-%d.lock", td ? td : "/tmp", (int)getpid());
    const char *saved = getenv("SYM_GPU_LOCK");
    char saved_copy[512] = {0};
    if (saved) snprintf(saved_copy, sizeof saved_copy, "%s", saved);
    setenv("SYM_GPU_LOCK", path, 1);
    unlink(path);

    int fails = 0;
    sym_lock_holder h;
    if (sym_api_lock_current(&h) != SYM_API_ENOTHELD) ++fails;
    if (sym_api_lock_acquire("selftest-a", 0, &h) != SYM_API_OK) ++fails;
    if (sym_api_lock_acquire("selftest-b", 0, NULL) != SYM_API_EBUSY) ++fails;
    if (sym_api_lock_release("selftest-b", 0) != SYM_API_ENOTHELD) ++fails;
    if (sym_api_lock_release("selftest-a", 0) != SYM_API_OK) ++fails;
    if (sym_api_lock_current(&h) != SYM_API_ENOTHELD) ++fails;
    char js[2048];
    if (sym_api_rack_json(js, sizeof js) != SYM_API_OK) ++fails;
    if (sym_api_rack_json(js, 8) != SYM_API_ENOSPC) ++fails;
    unlink(path);
    if (saved) setenv("SYM_GPU_LOCK", saved_copy, 1); else unsetenv("SYM_GPU_LOCK");

    char line[128];
    snprintf(line, sizeof line, "selftest %s: %d failure(s), abi %s", fails ? "FAIL" : "PASS", fails, sym_api_version_string());
    if (report && cap) put(report, cap, line);
    return fails ? SYM_API_EIO : SYM_API_OK;
}
