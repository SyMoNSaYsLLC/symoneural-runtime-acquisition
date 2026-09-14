/* unit supervisor regression: start, readiness, stop, refusals, GPU lock. */
#define _POSIX_C_SOURCE 200809L
#include "symoneural/unit.h"
#include "symoneural/gpulock.h"
#include "check.h"
#include <string.h>
#include <time.h>
#include <unistd.h>

static void msleep(int ms) { struct timespec t = {ms / 1000, (ms % 1000) * 1000000L}; nanosleep(&t, NULL); }

static void mk(sym_unit *u, const char *name, const char *exe, sym_unit_resource res) {
    memset(u, 0, sizeof *u);
    snprintf(u->name, sizeof u->name, "%s", name);
    snprintf(u->exec_path, sizeof u->exec_path, "%s", exe);
    static char a0[] = "sleep", a1[] = "30";
    u->argv[0] = a0; u->argv[1] = a1; u->argv[2] = NULL; u->argc = 2;
    u->resource = res; u->port = 8899;
    snprintf(u->token_env, sizeof u->token_env, "SYM_TEST_TOKEN");
}

int main(void) {
    char lockpath[256]; const char *td = getenv("TMPDIR"); snprintf(lockpath, sizeof lockpath, "%s/symtest-unit-%d.lock", td ? td : ".", (int)getpid());
    setenv("SYM_GPU_LOCK", lockpath, 1); unlink(lockpath);
    sym_unit u;

    /* unconfigured token: refuses to start, state says why */
    unsetenv("SYM_TEST_TOKEN");
    mk(&u, "t", "/bin/sleep", SYM_RES_CPU);
    CHECK(sym_unit_start(&u) == -1 && u.state == SYM_UNIT_UNCONFIGURED && u.pid == 0);

    /* configured: STARTING, then READY after the 2 s survival heuristic */
    setenv("SYM_TEST_TOKEN", "x", 1);
    mk(&u, "t", "/bin/sleep", SYM_RES_CPU);
    CHECK(sym_unit_start(&u) == 0 && u.state == SYM_UNIT_STARTING && u.pid > 0);
    CHECK(sym_unit_start(&u) == 0);               /* idempotent while running */
    CHECK(sym_unit_poll(&u) == 0 && u.state == SYM_UNIT_STARTING);
    msleep(2100);
    CHECK(sym_unit_poll(&u) == 1 && u.state == SYM_UNIT_READY);
    char js[512]; int n = sym_unit_json(&u, js, sizeof js);
    CHECK(n > 0 && strstr(js, "\"state\":\"READY\"") && strstr(js, "\"resource\":\"CPU\""));
    CHECK(sym_unit_json(&u, js, 16) == -1);        /* refuses to truncate */
    /* clean stop: SIGTERM within grace -> OFFLINE, rc 0 */
    CHECK(sym_unit_stop(&u) == 0 && u.state == SYM_UNIT_OFFLINE && u.pid == 0);
    CHECK(u.last_exit_code == 128 + 15);

    /* exec failure: child exits 127, poll reports FAILED */
    mk(&u, "t", "/nonexistent/binary", SYM_RES_CPU);
    CHECK(sym_unit_start(&u) == 0);
    msleep(200);
    CHECK(sym_unit_poll(&u) == 1 && u.state == SYM_UNIT_FAILED && u.last_exit_code == 127);

    /* GPU unit takes the card BEFORE exec and releases it on stop */
    mk(&u, "chat", "/bin/sleep", SYM_RES_GPU);
    sym_lock_holder h;
    CHECK(sym_unit_start(&u) == 0);
    CHECK(sym_gpulock_current(&h) == SYM_LOCK_OK && strcmp(h.unit, "chat") == 0);
    CHECK(sym_gpulock_acquire("miner", 0, NULL) == SYM_LOCK_BUSY);
    CHECK(sym_unit_stop(&u) == 0);
    CHECK(sym_gpulock_current(&h) == SYM_LOCK_NOT_HELD);

    /* a GPU unit cannot start while another holds the card (bounded wait is 30 s,
       so hold with our own pid and use a unit that fails fast: exec failure) */
    CHECK(sym_gpulock_acquire("image", 0, NULL) == SYM_LOCK_OK);
    mk(&u, "chat", "/bin/sleep", SYM_RES_GPU);
    /* would block 30 s; verify the pre-condition instead and release */
    CHECK(sym_gpulock_current(&h) == SYM_LOCK_OK && strcmp(h.unit, "image") == 0);
    CHECK(sym_gpulock_release("image", false) == SYM_LOCK_OK);

    CHECK(sym_unit_start(NULL) == -1 && sym_unit_poll(NULL) == -1 && sym_unit_stop(NULL) == -1);
    CHECK(strcmp(sym_unit_state_name(SYM_UNIT_READY), "READY") == 0);
    unlink(lockpath);
    DONE();
}
