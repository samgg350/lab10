# Exercise 10 - q2_frfr   (this Makefile is GIVEN - you do not need to change it)
#
#   make         build the program ./frfr  (only if a file changed)
#   make run     build it, then run it
#   make clean   delete the program (your .c, .h and .txt files stay)
#
# A rule is:   target: the files it needs
#              <TAB>the command that makes the target
CC     = gcc
CFLAGS = -Wall -Wextra -std=c11

frfr: main.c frfr.c frfr.h
	$(CC) $(CFLAGS) main.c frfr.c -o frfr

run: frfr
	./frfr

clean:
	rm -f frfr frfr.exe

.PHONY: run clean
