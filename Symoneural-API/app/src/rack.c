/* rack.c — rack telemetry from sysfs, procfs and nvidia-smi.
 *
 * Deliberately no NVML. NVML is a closed NVIDIA library; linking it would put a
 * proprietary blob behind a status endpoint, and the estate's whole claim is
 * that its stack is built from source it holds. nvidia-smi is invoked as a
 * SUBPROCESS whose absence degrades to present=false rather than a link error.
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */

#define _POSIX_C_SOURCE 200809L

#include "symoneural/rack.h"

#include <ctype.h>
#include <fcntl.h>
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

extern char **environ;

/* Read one long from a "key: value" line in a procfs file. */
static bool proc_long(const char *path, const char *key, long *out)
{
    FILE *fh = fopen(path, "re");
    if (fh == NULL)
        return false;

    char line[256];
    const size_t klen = strlen(key);
    bool found = false;
    while (fgets(line, sizeof(line), fh) != NULL) {
        if (strncmp(line, key, klen) != 0)
            continue;
        const char *p = line + klen;
        while (*p == ':' || *p == ' ' || *p == '\t')
            ++p;
        *out = strtol(p, NULL, 10);
        found = true;
        break;
    }
    fclose(fh);
    return found;
}

int sym_rack_host(sym_host_state *out)
{
    if (out == NULL)
        return -1;
    memset(out, 0, sizeof(*out));

    proc_long("/proc/meminfo", "MemTotal",     &out->mem_total_kb);
    proc_long("/proc/meminfo", "MemAvailable", &out->mem_available_kb);
    proc_long("/proc/meminfo", "SwapTotal",    &out->swap_total_kb);
    proc_long("/proc/meminfo", "SwapFree",     &out->swap_free_kb);

    FILE *fh = fopen("/proc/loadavg", "re");
    if (fh != NULL) {
        long running = 0, total = 0;
        if (fscanf(fh, "%lf %lf %lf %ld/%ld",
                   &out->load_1, &out->load_5, &out->load_15,
                   &running, &total) >= 5) {
            out->procs_running = running;
            /* the fifth field counts kernel scheduling entities: threads, not
             * processes - exactly the number the header promises */
            out->threads_total = total;
        }
        fclose(fh);
    }

    /* procs_running from /proc/stat is authoritative when present; the thread
     * total above is the number that actually predicted the desktop lockups on
     * this box: 814 threads on 20 cores starved the compositor, while memory
     * sat at 8%. Memory pressure was never the signal. */
    fh = fopen("/proc/stat", "re");
    if (fh != NULL) {
        char line[256];
        while (fgets(line, sizeof(line), fh) != NULL) {
            if (strncmp(line, "procs_running", 13) == 0) {
                out->procs_running = strtol(line + 13, NULL, 10);
                break;
            }
        }
        fclose(fh);
    }
    return 0;
}

/* Run argv with stdout on a pipe and stderr discarded; copy the first line of
 * output into line (NUL-terminated, newline stripped), drain the rest so the
 * child can exit, reap it. 0 only if it exited 0 and printed something. */
static int spawn_first_line(char *const argv[], char *line, size_t cap)
{
    int fds[2];
    if (cap == 0 || pipe(fds) != 0)
        return -1;

    posix_spawn_file_actions_t fa;
    posix_spawn_file_actions_init(&fa);
    posix_spawn_file_actions_adddup2(&fa, fds[1], STDOUT_FILENO);
    posix_spawn_file_actions_addopen(&fa, STDERR_FILENO, "/dev/null", O_WRONLY, 0);
    posix_spawn_file_actions_addclose(&fa, fds[0]);
    posix_spawn_file_actions_addclose(&fa, fds[1]);

    pid_t pid = 0;
    int rc = posix_spawnp(&pid, argv[0], &fa, NULL, argv, environ);
    posix_spawn_file_actions_destroy(&fa);
    close(fds[1]);
    if (rc != 0) {
        close(fds[0]);
        return -1;
    }

    size_t n = 0;
    bool eol = false;
    char c;
    for (;;) {
        ssize_t r = read(fds[0], &c, 1);
        if (r <= 0)
            break;
        if (eol)
            continue;                      /* drain, so the child is not blocked */
        if (c == '\n') { eol = true; continue; }
        if (n + 1 < cap)
            line[n++] = c;
    }
    close(fds[0]);
    line[n] = '\0';

    int status = 0;
    if (waitpid(pid, &status, 0) != pid)
        return -1;
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0 || n == 0)
        return -1;
    return 0;
}

