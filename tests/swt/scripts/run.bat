@echo off

c:\Python38\python.exe . ^
    -a https://cwms-data.usace.army.mil/cwms-data ^
    -i tests/swt/testfiles/test.frm ^
    -O SWT ^
	-p ^
	-o tests/swt/output/test.txt ^
    %*