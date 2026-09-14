/* unit.c — unit supervision: fork, watch, stop.
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */

#define _POSIX_C_SOURCE 200809L

#include "symoneural/unit.h"
#include "symoneural/gpulock.h"

#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

const char *sym_unit_state_name(sym_unit_state st)
{
    switch (st) {
    case SYM_UNIT_OFFLINE:      return "OFFLINE";
    case SYM_UNIT_STARTING:     return "STARTING";
    case SYM_UNIT_READY:        return "READY";
    case SYM_UNIT_STOPPING:     return "STOPPING";
    case SYM_UNIT_FAILED:       return "FAILED";
    case SYM_UNIT_UNCONFIGURED: return "UNCONFIGURED";
    }
    return "UNKNOWN";
}

/* A unit whose token is unprovisioned must not come up.
 *
 * Failing closed matters more here than anywhere else: a unit that starts
 * without a token is an unauthenticated surface on the rack, and it would look
 * healthy while being wide open. */
static bool token_present(const sym_unit *u)
{
    if (u->token_env[0] == '\0')
        return false;
    const char *v = getenv(u->token_env);
    return (v != NULL && *v != '\0');
}

int sym_unit_start(sym_unit *u)
{
    if (u == NULL || u->exec_path[0] == '\0' || u->argc <= 0)
        return -1;

    if (u->state == SYM_UNIT_READY || u->state == SYM_UNIT_STARTING)
        return 0;                       /* idempotent */

    if (!token_present(u)) {
        u->state = SYM_UNIT_UNCONFIGURED;
        return -1;
    }

    /* A GPU unit takes the card BEFORE exec. Taking it afterwards would leave a
     * window in which the process is live and touching the device without
     * holding the lock - which is exactly the state the lock exists to make
     * impossible. */
    if (u->resource == SYM_RES_GPU) {
        sym_lock_status st = sym_gpulock_acquire(u->name, 30000, NULL);
        if (st != SYM_LOCK_OK) {
            u->state = SYM_UNIT_FAILED;
            return -1;
        }
    }

    pid_t pid = fork();
    if (pid < 0) {
        if (u->resource == SYM_RES_GPU)
            sym_gpulock_release(u->name, false);
        u->state = SYM_UNIT_FAILED;
        return -1;
    }

    if (pid == 0) {
        /* Child. Its own process group, so stopping the unit stops everything
         * it spawned - llama-server and GStreamer both fork helpers, and
         * signalling only the parent leaves those holding VRAM. */
        setpgid(0, 0);

        /* Restore default handling: a child inheriting SIG_IGN cannot be
         * stopped by the signal the supervisor is about to rely on. */
        signal(SIGTERM, SIG_DFL);
        signal(SIGINT,  SIG_DFL);
        signal(SIGPIPE, SIG_DFL);

        execv(u->exec_path, u->argv);
        _exit(127);                     /* exec failed; 127 is the convention */
    }

    /* The parent puts the child in its own group too. Only the child doing it
     * leaves a window in which kill(-pid) from a fast stop() gets ESRCH, the
     * unit is declared gone, the process leaks and the GPU lock stays held -
     * caught by tests/native/test_unit.c. EACCES/ESRCH here mean the child has
     * already exec'd or exited, and both are harmless. */
    (void)setpgid(pid, pid);

    u->pid = pid;
    u->state = SYM_UNIT_STARTING;
    u->started_at = time(NULL);
    u->last_exit_code = 0;
    return 0;
}

