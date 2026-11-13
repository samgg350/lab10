/*
 * ESE 124 - Exercise 10 - Q1: vending.c - the machine is TWO 2D ARRAYS
 * Name: Sammuel Gomez          SBU ID: ____________
 *
 * YOU write: the two tables, column_of(), vend_step().   (main.c, vending.h, Makefile are given)
 * Copy the table from the handout: every arrow "state --input/action--> next" is ONE cell.
 */
#include "vending.h"

/* TODO 1: fill both tables.  row = state, column = input.
                                                 NICKEL  DIME   QUARTER  CANCEL */
const VState next_state[NUM_STATES][NUM_INPUTS] = {
    /* S0  */ { S5,  S10, S0,  S0 },
    /* S5  */ { S10, S0,  S5,  S0 },
    /* S10 */ { S0,  S0,  S10, S0 } };
const Action action_table[NUM_STATES][NUM_INPUTS] = {
    /* S0  */ { WAIT, WAIT,        REJECT, WAIT   },
    /* S5  */ { WAIT, VEND,        REJECT, REFUND },
    /* S10 */ { VEND, VEND_CHANGE, REJECT, REFUND } };
const int CENTS[NUM_STATES] = { 0, 5, 10 };                     /* given */

static const char *STATE_NAME[NUM_STATES] = { "S0", "S5", "S10" };
static const char *ACTION_NAME[NUM_ACTIONS] = { "WAIT", "VEND", "VEND_CHANGE", "REJECT", "REFUND" };
const char *state_name(VState s) { return STATE_NAME[s]; }      /* given */
const char *action_name(Action a) { return ACTION_NAME[a]; }    /* given */

int column_of(char c) {
    /* TODO 2: 'N' -> NICKEL, 'D' -> DIME, 'Q' -> QUARTER, 'C' -> CANCEL, any other char -> -1 */
    if (c == 'N') return NICKEL;
    if (c == 'D') return DIME;
    if (c == 'Q') return QUARTER;
    if (c == 'C') return CANCEL;
    return -1;
}

Action vend_step(VState *s, int col) {
    /* TODO 3:  Action a = action_table[*s][col];     (output first, OLD state)
                *s = next_state[*s][col];             (then move)
                return a;
       No switch and no if here: the tables ARE the machine.                    */
    Action a = action_table[*s][col];
    *s = next_state[*s][col];
    return a;
}
