# Exercise 10 - q4_lock   (this Makefile is GIVEN - you do not need to change it)
#
#   make         build the program ./lock  (only if a file changed)
#   make run     build it, then run it
#   make clean   delete the program (your .c, .h and .txt files stay)
#
# A rule is:   target: the files it needs
#              <TAB>the command that makes the target
CC     = gcc
CFLAGS = -Wall -Wextra -std=c11

lock: main.c lock.c lock.h
	$(CC) $(CFLAGS) main.c lock.c -o lock

run: lock
	./lock

clean:
	rm -f lock lock.exe

.PHONY: run clean
