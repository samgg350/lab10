#ifndef ATM_H
#define ATM_H

#define MAX_ACC  10
#define NAME_LEN 16
#define LINE_LEN 60
#define MSG_LEN  40

/* The ATM is always in ONE of these states: */
typedef enum { IDLE, WAIT_PIN, READY, NUM_STATES } AtmState;

typedef struct {
    char name[NAME_LEN];
    int pin;
    double balance;
} Account;

/* What the machine remembers: its state and whose card is inside. */
typedef struct {
    AtmState state;
    int acct;                  /* index of the account whose card is inside (-1 = none) */
} Atm;

/* GIVEN in atm.c */
int load_accounts(const char *file, Account acc[], int max);   /* n, -1 no file, 0 bad file */
int find_account(const Account acc[], int n, const char *name); /* index or -1             */
const char *atm_state_name(AtmState s);                         /* IDLE -> "IDLE" ...      */

/* YOU write this one. Handle ONE line of session.txt: change m->state (and the balance)
   and copy the message into msg.
     state     line         condition        -> next state   message
     IDLE      CARD name    name is known    -> WAIT_PIN     "INSERT PIN"
                            unknown name     -> IDLE         "NO SUCH ACCOUNT"
     WAIT_PIN  PIN p        p is correct     -> READY        "PIN OK"
                            p is wrong       -> WAIT_PIN     "WRONG PIN"
     WAIT_PIN  EJECT                         -> IDLE         "CARD RETURNED"
     READY     BALANCE                       -> READY        "BALANCE 500.00"
     READY     WITHDRAW a   a <= 0           -> READY        "INVALID AMOUNT"
                            a > balance      -> READY        "INSUFFICIENT FUNDS"
                            otherwise        -> READY        "CASH 120.00"   (balance - a)
     READY     EJECT                         -> IDLE         "CARD RETURNED"
   ANY other line (wrong state, unknown word, missing number) -> same state, "REJECTED" */
void atm_step(Atm *m, Account acc[], int n, const char *line, char msg[]);

#endif