int sym_unit_poll(sym_unit *u)
{
    if (u == NULL)
        return -1;
    if (u->pid <= 0)
        return 0;

    int status = 0;
    pid_t r = waitpid(u->pid, &status, WNOHANG);

    if (r == 0) {
        /* Still running. STARTING becomes READY once it has survived long
         * enough to have bound its port; a process that exits immediately
         * never reaches READY and is reported FAILED instead. */
        if (u->state == SYM_UNIT_STARTING &&
            difftime(time(NULL), u->started_at) >= 2.0) {
            u->state = SYM_UNIT_READY;
            return 1;
        }
        return 0;
    }

    if (r < 0) {
        if (errno == ECHILD) {          /* already reaped */
            u->pid = 0;
            u->state = SYM_UNIT_OFFLINE;
            return 1;
        }
        return -1;
    }

    /* Exited. Release the card unconditionally - if this unit did not hold it
     * the release is refused, and if it did, the card must not stay locked
     * behind a dead process. */
    if (u->resource == SYM_RES_GPU)
        sym_gpulock_release(u->name, false);

    if (WIFEXITED(status)) {
        u->last_exit_code = WEXITSTATUS(status);
        u->state = (u->last_exit_code == 0) ? SYM_UNIT_OFFLINE : SYM_UNIT_FAILED;
    } else if (WIFSIGNALED(status)) {
        u->last_exit_code = 128 + WTERMSIG(status);
        /* SIGTERM during a deliberate stop is success, not failure. */
        u->state = (u->state == SYM_UNIT_STOPPING && WTERMSIG(status) == SIGTERM)
                       ? SYM_UNIT_OFFLINE
                       : SYM_UNIT_FAILED;
    } else {
        u->state = SYM_UNIT_FAILED;
    }

    u->pid = 0;
    return 1;
}

int sym_unit_stop(sym_unit *u)
{
    if (u == NULL)
        return -1;
    if (u->pid <= 0) {
        u->state = SYM_UNIT_OFFLINE;
        return 0;
    }

    u->state = SYM_UNIT_STOPPING;

    /* Negative pid: signal the whole process group, not just the leader. If the
     * group is not there, signal the pid itself; only if THAT is gone too is the
     * unit already dead - and even then poll() must reap it and release the card. */
    if (kill(-u->pid, SIGTERM) != 0 && errno == ESRCH &&
        kill(u->pid, SIGTERM) != 0 && errno == ESRCH) {
        (void)sym_unit_poll(u);
        if (u->resource == SYM_RES_GPU)
            sym_gpulock_release(u->name, false);
        u->pid = 0;
        u->state = SYM_UNIT_OFFLINE;
        return 0;
    }

    /* Grace. A GPU unit needs time to free VRAM and drop its lock; killing it
     * at once strands both, and the next unit inherits a device that is still
     * allocated. */
    const struct timespec tick = {.tv_sec = 0, .tv_nsec = 100L * 1000L * 1000L};
    for (int waited_ms = 0; waited_ms < SYM_UNIT_STOP_GRACE_S * 1000;
         waited_ms += 100) {
        if (sym_unit_poll(u) == 1 && u->pid == 0)
            return 0;
        nanosleep(&tick, NULL);
    }

    kill(-u->pid, SIGKILL);
    (void)sym_unit_poll(u);
    if (u->resource == SYM_RES_GPU)
        sym_gpulock_release(u->name, true);   /* force: the holder is gone */
    u->pid = 0;
    u->state = SYM_UNIT_OFFLINE;
    return -1;                                 /* stopped, but not cleanly */
}

int sym_unit_json(const sym_unit *u, char *buf, size_t cap)
{
    if (u == NULL || buf == NULL || cap == 0)
        return -1;

    static const char *res[] = {"CPU", "GPU", "NET"};
    int n = snprintf(
        buf, cap,
        "{\"unit\":\"%s\",\"state\":\"%s\",\"resource\":\"%s\",\"port\":%d,"
        "\"pid\":%d,\"uptime_s\":%.0f,\"restarts\":%d,\"last_exit\":%d}",
        u->name, sym_unit_state_name(u->state),
        res[u->resource <= SYM_RES_NET ? u->resource : 0],
        u->port, (int)u->pid,
        (u->pid > 0 && u->started_at) ? difftime(time(NULL), u->started_at) : 0.0,
        u->restart_count, u->last_exit_code);

    if (n < 0 || (size_t)n >= cap)
        return -1;
    return n;
}
