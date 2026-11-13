/*
 * ESE 124 - Exercise 10 - Q2: frfr - an overlapping pattern counter (switch)
 * main.c is GIVEN. You write the machine in frfr.c.
 *
 * For every message (one per line, empty lines skipped) main prints  MSG k: FRFR=<count>
 * then MESSAGES=  TOTAL=  MOST=<the FIRST message with the biggest count, or NONE>
 */
#include <stdio.h>
#include <string.h>
#include "frfr.h"

int main(void) {
    FILE *fp = fopen("messages.txt", "r");
    if (fp == NULL) {
        printf("Cannot open messages.txt\n");
        return 1;
    }
    char line[LINE_LEN];
    int k = 0, total = 0, best = 0, most = 0;
    while (fgets(line, LINE_LEN, fp) != NULL) {
        line[strcspn(line, "\r\n")] = '\0';
        if (line[0] == '\0')
            continue;
        k++;
        int n = count_frfr(line);
        printf("MSG %d: FRFR=%d\n", k, n);
        total += n;
        if (n > best) {                    /* FIRST message wins a tie */
            best = n;
            most = k;
        }
    }
    fclose(fp);
    printf("MESSAGES=%d\n", k);
    printf("TOTAL=%d\n", total);
    if (most == 0)
        printf("MOST=NONE\n");
    else
        printf("MOST=%d\n", most);
    return 0;
}
