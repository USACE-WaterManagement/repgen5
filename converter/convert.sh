#!/bin/sh
# This accepts two arguments, input directory (repgen4), and an output directory (repgen5).
# It will try to convert every report file found in the input directory, and place it in the output.
# Example: ./convert.sh /wm/spkshare/production/config/reports/daily /wm/spkshare/production/config/reports/daily.5

INPUT=$(readlink -f $1)
OUTPUT=$(readlink -m $2)
SCRIPT=$(readlink -f $0)
SCRIPT="`dirname $SCRIPT`/convert_report.py"

cd $INPUT

if [ ! -d $OUTPUT ]; then mkdir -p $OUTPUT; fi

# Report files are assumed to be in this format, starting with the letter 'i'
# i<zero or one letter, such as 'a', 'c'>-<report name>
# For example: i-blblvl ia-frm
for f in ${FILE_MASK:="i*-*"}; do
	# This is a custom exception, meaning skip files that match this pattern
	if [ "${f#*"20d5d"}" != "$f" ]; then
	       continue
	fi	       
	IN="$INPUT/$f"
	OUT="$OUTPUT/$f"

	# Run converter on report file
	echo $SCRIPT $IN $OUT
	$SCRIPT $IN $OUT
done

