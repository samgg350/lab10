# ESE 124 – Exercise 10: State Machines with switch and 2D Arrays

A state machine is always in ONE state. Each input moves it along one arrow to the next state. You will code machines in two ways:

- **switch:** `switch (state)`, then an `if` on the input picks the arrow.
- **2D array:** row = state, column = input. `next_state[state][in]` *is* the diagram.

The full handout is **`Exercise10.pdf`** (the cheat sheet is on its last pages).

## What you edit

**In every folder, `main.c`, the `.h` file and the `Makefile` are given. You only edit ONE `.c` file.**

| Q | Folder | You edit | Way | Points |
|---|---|---|---|---:|
| Q1 | `q1_vending` | `vending.c` | 2D array | 15 |
| Q2 | `q2_frfr` | `frfr.c` | switch | 15 |
| Q3 | `q3_brobank` | `atm.c` (only `atm_step`) | switch | 20 |
| Q4 | `q4_lock` | `lock.c` | 2D array | 20 |
| Q5 | `q5_comments` | `strip.c` | switch AND 2D array | 25 |
| | `reflection.txt` | | | 5 |

Every question works the same way:

1. Look at the diagram and the table in `Exercise10.pdf`.
2. Open the `.c` file and do TODO 1, TODO 2, TODO 3 ... in order.
3. In the question folder type `make run`.
4. Compare with `expected_output.txt` in the same folder.
5. Run the autograder for that question (below) and fix what it says.

All five machines are **Mealy** machines: every arrow is `input/output`. Read the output with the OLD state, then move.

## How to use the Makefile

Open a terminal in a question folder and type:

```
cd q1_vending
make            builds the program   (Windows: mingw32-make)
make run        builds it and runs it
make clean      deletes the program (your files stay)
```

Compare what you see with **`expected_output.txt`** in the same folder.

## Run the autograder

From the main folder:

```
py tests\run_all_tests.py          Windows (or double-click run_tests.bat)
python3 tests/run_all_tests.py     Mac / Linux
py tests\run_all_tests.py q4       only the Q4 tests
```

A FAIL shows the input, the lines it expected (`[ OK ]` / `[FAIL]`), what your program printed, and a HINT. A table test names the wrong cell, e.g. `next_state[S0110][IN1] should be S01`.

**The "way" is checked.** A switch function must use `switch`. A table function must use only the tables (no `switch`, no `if`, no `?:`), and the test changes one table cell to make sure your function really reads it.

## Submit

```
git add q*/*.c reflection.txt
git commit -m "Exercise 10"
git push
```

Then check the green check mark in the **Actions** tab on GitHub.
