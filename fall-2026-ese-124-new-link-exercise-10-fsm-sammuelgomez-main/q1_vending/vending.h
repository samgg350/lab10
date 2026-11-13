#ifndef VENDING_H
#define VENDING_H

/* BroBot's 15-cent snack machine - a MEALY machine solved with 2D ARRAYS.
   The state is the money inside the machine: 0, 5 or 10 cents.            */
typedef enum { S0, S5, S10, NUM_STATES } VState;

/* The inputs (columns). coins.txt uses one letter per input:
   N = nickel (5c)   D = dime (10c)   Q = quarter (not accepted)   C = cancel  */
typedef enum { NICKEL, DIME, QUARTER, CANCEL, NUM_INPUTS } Input;

/* The outputs (what the machine does on that arrow). */
typedef enum { WAIT, VEND, VEND_CHANGE, REJECT, REFUND, NUM_ACTIONS } Action;

#define CHANGE_CENTS 5          /* VEND_CHANGE always gives back one nickel        */

/* The whole diagram as two tables: row = state, column = input.  (vending.c) */
extern const VState next_state[NUM_STATES][NUM_INPUTS];
extern const Action action_table[NUM_STATES][NUM_INPUTS];
extern const int    CENTS[NUM_STATES];          /* money held in each state: 0, 5, 10 */

/* 'N' -> NICKEL, 'D' -> DIME, 'Q' -> QUARTER, 'C' -> CANCEL, any other char -> -1 */
int column_of(char c);

/* S0 -> "S0" ...    WAIT -> "WAIT" ...   (GIVEN in vending.c) */
const char *state_name(VState s);
const char *action_name(Action a);

/* ONE step with the tables: a = action_table[*s][col]; *s = next_state[*s][col]; return a.
   No switch and no if here - the tables ARE the machine. */
Action vend_step(VState *s, int col);

#endif
