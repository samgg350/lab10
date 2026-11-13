/*
 * ESE 124 - Exercise 10 - Q3: atm.c - the BroBank ATM as a SWITCH state machine
 * Name: Sammuel Gomez          SBU ID: ____________
 *
 * YOU write: atm_step() at the bottom. The rules table is in atm.h and in the handout.
 */
#include <stdio.h>
#include <string.h>
#include "atm.h"

/* ---------- GIVEN ---------- */
int load_accounts(const char *file, Account acc[], int max) {
    FILE *fp = fopen(file, "r");
    if (fp == NULL)
        return -1;
    int n;
    if (fscanf(fp, "%d", &n) != 1 || n < 1 || n > max) {
        fclose(fp);
        return 0;
    }
    for (int i = 0; i < n; i++) {
        if (fscanf(fp, "%15s %d %lf", acc[i].name, &acc[i].pin, &acc[i].balance) != 3) {
            fclose(fp);
            return 0;
        }
    }
    fclose(fp);
    return n;
}

int find_account(const Account acc[], int n, const char *name) {
    for (int i = 0; i < n; i++)
        if (strcmp(acc[i].name, name) == 0)
            return i;
    return -1;
}

const char *atm_state_name(AtmState s) {
    static const char *NAME[NUM_STATES] = { "IDLE", "WAIT_PIN", "READY" };
    return NAME[s];
}

/* ---------- YOU: the state machine ---------- */
void atm_step(Atm *m, Account acc[], int n, const char *line, char msg[]) {
    char cmd[NAME_LEN], arg[NAME_LEN];
    int got = sscanf(line, "%15s %15s", cmd, arg);    /* got = how many words were read */

    strcpy(msg, "REJECTED");                          /* the default answer (keep this) */

    /* TODO: switch (m->state) {
             case IDLE:     CARD name    (got == 2, strcmp(cmd, "CARD") == 0)
                              k = find_account(acc, n, arg);
                              k < 0 -> "NO SUCH ACCOUNT"
                              else  -> m->acct = k;  m->state = WAIT_PIN;  "INSERT PIN"
                            break;
             case WAIT_PIN: PIN p        (sscanf(arg, "%d", &pin) == 1)
                              p == acc[m->acct].pin -> READY "PIN OK", else "WRONG PIN"
                            EJECT        (got == 1)  -> IDLE, m->acct = -1, "CARD RETURNED"
                            break;
             case READY:    BALANCE      -> sprintf(msg, "BALANCE %.2f", ...)
                            WITHDRAW a   (sscanf(arg, "%lf", &amt) == 1)
                              a <= 0 "INVALID AMOUNT", a > balance "INSUFFICIENT FUNDS",
                              else balance -= a and sprintf(msg, "CASH %.2f", a)
                            EJECT        -> IDLE, m->acct = -1, "CARD RETURNED"
                            break;
             default:       break;
             }
       Use strcpy(msg, "...") to set the message.                                 */
    int k;
    int pin;
    double amt;

    switch (m->state) {
    case IDLE:
        if (got == 2 && strcmp(cmd, "CARD") == 0) {
            k = find_account(acc, n, arg);
            if (k < 0) {
                strcpy(msg, "NO SUCH ACCOUNT");
            } else {
                m->acct = k;
                m->state = WAIT_PIN;
                strcpy(msg, "INSERT PIN");
            }
        }
        break;
    case WAIT_PIN:
        if (got == 2 && strcmp(cmd, "PIN") == 0 && sscanf(arg, "%d", &pin) == 1) {
            if (pin == acc[m->acct].pin) {
                m->state = READY;
                strcpy(msg, "PIN OK");
            } else {
                strcpy(msg, "WRONG PIN");
            }
        } else if (got == 1 && strcmp(cmd, "EJECT") == 0) {
            m->state = IDLE;
            m->acct = -1;
            strcpy(msg, "CARD RETURNED");
        }
        break;
    case READY:
        if (got == 1 && strcmp(cmd, "BALANCE") == 0) {
            sprintf(msg, "BALANCE %.2f", acc[m->acct].balance);
        } else if (got == 2 && strcmp(cmd, "WITHDRAW") == 0 && sscanf(arg, "%lf", &amt) == 1) {
            if (amt <= 0) {
                strcpy(msg, "INVALID AMOUNT");
            } else if (amt > acc[m->acct].balance) {
                strcpy(msg, "INSUFFICIENT FUNDS");
            } else {
                acc[m->acct].balance -= amt;
                sprintf(msg, "CASH %.2f", amt);
            }
        } else if (got == 1 && strcmp(cmd, "EJECT") == 0) {
            m->state = IDLE;
            m->acct = -1;
            strcpy(msg, "CARD RETURNED");
        }
        break;
    default:
        break;
    }
}
