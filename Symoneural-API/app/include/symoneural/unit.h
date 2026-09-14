/* symoneural/unit.h — the unit supervisor.
 *
 * A "unit" is one addressable surface on the rack: a native process the
 * supervisor starts, watches, and stops. This is the C half of DispatchOS -
 * the part that owns real processes rather than HTTP routes.
 *
 * Units are native binaries (llama-server, the miner, GStreamer pipelines) so
 * supervision belongs in C: it needs fork/exec, process groups, signal
 * handling and waitpid, none of which survive being proxied through a Python
 * web process that may itself be restarted.
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */

#ifndef SYMONEURAL_UNIT_H
#define SYMONEURAL_UNIT_H

#include <stdbool.h>
#include <sys/types.h>
#include <time.h>

#ifdef __cplusplus
extern "C" {
#endif

#define SYM_UNIT_NAME_MAX   64
#define SYM_UNIT_ARGV_MAX   32
#define SYM_UNIT_PATH_MAX   512

typedef enum {
    SYM_UNIT_OFFLINE = 0,   /* not started                                  */
    SYM_UNIT_STARTING,      /* forked, not yet confirmed listening          */
    SYM_UNIT_READY,         /* running and answering                        */
    SYM_UNIT_STOPPING,      /* SIGTERM sent, grace period running           */
    SYM_UNIT_FAILED,        /* exited non-zero, or never became ready       */
    SYM_UNIT_UNCONFIGURED   /* no token provisioned; refuses to start       */
} sym_unit_state;

typedef enum {
    SYM_RES_CPU = 0,        /* never queues for the card */
    SYM_RES_GPU,            /* contends for the single-card lock */
    SYM_RES_NET             /* I/O bound */
} sym_unit_resource;

typedef struct {
    char              name[SYM_UNIT_NAME_MAX];
    char              exec_path[SYM_UNIT_PATH_MAX];
    char             *argv[SYM_UNIT_ARGV_MAX];
    int               argc;
    sym_unit_resource resource;
    int               port;
    char              token_env[SYM_UNIT_NAME_MAX];

    /* runtime state - owned by the supervisor, never set by a caller */
    pid_t             pid;
    sym_unit_state    state;
    time_t            started_at;
    int               restart_count;
    int               last_exit_code;
} sym_unit;

/* Grace period between SIGTERM and SIGKILL. A unit holding the GPU needs time
 * to release VRAM and its lock; killing it immediately strands both. */
#define SYM_UNIT_STOP_GRACE_S 10

const char *sym_unit_state_name(sym_unit_state st);

/* Start a unit. Returns 0 on success, -1 on failure.
 *
 * Refuses if the unit's token is unprovisioned - an unconfigured unit must not
 * come up serving. GPU units take the card lock BEFORE exec, so a unit never
 * reaches the device without holding it. */
int sym_unit_start(sym_unit *u);

/* Reap and update state without blocking. Call from the supervisor loop.
 * Returns 1 if the state changed, 0 if not, -1 on error. */
int sym_unit_poll(sym_unit *u);

/* SIGTERM, wait up to SYM_UNIT_STOP_GRACE_S, then SIGKILL. Releases the GPU
 * lock if this unit held it. Returns 0 if it stopped cleanly. */
int sym_unit_stop(sym_unit *u);

/* Serialise one unit as JSON. Returns bytes written, -1 if it would not fit. */
int sym_unit_json(const sym_unit *u, char *buf, size_t cap);

#ifdef __cplusplus
}
#endif
#endif /* SYMONEURAL_UNIT_H */
