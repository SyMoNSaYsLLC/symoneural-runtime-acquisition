/* gpulock.c — single-card arbitration for native units.
 *
 * Implements the protocol in symoneural/gpulock.h. The lock file is the
 * contract shared with the Python control plane, so a C holder is visible to
 * Python and the reverse.
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */

#define _POSIX_C_SOURCE 200809L

#include "symoneural/gpulock.h"

#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <libgen.h>
#include <limits.h>
#include <sys/stat.h>

/* ------------------------------------------------------------------ */
/* Priority table. Kept in step with PRIORITY in gpulock.py.           */
/* ------------------------------------------------------------------ */

struct prio_entry {
    const char *unit;
    int priority;
};

static const struct prio_entry PRIO[] = {
    {"chat",      100},
    {"image",     100},
    {"sigils",     90},
    {"studio",     50},
    {"reinforce",  50},
    {"miner",      10},   /* yields to every interactive surface */
};

int sym_gpulock_priority(const char *unit)
{
    if (unit == NULL)
        return 50;
    for (size_t i = 0; i < sizeof(PRIO) / sizeof(PRIO[0]); ++i) {
        if (strcmp(PRIO[i].unit, unit) == 0)
            return PRIO[i].priority;
    }
    return 50; /* unknown units sit mid-table, never at the top */
}

const char *sym_gpulock_path(void)
{
    const char *env = getenv("SYM_GPU_LOCK");
    return (env != NULL && *env != '\0') ? env : SYM_GPULOCK_DEFAULT_PATH;
}

const char *sym_gpulock_strerror(sym_lock_status st)
{
    switch (st) {
    case SYM_LOCK_OK:        return "ok";
    case SYM_LOCK_BUSY:      return "GPU held by another unit";
    case SYM_LOCK_IO:        return "lock file I/O error";
    case SYM_LOCK_CORRUPT:   return "lock file unparseable";
    case SYM_LOCK_NOT_HELD:  return "lock not held by this unit";
    case SYM_LOCK_INVALID:   return "invalid argument";
    }
    return "unknown";
}

static double now_seconds(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_REALTIME, &ts) != 0)
        return (double)time(NULL);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

/* Is a pid still running?
 *
 * EPERM means it exists and belongs to someone else - that is ALIVE, not
 * absent. Treating EPERM as dead would let one user reap another's lock. */
static bool pid_alive(pid_t pid)
{
    if (pid <= 0)
        return false;
    if (kill(pid, 0) == 0)
        return true;
    return (errno == EPERM);
}

/* ------------------------------------------------------------------ */
/* Minimal JSON reader.                                               */
/*                                                                    */
/* Deliberately not a JSON library. This file has exactly three keys   */
/* written only by us, and a dependency on a parser would put a third  */
/* party in the path of the GPU lock. Anything it cannot understand is */
/* treated as CORRUPT, which is handled as "absent" by the caller -    */
/* fail toward an unlocked card, never toward a phantom holder.        */
/* ------------------------------------------------------------------ */

static bool json_string(const char *buf, const char *key, char *out, size_t cap)
{
    char pattern[64];
    snprintf(pattern, sizeof(pattern), "\"%s\"", key);
    const char *p = strstr(buf, pattern);
    if (p == NULL)
        return false;
    p = strchr(p + strlen(pattern), ':');
    if (p == NULL)
        return false;
    while (*p == ':' || *p == ' ' || *p == '\t')
        ++p;
    if (*p != '"')
        return false;
    ++p;
    size_t i = 0;
    while (*p != '\0' && *p != '"' && i + 1 < cap)
        out[i++] = *p++;
    out[i] = '\0';
    return (*p == '"');
}

static bool json_number(const char *buf, const char *key, double *out)
{
    char pattern[64];
    snprintf(pattern, sizeof(pattern), "\"%s\"", key);
    const char *p = strstr(buf, pattern);
    if (p == NULL)
        return false;
    p = strchr(p + strlen(pattern), ':');
    if (p == NULL)
        return false;
    ++p;
    char *end = NULL;
    double v = strtod(p, &end);
    if (end == p)
        return false;
    *out = v;
    return true;
}

static sym_lock_status read_holder(sym_lock_holder *out)
{
    const char *path = sym_gpulock_path();
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0)
        return (errno == ENOENT) ? SYM_LOCK_NOT_HELD : SYM_LOCK_IO;

    char buf[512];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0)
        return SYM_LOCK_CORRUPT;
    buf[n] = '\0';

    sym_lock_holder h;
    memset(&h, 0, sizeof(h));
    double pid = 0.0;
    if (!json_string(buf, "unit", h.unit, sizeof(h.unit)))
        return SYM_LOCK_CORRUPT;
    if (!json_number(buf, "pid", &pid))
        return SYM_LOCK_CORRUPT;
    if (!json_number(buf, "since", &h.since))
        return SYM_LOCK_CORRUPT;
    h.pid = (pid_t)pid;

    if (out != NULL)
        *out = h;
    return SYM_LOCK_OK;
}

