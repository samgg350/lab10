# Exercise 10 - q5_comments   (this Makefile is GIVEN - you do not need to change it)
#
#   make         build the program ./nocomment  (only if a file changed)
#   make run     build it, then run it
#   make clean   delete the program (your .c, .h and .txt files stay)
#
# A rule is:   target: the files it needs
#              <TAB>the command that makes the target
CC     = gcc
CFLAGS = -Wall -Wextra -std=c11

nocomment: main.c strip.c strip.h
	$(CC) $(CFLAGS) main.c strip.c -o nocomment

run: nocomment
	./nocomment

clean:
	rm -f nocomment nocomment.exe

.PHONY: run clean
