# ESE 124 Exercise 10 - top-level Makefile
#   make         build every question (each folder has its own Makefile)
#   make test    run the autograder
#   make clean   clean every folder
# You can also build one question:   cd q1_vending   then   make

all:
	-$(MAKE) -C q1_vending
	-$(MAKE) -C q2_frfr
	-$(MAKE) -C q3_brobank
	-$(MAKE) -C q4_lock
	-$(MAKE) -C q5_comments

test:
	python3 tests/run_all_tests.py

clean:
	-$(MAKE) -C q1_vending clean
	-$(MAKE) -C q2_frfr clean
	-$(MAKE) -C q3_brobank clean
	-$(MAKE) -C q4_lock clean
	-$(MAKE) -C q5_comments clean
	rm -rf tests/.build tests/debug tests/last_report.txt

.PHONY: all test clean
