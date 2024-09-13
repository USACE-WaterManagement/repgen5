#!/bin/bash

reportname="$1"
echo "$reportname"

if [ -z "$1" ]; then
    echo "No input provided. Listing files in the 'tests/swt/testfiles' directory:"
    for f in tests/swt/testfiles/*.*; do
        filename=$(basename "$f")
        echo "./run.sh ${filename%.*}"
    done
    exit 1
fi

case "$reportname" in
    *.frm) reportname="${reportname%.frm}" ;;
    *.out) reportname="${reportname%.out}" ;;
esac

python3 . \
    -a https://cwms-data.usace.army.mil/cwms-data \
    -i tests/swt/testfiles/"$reportname".frm \
    -O SWT \
    -o tests/swt/output/"$reportname".out \
    "$@"
