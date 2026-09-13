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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
                   &running, &total) >= 3) {
            out->procs_running = running;
        }
        fclose(fh);
    }

    /* Thread count is the number that actually predicts the desktop lockups on
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

/* nvidia-smi, queried for exactly the fields we report. One invocation, CSV,
 * no units - anything else means a driver we do not understand, and we say so
 * by returning -1 rather than reporting a guess. */
int sym_rack_gpu(sym_gpu_state *out)
{
    if (out == NULL)
        return -1;
    memset(out, 0, sizeof(*out));
    out->present = false;

    const char *cmd =
        "nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,"
        "temperature.gpu,power.draw,power.limit,utilization.gpu "
        "--format=csv,noheader,nounits 2>/dev/null";

    FILE *pipe = popen(cmd, "re");
    if (pipe == NULL)
        return -1;

    char line[512];
    char *got = fgets(line, sizeof(line), pipe);
    int rc = pclose(pipe);
    if (got == NULL || rc != 0)
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
        "\"procs_running\":%ld}"
        "}",
        gpu.present ? "true" : "false", gpu.name,
        gpu.vram_total_mib, gpu.vram_used_mib, gpu.vram_free_mib,
        gpu.temperature_c, gpu.power_watts, gpu.power_limit_watts,
        gpu.utilisation_pct,
        host.mem_total_kb, host.mem_available_kb,
        host.swap_total_kb, host.swap_free_kb,
        host.load_1, host.load_5, host.load_15, host.procs_running);

    /* snprintf truncates silently and the result would still PARSE as JSON
     * while being wrong. Refuse instead. */
    if (n < 0 || (size_t)n >= cap)
        return -1;
    return n;
}
