/*
 * ESE 124 - Exercise 10 - Q5: strip.c - ONE machine written TWO ways
 * Name: ____________________   SBU ID: ____________
 *
 * YOU write: next_switch() (way 1), the two tables and next_by_table() (way 2).
 * main.c prints AGREE=YES only when both ways give exactly the same clean code.
 */
#include "strip.h"

/* ---------- YOU: WAY 1 - switch on the state, if on the char class ---------- */
SState next_switch(SState s, CharClass c, Action *a) {
    /* TODO 1: one case per state, an if per char class. Use the arrow table in the handout.
         switch (s) {
         case CODE:
             if (c == C_SLASH) { *a = A_NONE; return SLASH; }    (hold the '/')
             *a = A_COPY;  return CODE;
         case SLASH:  ...
         case BLOCK:  ...
         case STAR:   ...
         default:     *a = A_NONE;  return CODE;
         }                                                                       */
    (void)s;
    (void)c;
    *a = A_COPY;
    return CODE;
}

/* ---------- YOU: WAY 2 - the same machine as two tables ---------- */
/* TODO 2: fill both tables (row = state, column = char class).   '/'   '*'   other */
const SState next_table[NUM_STATES][NUM_CLASSES] = {
    /* CODE  */ { CODE, CODE, CODE },
    /* SLASH */ { CODE, CODE, CODE },
    /* BLOCK */ { CODE, CODE, CODE },
    /* STAR  */ { CODE, CODE, CODE } };
const Action act_table[NUM_STATES][NUM_CLASSES] = {
    /* CODE  */ { A_NONE, A_NONE, A_NONE },
    /* SLASH */ { A_NONE, A_NONE, A_NONE },
    /* BLOCK */ { A_NONE, A_NONE, A_NONE },
    /* STAR  */ { A_NONE, A_NONE, A_NONE } };

SState next_by_table(SState s, CharClass c, Action *a) {
    /* TODO 3:  *a = act_table[s][c];  return next_table[s][c];   (no switch, no if) */
    (void)s;
    (void)c;
    *a = A_NONE;
    return CODE;
}

/* ---------- GIVEN ---------- */
CharClass class_of(char c) {
    if (c == '/') return C_SLASH;
    if (c == '*') return C_STAR;
    return C_OTHER;
}

int strip_text(const char *src, char dst[], int use_table, int *comments) {
    SState s = CODE;
    int n = 0;
    *comments = 0;
    for (int i = 0; src[i] != '\0' && n < MAX_TEXT - 2; i++) {
        char ch = src[i];
        Action a;
        if (use_table)
            s = next_by_table(s, class_of(ch), &a);       /* WAY 2 */
        else
            s = next_switch(s, class_of(ch), &a);         /* WAY 1 */
        if (a == A_COPY) {
            dst[n++] = ch;
        } else if (a == A_FLUSH) {
            dst[n++] = '/';
            dst[n++] = ch;
        } else if (a == A_START) {
            (*comments)++;
        } else if (a == A_SPACE) {
            dst[n++] = ' ';
        }
    }
    if (s == SLASH)
        dst[n++] = '/';                   /* the text ended right after a '/' */
    dst[n] = '\0';
    return s == BLOCK || s == STAR;
}
