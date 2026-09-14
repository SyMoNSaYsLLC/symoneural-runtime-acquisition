/* rack telemetry regression: host fields, JSON shape, non-truncation. */
#define _POSIX_C_SOURCE 200809L
#include "symoneural/rack.h"
#include "check.h"
#include <string.h>

int main(void) {
    sym_host_state h;
    CHECK(sym_rack_host(&h) == 0);
    CHECK(h.mem_total_kb > 0 && h.mem_available_kb > 0 && h.load_1 >= 0.0);
    CHECK(h.threads_total > 0 && h.threads_total >= h.procs_running);   /* /proc/loadavg 5th field */
    CHECK(sym_rack_host(NULL) == -1);

    sym_gpu_state g;
    int rc = sym_rack_gpu(&g);
    /* either a GPU is readable and present, or it is reported absent - never undefined */
    CHECK((rc == 0 && g.present && g.vram_total_mib > 0) || (rc == -1 && !g.present));
    CHECK(sym_rack_gpu(NULL) == -1);

    char buf[2048];
    int n = sym_rack_json(buf, sizeof buf);
    CHECK(n > 0 && buf[0] == '{' && buf[n - 1] == '}');
    CHECK(strstr(buf, "\"gpu\":{\"present\":") && strstr(buf, "\"host\":{\"mem_total_kb\":"));
    CHECK(strstr(buf, "\"threads_total\":") != NULL);
    CHECK(sym_rack_json(buf, 32) == -1);       /* refuses to truncate */
    CHECK(sym_rack_json(NULL, 10) == -1 && sym_rack_json(buf, 0) == -1);
    DONE();
}