/* nvidia-smi, queried for exactly the fields we report. One invocation, CSV,
 * no units - anything else means a driver we do not understand, and we say so
 * by returning -1 rather than reporting a guess. */
int sym_rack_gpu(sym_gpu_state *out)
{
    if (out == NULL)
        return -1;
    memset(out, 0, sizeof(*out));
    out->present = false;

    /* A fixed argv through posix_spawnp: no /bin/sh, no string a caller could
     * shape. The reconstruction forbids a shell anywhere in the native API. */
    char *const argv[] = {
        "nvidia-smi",
        "--query-gpu=name,memory.total,memory.used,memory.free,"
        "temperature.gpu,power.draw,power.limit,utilization.gpu",
        "--format=csv,noheader,nounits",
        NULL
    };

    char line[512];
    if (spawn_first_line(argv, line, sizeof(line)) != 0)
        return -1;

    /* name may contain commas in principle; take the first field up to the
     * first comma and parse the numerics from the remainder. */
    char *comma = strchr(line, ',');
    if (comma == NULL)
        return -1;
    *comma = '\0';
    /* Bounded copy, not snprintf("%s"): gcc rightly refuses a 512-byte source
     * into a 128-byte field, and a truncated GPU name is better than a warning
     * silenced. */
    strncpy(out->name, line, sizeof(out->name) - 1);
    out->name[sizeof(out->name) - 1] = '\0';

    double vtot = 0, vused = 0, vfree = 0, pw = 0, pl = 0;
    int temp = 0, util = 0;
    int n = sscanf(comma + 1, " %lf , %lf , %lf , %d , %lf , %lf , %d",
                   &vtot, &vused, &vfree, &temp, &pw, &pl, &util);
    if (n < 4)
        return -1;

    out->vram_total_mib     = (long)vtot;
    out->vram_used_mib      = (long)vused;
    out->vram_free_mib      = (long)vfree;
    out->temperature_c      = temp;
    out->power_watts        = (int)pw;
    out->power_limit_watts  = (int)pl;
    out->utilisation_pct    = util;
    out->present            = true;
    return 0;
}

int sym_rack_json(char *buf, size_t cap)
{
    if (buf == NULL || cap == 0)
        return -1;

    sym_gpu_state gpu;
    sym_host_state host;
    (void)sym_rack_gpu(&gpu);     /* absence is reported, not fatal */
    if (sym_rack_host(&host) != 0)
        return -1;

    int n = snprintf(
        buf, cap,
        "{"
        "\"gpu\":{\"present\":%s,\"name\":\"%s\",\"vram_total_mib\":%ld,"
        "\"vram_used_mib\":%ld,\"vram_free_mib\":%ld,\"temperature_c\":%d,"
        "\"power_watts\":%d,\"power_limit_watts\":%d,\"utilisation_pct\":%d},"
        "\"host\":{\"mem_total_kb\":%ld,\"mem_available_kb\":%ld,"
        "\"swap_total_kb\":%ld,\"swap_free_kb\":%ld,"
        "\"load_1\":%.2f,\"load_5\":%.2f,\"load_15\":%.2f,"
        "\"procs_running\":%ld,\"threads_total\":%ld}"
        "}",
        gpu.present ? "true" : "false", gpu.name,
        gpu.vram_total_mib, gpu.vram_used_mib, gpu.vram_free_mib,
        gpu.temperature_c, gpu.power_watts, gpu.power_limit_watts,
        gpu.utilisation_pct,
        host.mem_total_kb, host.mem_available_kb,
        host.swap_total_kb, host.swap_free_kb,
        host.load_1, host.load_5, host.load_15, host.procs_running,
        host.threads_total);

    /* snprintf truncates silently and the result would still PARSE as JSON
     * while being wrong. Refuse instead. */
    if (n < 0 || (size_t)n >= cap)
        return -1;
    return n;
}