/* mkdir -p for the lock's parent. The run directory may not survive a reboot. */
static int ensure_parent(const char *path)
{
    char tmp[PATH_MAX];
    snprintf(tmp, sizeof(tmp), "%s", path);
    char *dir = dirname(tmp);
    if (mkdir(dir, 0755) == 0 || errno == EEXIST)
        return 0;
    return -1;
}

sym_lock_status sym_gpulock_current(sym_lock_holder *out)
{
    sym_lock_holder h;
    sym_lock_status st = read_holder(&h);
    if (st != SYM_LOCK_OK)
        return st;

    if (!pid_alive(h.pid)) {
        /* Stale: the recorded holder is gone. Reap it rather than report it -
         * a card idle behind a corpse is the failure this exists to prevent. */
        unlink(sym_gpulock_path());
        return SYM_LOCK_NOT_HELD;
    }

    if (out != NULL)
        *out = h;
    return SYM_LOCK_OK;
}

sym_lock_status sym_gpulock_acquire(const char *unit, int timeout_ms,
                                    sym_lock_holder *out)
{
    if (unit == NULL || *unit == '\0' || strlen(unit) >= SYM_GPULOCK_UNIT_MAX)
        return SYM_LOCK_INVALID;

    const char *path = sym_gpulock_path();
    const double deadline = now_seconds() + (double)timeout_ms / 1000.0;
    const struct timespec poll = {.tv_sec = 0, .tv_nsec = 250L * 1000L * 1000L};

    for (;;) {
        sym_lock_holder held;
        sym_lock_status st = sym_gpulock_current(&held);

        if (st == SYM_LOCK_NOT_HELD || st == SYM_LOCK_CORRUPT) {
            if (ensure_parent(path) != 0)
                return SYM_LOCK_IO;

            /* O_EXCL makes creation atomic: whoever creates the file wins,
             * and the loser retries rather than overwriting a live holder. */
            int fd = open(path, O_CREAT | O_EXCL | O_WRONLY | O_CLOEXEC, 0644);
            if (fd >= 0) {
                sym_lock_holder mine;
                memset(&mine, 0, sizeof(mine));
                snprintf(mine.unit, sizeof(mine.unit), "%s", unit);
                mine.pid = getpid();
                mine.since = now_seconds();

                char json[256];
                int len = snprintf(json, sizeof(json),
                                   "{\"unit\":\"%s\",\"pid\":%d,\"since\":%.3f}",
                                   mine.unit, (int)mine.pid, mine.since);
                bool wrote = (len > 0 && write(fd, json, (size_t)len) == (ssize_t)len);
                /* fsync: a lock that survives the write but not a power cut is
                 * worse than none - it strands the card on reboot. */
                if (wrote)
                    fsync(fd);
                close(fd);
                if (!wrote) {
                    unlink(path);
                    return SYM_LOCK_IO;
                }
                if (out != NULL)
                    *out = mine;
                return SYM_LOCK_OK;
            }
            if (errno != EEXIST)
                return SYM_LOCK_IO;
            /* lost the race - fall through and retry */
        } else if (st == SYM_LOCK_OK && strcmp(held.unit, unit) == 0) {
            if (out != NULL)
                *out = held;
            return SYM_LOCK_OK;  /* re-entrant for the same unit */
        } else if (st == SYM_LOCK_IO) {
            return st;
        }

        if (now_seconds() >= deadline) {
            if (out != NULL && sym_gpulock_current(out) != SYM_LOCK_OK)
                memset(out, 0, sizeof(*out));
            return SYM_LOCK_BUSY;
        }
        nanosleep(&poll, NULL);
    }
}

sym_lock_status sym_gpulock_release(const char *unit, bool force)
{
    if (unit == NULL || *unit == '\0')
        return SYM_LOCK_INVALID;

    sym_lock_holder held;
    sym_lock_status st = read_holder(&held);
    if (st != SYM_LOCK_OK)
        return st;

    if (strcmp(held.unit, unit) != 0 && !force)
        return SYM_LOCK_NOT_HELD;

    if (unlink(sym_gpulock_path()) != 0)
        return (errno == ENOENT) ? SYM_LOCK_NOT_HELD : SYM_LOCK_IO;
    return SYM_LOCK_OK;
}
