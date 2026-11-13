/*
 * ESE 124 - Exercise 10 - Q4: lock.c - the door lock as a MEALY machine with 2D ARRAYS
 * Name: Sammuel Gomez          SBU ID: ____________
 *
 * YOU write: the two tables, column_of(), lock_step().   (main.c, lock.h, Makefile are given)
 * The arrows (input/output). Copy each one into ONE cell of next_state AND out_table:
 *     SX   --0/0--> S0     SX   --1/0--> SX
 *     S0   --0/0--> S0     S0   --1/0--> S01
 *     S01  --0/0--> S0     S01  --1/0--> S011
 *     S011 --0/1--> S0     S011 --1/0--> SX       <- 0 1 1 0 typed: output 1 = OPEN
 *     any state --ERR/0--> SX                     (a key that is not 0 or 1)
 */
#include <string.h>
#include "lock.h"

/* TODO 1: fill both tables (4 rows x 3 columns).  row = state, column = input.
                                                 IN0  IN1  ERR */
const LState next_state[NUM_STATES][NUM_INPUTS] = {
    /* SX   */ { S0, SX,   SX },
    /* S0   */ { S0, S01,  SX },
    /* S01  */ { S0, S011, SX },
    /* S011 */ { S0, SX,   SX } };
const int out_table[NUM_STATES][NUM_INPUTS] = {
    /* SX   */ { 0, 0, 0 },
    /* S0   */ { 0, 0, 0 },
    /* S01  */ { 0, 0, 0 },
    /* S011 */ { 1, 0, 0 } };

int column_of(char c) {
    /* TODO 2: '0' -> IN0, '1' -> IN1, anything else -> ERR */
    if (c == '0') return IN0;
    if (c == '1') return IN1;
    return ERR;
}

int lock_step(LState *s, int col) {
    /* TODO 3:  int out = out_table[*s][col];     (output first, OLD state)
                *s = next_state[*s][col];         (then move)
                return out;
       No switch and no if here.                                                  */
    int out = out_table[*s][col];
    *s = next_state[*s][col];
    return out;
}

/* ---------- GIVEN ---------- */
static const char *NAME[NUM_STATES] = { "SX", "S0", "S01", "S011" };

const char *state_name(LState s) { return NAME[s]; }

int run_log(const char *keys, LState trace[], char u[]) {
    int n = (int)strlen(keys), opens = 0;
    LState s = SX;
    trace[0] = s;
    for (int i = 0; i < n; i++) {
        int out = lock_step(&s, column_of(keys[i]));
        trace[i + 1] = s;
        u[i] = (char)('0' + out);
        opens += out;
    }
    u[n] = '\0';
    return opens;
}
