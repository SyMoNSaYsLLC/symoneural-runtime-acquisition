# Regression tests for the first-party API C (A0). Host build; the same sources
# later become libsymoneural-api. `make test` builds and runs every test.
CC      ?= cc
CFLAGS  ?= -std=c11 -Wall -Wextra -Werror -O1 -g
SRC     := ../../src
INC     := ../../include
OBJS    := $(SRC)/gpulock.c $(SRC)/unit.c $(SRC)/rack.c
TESTS   := test_gpulock test_unit test_rack

all: $(TESTS)

test_%: test_%.c $(OBJS) $(INC)/symoneural/*.h
	$(CC) $(CFLAGS) -I$(INC) $(OBJS) $< -o $@

test: all
	@set -e; for t in $(TESTS); do echo "== $$t"; ./$$t; done; echo "ALL NATIVE TESTS PASS"

clean:
	rm -f $(TESTS)
.PHONY: all test clean
