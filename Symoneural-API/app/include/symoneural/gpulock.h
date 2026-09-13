/* symoneural/gpulock.h — single-card arbitration for native units.
 *
 * One RTX 5070 Ti, 15.92 GiB. A chat weight set and an image weight set do not
 * both fit, so exactly one surface may hold the device at a time.
 *
 * The Python control plane implements the same protocol; this is the C half,
 * for units that are native binaries (llama-server, the miner, the GStreamer
 * pipelines) and cannot call into the API process to ask permission.
 *
 * THE FILE FORMAT IS THE CONTRACT. Both halves read and write the same JSON
 * object, so a C holder is visible to Python and the reverse:
 *
 *     {"unit":"chat","pid":12345,"since":1789312176.327}
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */

#ifndef SYMONEURAL_GPULOCK_H
#define SYMONEURAL_GPULOCK_H

#include <stdbool.h>
#include <sys/types.h>

#ifdef __cplusplus
extern "C" {
#endif

#define SYM_GPULOCK_UNIT_MAX 64
#define SYM_GPULOCK_DEFAULT_PATH "/run/symoneural/gpu.lock"

typedef enum {
    SYM_LOCK_OK = 0,
    SYM_LOCK_BUSY = -1,      /* held by another unit, deadline passed   */
    SYM_LOCK_IO = -2,        /* filesystem error; errno is set          */
    SYM_LOCK_CORRUPT = -3,   /* lock file unparseable                   */
    SYM_LOCK_NOT_HELD = -4,  /* release called by a non-holder          */
    SYM_LOCK_INVALID = -5    /* bad argument                            */
} sym_lock_status;

typedef struct {
    char unit[SYM_GPULOCK_UNIT_MAX];
    pid_t pid;
    double since;            /* unix epoch seconds, matches the Python half */
} sym_lock_holder;

/* Priority. Higher wins. Interactive surfaces outrank batch ones: the miner
 * yields to chat, always. Revenue that makes a user wait is a complaint. */
int sym_gpulock_priority(const char *unit);

/* Path in use: $SYM_GPU_LOCK, else SYM_GPULOCK_DEFAULT_PATH. */
const char *sym_gpulock_path(void);

/* Who holds the card.
 *
 * REAPS A STALE RECORD rather than reporting it: if the recorded PID is gone,
 * the lock file is removed and this returns SYM_LOCK_NOT_HELD. A card left idle
 * behind a dead holder is the failure this prevents. */
sym_lock_status sym_gpulock_current(sym_lock_holder *out);

/* Acquire for `unit`, waiting up to timeout_ms (0 = try once).
 *
 * Re-entrant for the same unit. A higher-priority unit WAITS rather than
 * preempting: killing a holder mid-inference corrupts its output and leaves
 * VRAM allocated, so yielding is cooperative by design. */
sym_lock_status sym_gpulock_acquire(const char *unit, int timeout_ms,
                                    sym_lock_holder *out);

/* Release. Refuses to release another unit's lock unless `force`.
 * `force` exists only to reap a dead holder, never to jump a queue. */
sym_lock_status sym_gpulock_release(const char *unit, bool force);

/* Human-readable status, for logs and error paths. */
const char *sym_gpulock_strerror(sym_lock_status st);

#ifdef __cplusplus
}
#endif
#endif /* SYMONEURAL_GPULOCK_H */
