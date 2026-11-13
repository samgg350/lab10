/*
 * ESE 124 - Exercise 10 - Q2: frfr.c - a SWITCH state machine
 * Name: ____________________   SBU ID: ____________
 *
 * YOU write: frfr_step() and count_frfr().   (main.c, frfr.h, Makefile are given)
 * Draw it first:  S0 --F--> S_F --R--> S_FR --F--> S_FRF --R--> (match!) S_FR
 */
#include <stdio.h>
#include <ctype.h>
#include "frfr.h"

FState frfr_step(FState s, char c, int *found) {
    /* TODO 1:
         char u = (char)toupper((unsigned char)c);     'f' and 'F' are the same
         *found = 0;
         switch (s) {
         case S0:    F -> S_F,                    anything else -> S0
         case S_F:   R -> S_FR,   F -> S_F,       anything else -> S0
         case S_FR:  F -> S_FRF,                  anything else -> S0
         case S_FRF: R -> *found = 1, S_FR  (overlap!)
                     F -> S_F,                    anything else -> S0
         default:    return S0;
         }                                                                       */
    char u = (char)toupper((unsigned char)c);
    *found = 0;
    switch (s) {
    case S0:
        if (u == 'F') return S_F;
        return S0;
    case S_F:
        if (u == 'R') return S_FR;
        if (u == 'F') return S_F;
        return S0;
    case S_FR:
        if (u == 'F') return S_FRF;
        return S0;
    case S_FRF:
        if (u == 'R') {
            *found = 1;
            return S_FR;
        }
        if (u == 'F') return S_F;
        return S0;
    default:
        return S0;
    }
}

int count_frfr(const char *text) {
    /* TODO 2: if text is NULL return 0.
               s = S0;  for every char:  s = frfr_step(s, text[i], &found);  count += found;
               return count;                                                     */
    if (text == NULL) return 0;
    FState s = S0;
    int count = 0;
    int found = 0;
    for (int i = 0; text[i] != '\0'; i++) {
        s = frfr_step(s, text[i], &found);
        count += found;
    }
    return count;
}
