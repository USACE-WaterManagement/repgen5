@echo off

python3 . ^
    -a https://cwms-data.usace.army.mil/cwms-data ^
    -i tests/swt/testfiles/test.frm ^
    -O SWT ^
	-p ^
    %*