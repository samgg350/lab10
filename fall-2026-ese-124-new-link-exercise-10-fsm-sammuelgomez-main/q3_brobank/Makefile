# Exercise 10 - q3_brobank   (this Makefile is GIVEN - you do not need to change it)
#
#   make         build the program ./atm  (only if a file changed)
#   make run     build it, then run it
#   make clean   delete the program (your .c, .h and .txt files stay)
#
# A rule is:   target: the files it needs
#              <TAB>the command that makes the target
CC     = gcc
CFLAGS = -Wall -Wextra -std=c11

atm: main.c atm.c atm.h
	$(CC) $(CFLAGS) main.c atm.c -o atm

run: atm
	./atm

clean:
	rm -f atm atm.exe

.PHONY: run clean
