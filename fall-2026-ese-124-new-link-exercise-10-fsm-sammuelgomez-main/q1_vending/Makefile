# Exercise 10 - q1_vending   (this Makefile is GIVEN - you do not need to change it)
#
#   make         build the program ./vending  (only if a file changed)
#   make run     build it, then run it
#   make clean   delete the program (your .c, .h and .txt files stay)
#
# A rule is:   target: the files it needs
#              <TAB>the command that makes the target
CC     = gcc
CFLAGS = -Wall -Wextra -std=c11

vending: main.c vending.c vending.h
	$(CC) $(CFLAGS) main.c vending.c -o vending

run: vending
	./vending

clean:
	rm -f vending vending.exe

.PHONY: run clean
