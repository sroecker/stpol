

test:
	util/test_step1.sh
	util/test_step1B.sh
	util/test_step2.sh

clean:
	rm -Rf testing_step*
	rm *.log
