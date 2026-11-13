/*
 * ESE 124 - Exercise 10 - Q3: BroBank W10 - The ATM State Machine (switch)
 * main.c is GIVEN. You write atm_step() in atm.c.
 *
 * For every non-empty line of session.txt main prints
 *     EVENT k: <the line> | <state before> -> <state after> | <message>
 * then FINAL=  REJECTED=  and one "ACCOUNT name balance" line per account.
 */
#include <stdio.h>
#include <string.h>
#include "atm.h"

int main(void) {
    Account acc[MAX_ACC];
    int n = load_accounts("accounts.txt", acc, MAX_ACC);
    if (n < 0) {
        printf("Cannot open accounts.txt\n");
        return 1;
    }
    if (n == 0) {
        printf("Invalid accounts file\n");
        return 1;
    }
    FILE *fp = fopen("session.txt", "r");
    if (fp == NULL) {
        printf("Cannot open session.txt\n");
        return 1;
    }
    Atm m = { IDLE, -1 };
    char line[LINE_LEN], msg[MSG_LEN], first[NAME_LEN];
    int k = 0, rejected = 0;
    while (fgets(line, LINE_LEN, fp) != NULL) {
        line[strcspn(line, "\r\n")] = '\0';
        if (sscanf(line, "%15s", first) != 1)
            continue;                                  /* empty line */
        k++;
        AtmState before = m.state;
        atm_step(&m, acc, n, line, msg);               /* one step of the machine */
        printf("EVENT %d: %s | %s -> %s | %s\n", k, line, atm_state_name(before),
               atm_state_name(m.state), msg);
        if (strcmp(msg, "REJECTED") == 0)
            rejected++;
    }
    fclose(fp);
    printf("FINAL=%s\n", atm_state_name(m.state));
    printf("REJECTED=%d\n", rejected);
    for (int i = 0; i < n; i++)
        printf("ACCOUNT %s %.2f\n", acc[i].name, acc[i].balance);
    return 0;
}
