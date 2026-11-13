#ifndef STRIP_H
#define STRIP_H

/* Remove the block comments from C code - a MEALY machine with 4 states, solved BOTH ways.
     CODE   normal code                    SLASH  saw one '/' in code (maybe a comment)
     BLOCK  inside a comment               STAR   saw '*' inside a comment (maybe the end)
   Only block comments (slash-star ... star-slash) are removed. */
typedef enum { CODE, SLASH, BLOCK, STAR, NUM_STATES } SState;
typedef enum { C_SLASH, C_STAR, C_OTHER, NUM_CLASSES } CharClass;   /* '/'  '*'  anything else */

/* The OUTPUT of an arrow = what to write to the clean text:
     A_NONE  write nothing          A_COPY   write the char c
     A_FLUSH write '/' then c       (the '/' we held was NOT a comment)
     A_START write nothing, count one more comment
     A_SPACE write one ' '          (the comment ends: it becomes one space)            */
typedef enum { A_NONE, A_COPY, A_FLUSH, A_START, A_SPACE, NUM_ACTIONS } Action;

#define MAX_TEXT 4000

/* WAY 2 - the tables: row = state, column = char class              YOU fill them in strip.c */
extern const SState next_table[NUM_STATES][NUM_CLASSES];
extern const Action act_table[NUM_STATES][NUM_CLASSES];

SState next_switch(SState s, CharClass c, Action *a);     /* YOU - WAY 1: switch (s) + if on c     */
SState next_by_table(SState s, CharClass c, Action *a);   /* YOU - WAY 2: *a = act_table[s][c];
                                                                          return next_table[s][c]; */
CharClass class_of(char c);                               /* GIVEN                                 */
/* GIVEN: strip src into dst with way 1 (use_table = 0) or way 2 (use_table = 1).
   Counts the comments in *comments. Returns 1 if the text ends INSIDE a comment, else 0. */
int strip_text(const char *src, char dst[], int use_table, int *comments);

#endif
