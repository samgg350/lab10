#ifndef FRFR_H
#define FRFR_H

/* Count "frfr" (for real, for real) in chat messages - a pattern FSM solved with SWITCH.
   The state = how much of F R F R we have matched so far.
   Upper and lower case are the same letter ('f' == 'F').                         */
typedef enum { S0, S_F, S_FR, S_FRF, NUM_STATES } FState;
/*            ""   "F"  "FR"   "FRF"                                              */

#define LINE_LEN 200

/* ONE step: switch (s), then look at the letter (use toupper).
   Set *found = 1 on the letter that completes F R F R, otherwise *found = 0.
   OVERLAP: after a match go to S_FR, because the last "FR" can start the next one
   ("FRFRFR" contains 2).  Return the next state. */
FState frfr_step(FState s, char c, int *found);

/* Run the machine over text, starting in S0. Return how many FRFR it found.
   NULL or "" -> 0.   Do NOT use strstr / strncmp: use frfr_step. */
int count_frfr(const char *text);

#endif
