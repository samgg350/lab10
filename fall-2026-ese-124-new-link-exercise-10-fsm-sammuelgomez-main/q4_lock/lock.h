#ifndef LOCK_H
#define LOCK_H

/* The CAD Lab door lock: type 0 1 1 0 and the door opens.
   A MEALY machine: every arrow is  input/output.  Output 1 = OPEN the door.
   The state remembers how much of 0 1 1 0 you have typed so far:
       SX = nothing   S0 = "0"   S01 = "01"   S011 = "011"
   Any key that is not 0 or 1 is a WRONG key: column ERR, back to SX, output 0. */
typedef enum { SX, S0, S01, S011, NUM_STATES } LState;
typedef enum { IN0, IN1, ERR, NUM_INPUTS } LInput;

#define MAX_KEYS 60
#define LINE_LEN 100

/* row = current state, column = input (IN0 / IN1 / ERR)          YOU fill them in lock.c */
extern const LState next_state[NUM_STATES][NUM_INPUTS];
extern const int    out_table[NUM_STATES][NUM_INPUTS];

int column_of(char c);                  /* YOU:   '0' -> IN0, '1' -> IN1, anything else -> ERR   */
int lock_step(LState *s, int col);      /* YOU:   out = out_table[*s][col];
                                                  *s  = next_state[*s][col];  return out;        */
const char *state_name(LState s);       /* GIVEN: SX -> "SX" ...                                 */
/* GIVEN: run one line of keys from SX. trace[0] = SX, trace[i] = state after key i,
   u[] = the output of every key as '0'/'1' (+ '\0'). Returns the number of times the door opened. */
int run_log(const char *keys, LState trace[], char u[]);

#endif
