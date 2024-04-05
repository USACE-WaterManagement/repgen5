#!/bin/sh

if [ "$1" = "convert" ]; then
	shift
	exec /converter/convert_report.py "$@"
elif [ "$1" = "batch_convert" ]; then
	shift
	exec /converter/convert.sh "$@"
else
	# Check if -i was supplied, as we don't want to override it
	# If not present, set it to stdin
	found=0
	for arg do
		case $arg in
			-i)	found=1	;;
			-i*)	found=1	;;
			--in)	found=1	;;
			--in=*)	found=1	;;
		esac
	done

	args=""
	[ -n "$CDA_BACKUP" ] && args="$args --alternate $CDA_BACKUP"
	[ -n "$COMPATIBILITY_MODE" ] && [ $COMPATIBILITY_MODE -gt 0 ] && args="$args --compatibility"
	[ -n "$CDA_TIMEOUT" ] && args="$args --timeout $CDA_TIMEOUT"
	[ -n "$OFFICE_ID" ] && args="$args --office $OFFICE_ID"
	[ -n "$RUN_DATE" ] && args="$args --date $DATE"
	[ -n "$RUN_TIME" ] && args="$args --time $TIME"
	[ -n "$DATA_FILE" ] && args="$args --file \"$DATA_FILE\""
	# TZ is already handled directly by repgen

	[ $found -eq 0 ] && args="$args -i-"

	args="--address $CDA_PRIMARY $args"
	[ -n "$VERBOSE" ] && [ $VERBOSE -gt 0 ] && set>&2 &&
		echo /repgen $args "$@">&2
	exec /repgen $args "$@"
fi
