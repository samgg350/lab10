/*
 * ESE 124 - Exercise 10 - Q4: The CAD Lab Door Lock (Mealy machine, 2D arrays)
 * main.c is GIVEN. You write the two tables, column_of() and lock_step() in lock.c.
 *
 * keypad.txt: one log per line (empty lines skipped). Every log starts in SX.
 * For log k main prints
 *     TRACE k: SX <state after key 1> <state after key 2> ...
 *     LOG k: OUT=<the output of every key> OPENS=<number of 1s>
 * then LOGS= and TOTAL_OPENS=
 */
#include <stdio.h>
#include <string.h>
#include "lock.h"

int main(void) {
    FILE *fp = fopen("keypad.txt", "r");
    if (fp == NULL) {
        printf("Cannot open keypad.txt\n");
        return 1;
    }
    char line[LINE_LEN], u[MAX_KEYS + 1];
    LState trace[MAX_KEYS + 1];
    int k = 0, total = 0;
    while (fgets(line, LINE_LEN, fp) != NULL) {
        line[strcspn(line, "\r\n")] = '\0';
        if (line[0] == '\0')
            continue;
        if ((int)strlen(line) > MAX_KEYS)
            line[MAX_KEYS] = '\0';             /* keep at most MAX_KEYS keys */
        k++;
        int n = run_log(line, trace, u);
        printf("TRACE %d:", k);
        for (int i = 0; i <= (int)strlen(line); i++)
            printf(" %s", state_name(trace[i]));
        printf("\n");
        printf("LOG %d: OUT=%s OPENS=%d\n", k, u, n);
        total += n;
    }
    fclose(fp);
    printf("LOGS=%d\n", k);
    printf("TOTAL_OPENS=%d\n", total);
    return 0;
}
