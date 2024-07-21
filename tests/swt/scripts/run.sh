#!/bin/bash

python3 . \
    -a https://cwms-data.usace.army.mil/cwms-data \
    -i tests/swt/testfiles/test.frm \
    -O SWT \
	-o tests/swt/output/test.txt \
    $@