#!/bin/sh
# ESE 124 Exercise 10 - Mac/Linux:  sh run_tests.sh      or   sh run_tests.sh q2
cd "$(dirname "$0")" && python3 tests/run_all_tests.py "$@"
