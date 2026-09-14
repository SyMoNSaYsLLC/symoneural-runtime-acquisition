/* symoneural/api.h — the stable C ABI of libsymoneural-api.
 *
 * The native half of the SyMoNeuRaL API owns low-level platform primitives:
 * the single-card GPU lock, unit process supervision, rack telemetry and
 * capability discovery. Everything above it - HTTP, schemas, applications,
 * policy, accounts - is Python. Nothing in this ABI names a customer, a route
 * or a page.
 *
 * ABI rules (reconstruction v1.1 §31):
 *   C17, no Python or C++ types, argv-based process control only, bounded
 *   buffers with explicit capacities, versioned structs (size-prefixed),
 *   stable negative error codes, no secret-bearing diagnostics.
 *
 * Thread safety: functions are reentrant; the lock and supervisor primitives
 * synchronise through the filesystem and the kernel, not through library
 * state. Process semantics: sym_unit_* operate on children of the CALLING
 * process (fork/exec/waitpid); a supervisor that exits abandons its children
 * to their process group, which sym_unit_stop() addresses as -pid.
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */
#ifndef SYMONEURAL_API_H
#define SYMONEURAL_API_H

#include <stddef.h>
#include <stdint.h>

#include "symoneural/gpulock.h"
#include "symoneural/rack.h"
#include "symoneural/unit.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ABI version: MAJOR breaks callers, MINOR adds, PATCH fixes. Python checks
 * MAJOR == its own before declaring signatures. */
#define SYM_API_ABI_MAJOR 1
#define SYM_API_ABI_MINOR 0
#define SYM_API_ABI_PATCH 0
#define SYM_API_ABI_VERSION ((SYM_API_ABI_MAJOR << 16) | (SYM_API_ABI_MINOR << 8) | SYM_API_ABI_PATCH)

/* Stable error codes. Every sym_api_* call returns 0 or one of these. */
typedef enum {
    SYM_API_OK          =  0,
    SYM_API_EINVAL      = -1,   /* bad argument                               */
    SYM_API_ENOSPC      = -2,   /* output buffer too small; nothing written   */
    SYM_API_ENOENT      = -3,   /* no such unit / capability                  */
    SYM_API_EIO         = -4,   /* filesystem / procfs error                  */
    SYM_API_EBUSY       = -5,   /* GPU lock held by another unit              */
    SYM_API_ENOTHELD    = -6,   /* release by a non-holder                    */
    SYM_API_EABI        = -7    /* struct size / ABI mismatch                 */
} sym_api_status;

/* Version and identity. Returns SYM_API_ABI_VERSION at build time. */
uint32_t    sym_api_abi_version(void);
const char *sym_api_version_string(void);       /* "1.0.0" */
const char *sym_api_strerror(int status);

/* Capability discovery: a fixed, sorted, space-separated list the caller can
 * parse without a JSON library. Bounded: fails with ENOSPC, never truncates. */
int sym_api_capabilities(char *buf, size_t cap);

/* Runtime paths the native half uses (lock file path, run directory).
 * Diagnostics-safe: paths only, never contents. */
int sym_api_lock_path(char *buf, size_t cap);

/* Priority: ONE table, here. Python reads it through the binding rather than
 * carrying a second copy (the two tables in gpulock.py/gpulock.c were a drift
 * hazard named in docs/api/CURRENT-IMPLEMENTATION.md). */
int sym_api_priority(const char *unit);
/* Enumerate the table: index 0..n-1; ENOENT past the end. */
int sym_api_priority_entry(int index, char *unit, size_t cap, int *priority);

/* GPU lock, mapped to sym_api_status. holder may be NULL. */
int sym_api_lock_current(sym_lock_holder *holder);
int sym_api_lock_acquire(const char *unit, int timeout_ms, sym_lock_holder *holder);
int sym_api_lock_release(const char *unit, int force);

/* Rack telemetry JSON (see rack.h); ENOSPC rather than truncation. */
int sym_api_rack_json(char *buf, size_t cap);

/* Self-test: exercises the lock protocol against a private path and the
 * telemetry reader. Returns 0 when the primitives behave. Never touches the
 * production lock path. */
int sym_api_selftest(char *report, size_t cap);

#ifdef __cplusplus
}
#endif
#endif /* SYMONEURAL_API_H */
