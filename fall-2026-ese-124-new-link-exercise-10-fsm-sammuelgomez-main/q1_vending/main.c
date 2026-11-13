/*
 * ESE 124 - Exercise 10 - Q1: BroBot's 15-cent Vending Machine (2D arrays)
 * main.c is GIVEN. You write the machine in vending.c.
 *
 * Reads coins.txt one char at a time. N D Q C are inputs; every other char
 * (space, new line, x ...) is ignored. For every input main prints
 *     STEP k: <old state> --<input>/<action>--> <new state>
 * and at the end VENDS= CHANGE_CENTS= REFUND_CENTS= FINAL=
 */
#include <stdio.h>
#include "vending.h"

int main(void) {
    FILE *fp = fopen("coins.txt", "r");
    if (fp == NULL) {
        printf("Cannot open coins.txt\n");
        return 1;
    }
    VState s = S0;
    int c, step = 0, vends = 0, change = 0, refund = 0;
    while ((c = fgetc(fp)) != EOF) {
        int col = column_of((char)c);
        if (col < 0)
            continue;                          /* not an input: ignore it */
        step++;
        VState old = s;                        /* remember the OLD state  */
        Action a = vend_step(&s, col);         /* one step of the machine */
        printf("STEP %d: %s --%c/%s--> %s\n", step, state_name(old), c, action_name(a), state_name(s));
        if (a == VEND || a == VEND_CHANGE)
            vends++;
        if (a == VEND_CHANGE)
            change += CHANGE_CENTS;
        if (a == REFUND)
            refund += CENTS[old];              /* give back what the OLD state held */
    }
    fclose(fp);
    printf("VENDS=%d\n", vends);
    printf("CHANGE_CENTS=%d\n", change);
    printf("REFUND_CENTS=%d\n", refund);
    printf("FINAL=%s\n", state_name(s));
    return 0;
}
