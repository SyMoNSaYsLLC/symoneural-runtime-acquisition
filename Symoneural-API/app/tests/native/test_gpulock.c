/* gpulock regression: the protocol both halves must keep. */
#define _POSIX_C_SOURCE 200809L
#include "symoneural/gpulock.h"
#include "check.h"
#include <fcntl.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>
#include <time.h>

static char lockpath[256];
static void msleep(int ms) { struct timespec t = {ms / 1000, (ms % 1000) * 1000000L}; nanosleep(&t, NULL); }

static void write_lock(const char *json) {
    int fd = open(lockpath, O_CREAT | O_TRUNC | O_WRONLY, 0644);
    CHECK(fd >= 0); CHECK(write(fd, json, strlen(json)) == (ssize_t)strlen(json)); close(fd);
}

int main(void) {
    const char *td = getenv("TMPDIR"); snprintf(lockpath, sizeof lockpath, "%s/symtest-gpu-%d.lock", td ? td : ".", (int)getpid());
    setenv("SYM_GPU_LOCK", lockpath, 1);
    unlink(lockpath);
    CHECK(strcmp(sym_gpulock_path(), lockpath) == 0);

    /* priorities: one table, known values, unknown mid-table */
    CHECK(sym_gpulock_priority("chat") == 100); CHECK(sym_gpulock_priority("miner") == 10);
    CHECK(sym_gpulock_priority("nosuch") == 50); CHECK(sym_gpulock_priority(NULL) == 50);

    /* nothing held */
    sym_lock_holder h;
    CHECK(sym_gpulock_current(&h) == SYM_LOCK_NOT_HELD);

    /* acquire, observe, busy for another, re-entrant for self */
    CHECK(sym_gpulock_acquire("chat", 0, &h) == SYM_LOCK_OK);
    CHECK(strcmp(h.unit, "chat") == 0 && h.pid == getpid() && h.since > 1.0e9);
    CHECK(sym_gpulock_current(&h) == SYM_LOCK_OK && strcmp(h.unit, "chat") == 0);
    CHECK(sym_gpulock_acquire("miner", 0, NULL) == SYM_LOCK_BUSY);
    CHECK(sym_gpulock_acquire("chat", 0, NULL) == SYM_LOCK_OK);
    /* release refuses a non-holder, accepts the holder */
    CHECK(sym_gpulock_release("miner", false) == SYM_LOCK_NOT_HELD);
    CHECK(sym_gpulock_current(&h) == SYM_LOCK_OK);
    CHECK(sym_gpulock_release("chat", false) == SYM_LOCK_OK);
    CHECK(sym_gpulock_current(&h) == SYM_LOCK_NOT_HELD);
    CHECK(sym_gpulock_release("chat", false) == SYM_LOCK_NOT_HELD);

    /* the Python half's file is readable by the C half (contract) */
    write_lock("{\"unit\": \"studio\", \"pid\": 1, \"since\": 1700000000.5}");
    CHECK(sym_gpulock_current(&h) == SYM_LOCK_OK); /* pid 1 is alive (EPERM counts) */
    CHECK(strcmp(h.unit, "studio") == 0 && h.pid == 1);
    CHECK(sym_gpulock_release("studio", true) == SYM_LOCK_OK);

    /* stale holder is reaped: a child that has exited */
    pid_t dead = fork(); CHECK(dead >= 0);
    if (dead == 0) _exit(0);
    CHECK(waitpid(dead, NULL, 0) == dead);
    char json[128]; snprintf(json, sizeof json, "{\"unit\":\"chat\",\"pid\":%d,\"since\":1.0}", (int)dead);
    write_lock(json);
    CHECK(sym_gpulock_current(&h) == SYM_LOCK_NOT_HELD);
    CHECK(access(lockpath, F_OK) != 0);            /* file removed */

    /* corrupt file: treated as absent, acquire proceeds */
    write_lock("not json at all");
    CHECK(sym_gpulock_acquire("image", 0, &h) == SYM_LOCK_OK);
    CHECK(sym_gpulock_release("image", false) == SYM_LOCK_OK);

    /* invalid arguments */
    CHECK(sym_gpulock_acquire(NULL, 0, NULL) == SYM_LOCK_INVALID);
    CHECK(sym_gpulock_acquire("", 0, NULL) == SYM_LOCK_INVALID);
    CHECK(sym_gpulock_release(NULL, false) == SYM_LOCK_INVALID);

    /* race: six DISTINCT units try at once, exactly one wins. (Re-entrancy is
       keyed by unit NAME, so six processes claiming "chat" would all be granted:
       a unit is a singleton by name and the supervisor owns that guarantee.) */
    static const char *racers[] = {"chat", "image", "sigils", "studio", "reinforce", "miner"};
    int wins = 0;
    for (int i = 0; i < 6; ++i) {
        pid_t c = fork(); CHECK(c >= 0);
        if (c == 0) {
            int ok = sym_gpulock_acquire(racers[i], 0, NULL) == SYM_LOCK_OK;
            /* a winner that exits at once becomes a STALE holder and a later racer
               would rightly reap it - hold the card until every racer has tried */
            if (ok) msleep(600);
            _exit(ok ? 0 : 1);
        }
    }
    for (int i = 0; i < 6; ++i) { int st; CHECK(wait(&st) > 0); if (WIFEXITED(st) && WEXITSTATUS(st) == 0) ++wins; }
    CHECK(wins == 1);
    /* the winner is dead, so the record is stale and gets reaped */
    CHECK(sym_gpulock_current(&h) == SYM_LOCK_NOT_HELD);

    /* bounded wait: 300 ms deadline against a live holder */
    CHECK(sym_gpulock_acquire("chat", 0, NULL) == SYM_LOCK_OK);
    CHECK(sym_gpulock_acquire("miner", 300, &h) == SYM_LOCK_BUSY);
    CHECK(strcmp(h.unit, "chat") == 0);          /* out reports who holds it */
    CHECK(sym_gpulock_release("chat", false) == SYM_LOCK_OK);
    CHECK(strcmp(sym_gpulock_strerror(SYM_LOCK_BUSY), "GPU held by another unit") == 0);
    unlink(lockpath);
    DONE();
}
