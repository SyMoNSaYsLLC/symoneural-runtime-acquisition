#ifndef SYM_TEST_CHECK_H
#define SYM_TEST_CHECK_H
#include <stdio.h>
#include <stdlib.h>
static int sym_checks = 0;
#define CHECK(cond) do { ++sym_checks; if (!(cond)) { fprintf(stderr, "  FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); exit(1); } } while (0)
#define DONE() do { printf("  %d checks passed\n", sym_checks); return 0; } while (0)
#endif
