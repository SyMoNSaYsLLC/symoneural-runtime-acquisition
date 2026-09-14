/* ABI-level regression: versions, errors, bounded buffers, table enumeration, lock mapping, selftest. */
#define _POSIX_C_SOURCE 200809L
#include "symoneural/api.h"
#include "check.h"
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(void) {
    char lockpath[256]; const char *td = getenv("TMPDIR");
    snprintf(lockpath, sizeof lockpath, "%s/symtest-api-%d.lock", td ? td : ".", (int)getpid());
    setenv("SYM_GPU_LOCK", lockpath, 1); unlink(lockpath);

    CHECK(sym_api_abi_version() == SYM_API_ABI_VERSION);
    CHECK((sym_api_abi_version() >> 16) == SYM_API_ABI_MAJOR);
    CHECK(strcmp(sym_api_version_string(), "1.0.0") == 0);
    CHECK(strcmp(sym_api_strerror(SYM_API_EBUSY), "GPU held by another unit") == 0);

    char b[256];
    CHECK(sym_api_capabilities(b, sizeof b) == SYM_API_OK && strstr(b, "gpu-lock"));
    CHECK(sym_api_capabilities(b, 4) == SYM_API_ENOSPC);          /* bounded, no truncation */
    CHECK(sym_api_capabilities(NULL, 4) == SYM_API_EINVAL);
    CHECK(sym_api_lock_path(b, sizeof b) == SYM_API_OK && strcmp(b, lockpath) == 0);

    /* one priority table, enumerable and consistent with lookup */
    int n = 0, p; char u[64];
    while (sym_api_priority_entry(n, u, sizeof u, &p) == SYM_API_OK) { CHECK(sym_api_priority(u) == p); ++n; }
    CHECK(n == 6);
    CHECK(sym_api_priority_entry(n, u, sizeof u, &p) == SYM_API_ENOENT);
    CHECK(sym_api_priority_entry(0, u, 2, &p) == SYM_API_ENOSPC);

    sym_lock_holder h;
    CHECK(sym_api_lock_current(&h) == SYM_API_ENOTHELD);
    CHECK(sym_api_lock_acquire("chat", 0, &h) == SYM_API_OK && h.pid == getpid());
    CHECK(sym_api_lock_acquire("miner", 0, NULL) == SYM_API_EBUSY);
    CHECK(sym_api_lock_release("miner", 0) == SYM_API_ENOTHELD);
    CHECK(sym_api_lock_release("chat", 0) == SYM_API_OK);
    CHECK(sym_api_lock_acquire("", 0, NULL) == SYM_API_EINVAL);

    char js[2048];
    CHECK(sym_api_rack_json(js, sizeof js) == SYM_API_OK && js[0] == '{');
    CHECK(sym_api_rack_json(js, 8) == SYM_API_ENOSPC);

    char r[128];
    CHECK(sym_api_selftest(r, sizeof r) == SYM_API_OK && strstr(r, "PASS"));
    CHECK(access(lockpath, F_OK) != 0);                            /* selftest left nothing behind */
    unlink(lockpath);
    DONE();
}
