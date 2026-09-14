/* symoneural-api-util — generic native diagnostics over the ABI. No customer
 * names, no routes, no secret values: paths and states only.
 *
 * Copyright (c) 2026 SyMoNeuRaL. SPDX-License-Identifier: MIT
 */
#define _POSIX_C_SOURCE 200809L
#include "symoneural/api.h"
#include <stdio.h>
#include <string.h>

static int usage(void)
{
    fprintf(stderr, "usage: symoneural-api-util version|abi|capabilities|units|lock-status|selftest|doctor\n");
    return 2;
}

static void lock_status(void)
{
    sym_lock_holder h;
    int st = sym_api_lock_current(&h);
    char path[512];
    sym_api_lock_path(path, sizeof path);
    if (st == SYM_API_OK)
        printf("{\"lock_path\":\"%s\",\"held\":true,\"unit\":\"%s\",\"pid\":%d,\"since\":%.3f}\n", path, h.unit, (int)h.pid, h.since);
    else
        printf("{\"lock_path\":\"%s\",\"held\":false,\"status\":\"%s\"}\n", path, sym_api_strerror(st));
}

int main(int argc, char **argv)
{
    if (argc < 2) return usage();
    const char *cmd = argv[1];
    if (strcmp(cmd, "version") == 0) { printf("%s\n", sym_api_version_string()); return 0; }
    if (strcmp(cmd, "abi") == 0) { printf("%u\n", sym_api_abi_version()); return 0; }
    if (strcmp(cmd, "capabilities") == 0) { char b[256]; if (sym_api_capabilities(b, sizeof b)) return 1; printf("%s\n", b); return 0; }
    if (strcmp(cmd, "units") == 0) {
        /* the units the lock knows, with their priorities: the one table */
        char u[64]; int p;
        for (int i = 0; sym_api_priority_entry(i, u, sizeof u, &p) == SYM_API_OK; ++i) printf("%s %d\n", u, p);
        return 0;
    }
    if (strcmp(cmd, "lock-status") == 0) { lock_status(); return 0; }
    if (strcmp(cmd, "selftest") == 0) { char r[128]; int rc = sym_api_selftest(r, sizeof r); printf("%s\n", r); return rc ? 1 : 0; }
    if (strcmp(cmd, "doctor") == 0) {
        char b[2048], r[128], path[512];
        printf("symoneural-api %s (abi %u)\n", sym_api_version_string(), sym_api_abi_version());
        sym_api_capabilities(b, sizeof b); printf("capabilities: %s\n", b);
        sym_api_lock_path(path, sizeof path); printf("lock path   : %s\n", path);
        int rc = sym_api_selftest(r, sizeof r); printf("%s\n", r);
        int tj = sym_api_rack_json(b, sizeof b); printf("telemetry   : %s\n", tj == SYM_API_OK ? (strstr(b, "\"present\":true") ? "gpu present" : "no gpu readable (host only)") : sym_api_strerror(tj));
        return rc ? 1 : 0;
    }
    return usage();
}
