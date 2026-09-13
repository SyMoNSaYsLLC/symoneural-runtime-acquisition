/* symoneural/rack.h — rack telemetry: what the hardware is actually doing.
 *
 * Reads the GPU, thermal and memory state that the rack surface reports. No
 * NVML dependency: NVML is a closed NVIDIA library, and linking it would put a
 * proprietary blob in the path of a status endpoint. Everything here comes from
 * sysfs, procfs or nvidia-smi's text output.
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */

#ifndef SYMONEURAL_RACK_H
#define SYMONEURAL_RACK_H

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define SYM_RACK_NAME_MAX 128

typedef struct {
    char  name[SYM_RACK_NAME_MAX];
    long  vram_total_mib;
    long  vram_used_mib;
    long  vram_free_mib;
    int   temperature_c;
    int   power_watts;
    int   power_limit_watts;
    int   utilisation_pct;
    bool  present;             /* false when no GPU could be read at all */
} sym_gpu_state;

typedef struct {
    long  mem_total_kb;
    long  mem_available_kb;
    long  swap_total_kb;
    long  swap_free_kb;
    double load_1;
    double load_5;
    double load_15;
    long  procs_running;
    long  threads_total;       /* the number that predicts desktop starvation */
} sym_host_state;

/* Read GPU state. Returns 0 on success, -1 if no GPU is readable.
 * On -1 the struct is zeroed with present=false, never left undefined. */
int sym_rack_gpu(sym_gpu_state *out);

/* Read host state from /proc. Returns 0 on success, -1 on error. */
int sym_rack_host(sym_host_state *out);

/* Serialise both into JSON. Returns bytes written, or -1 if it would not fit.
 * Never truncates silently: a half-written status object parses as valid JSON
 * and lies. */
int sym_rack_json(char *buf, size_t cap);

#ifdef __cplusplus
}
#endif
#endif /* SYMONEURAL_RACK_H */
