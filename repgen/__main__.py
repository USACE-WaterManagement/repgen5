import sys,time,datetime,pytz,tempfile,shutil,os
from repgen.data.value import Value
from repgen.report import Report
from repgen.util import filterAddress

version = "5.1.6"

# setup base time, ex
# default formats
def parseArgs():
	import argparse
	parser=argparse.ArgumentParser()
	_z = os.environ.get("TZ", None)		# Get TZ from environment, if specified
	dt = datetime.datetime.now().astimezone()
	_d = dt.strftime("%d%b%Y")
	_t = dt.strftime("%H%M")
	parser.add_argument( '-V', '--version',dest='show_ver',action='store_true',default=False, help="print version number")
	parser.add_argument( '-i', '--in', dest='in_file', help="INput report file", metavar="REPFILE" )
	parser.add_argument( '-o', '--out', dest='out_file', default="-", help="OUTput file with filled report", metavar="REPOUTPUT")
	parser.add_argument( '-f', '--file', dest='data_file', default=None, help="Variable data file", metavar="DATAFILE" )
	parser.add_argument( '-d', '--date', dest='base_date', default=_d, help="base date for data", metavar="DDMMMYYYY" )
	parser.add_argument( '-t', '--time', dest='base_time', default=_t, help="base time for data", metavar="HHMM")
	parser.add_argument( '-z', '--tz', dest='tz', default=_z, help="default timezone; equivalent to `TZ=timezone`", metavar='Time Zone Name')
	parser.add_argument( '-O', '--office', dest='office', default=None, help="default office to use if not specified in report; equivalent to `DBOFC=OFFICE_ID`", metavar='OFFICE_ID')
	parser.add_argument( '-a', '--address', dest='host', default='localhost', help="location for data connections; equivalent to `DB=hostname:port/path`", metavar='IP_or_hostname:port[/basepath]')
	parser.add_argument( '-A', '--alternate', dest='alternate', default=None, help="alternate location for data connections, if the primary is unavailable (only for RADAR)", metavar='IP_or_hostname:port[/basepath]')
	parser.add_argument( '-c', '--compatibility', dest='compat', action="store_true", default=False, help="repgen4 compatibility; case-insensitive labels")
	parser.add_argument( '--timeout', dest='timeout', type=float, default=None, help="Socket timeout, in seconds" )
	# This provides repgen4 style KEY=VALUE argument passing on the command-line
	parser.add_argument( 'set', default=[], help="Additional key=value pairs. e.g. `DBTZ=UTC DBOFC=HEC`", metavar="KEY=VALUE", nargs="*" )

	if len(sys.argv) == 1:
		parser.print_help()
		exit(2)

	return parser.parse_known_args()[0]

# https://stackoverflow.com/a/52014520
def parse_var(s):
    """
    Parse a key, value pair, separated by '='
    That's the reverse of ShellArgs.

    On the command line (argparse) a declaration will typically look like:
        foo=hello
    or
        foo="hello world"
    """
    items = s.split('=')
    key = items[0].strip() # we remove blanks around keys, as is logical
    if len(items) > 1:
        # rejoin the rest:
        value = '='.join(items[1:])
    return (key, value)

def parse_vars(items):
    """
        Parse a series of key-value pairs and return a dictionary and 
        a success boolean for whether each item was successfully parsed.
    """
    count = 0
    d = {}
    for item in items:
        if "=" in item:
            split_string = item.split("=")
            d[split_string[0].strip().upper()] = split_string[1].strip()
            count += 1
        else:
            print(f"Error: Invalid argument provided - {item}")
        
    return d, count == len(items)

# Pytz doesn't know all the aliases and abbreviations
# This works for Pacific, but untested in other locations that don't use DST.
TIMEZONE_ALIASES = {
	"Pacific Standard Time": "PST8PDT",
	"Pacific Daylight Time": "PST8PDT",
	"Mountain Standard Time": "MST7MDT",
	"Mountain Daylight Time": "MST7MDT",
	"Central Standard Time": "CST6CDT",
	"Central Daylight Time": "CST6CDT",
	"Eastern Standard Time": "EST5EDT",
	"Eastern Daylight Time": "EST5EDT",

	"PST": "PST8PDT",
	"PDT": "PST8PDT",
	"MST": "MST7MDT",
	"MDT": "MST7MDT",
	"CST": "CST6CDT",
	"CDT": "CST6CDT",
	"EDT": "EST5EDT",
	"EST": "EST5EDT",
}

def main():
	config = parseArgs()
	kwargs = parse_vars(config.set)[0]

	if config.show_ver == True:
		print(version)
		sys.exit(0)

	report_file = kwargs.get("IN", config.in_file)
	out_file = kwargs.get("REPORT", config.out_file)
	kwargs.pop("IN", None)		# This doesn't need to be visible to the report definition
	kwargs.pop("REPORT", None)
	kwargs.pop("FILE", None)

	(host, path) = filterAddress(config.host)
	(althost, altpath) = filterAddress(config.alternate)

	tz = None

	if config.tz:
		tz = pytz.timezone(config.tz)

	if not tz:
		# Default to the system timezone
		# Convert system timezone name to pytz compatible name
		# This might fail if TIMEZONE_ALIASES is missing an entry, in which case, using the --tz argument will skip this
		tz = str(datetime.datetime.now().astimezone().tzinfo)
		tz = pytz.timezone(TIMEZONE_ALIASES.get(tz, tz))

	# set some of the default values
	Value(1, host=host, path=path, tz=tz, ucformat=config.compat, timeout=config.timeout, althost=althost, altpath=altpath, dbofc=config.office, **kwargs)
	
	# read the report file
	if report_file == '-': 
		report_file = sys.stdin.name
		f = sys.stdin
	else:
		f = open(report_file, 'rt')
	report_data = f.read()
	f.close()

	base_date = kwargs.get("DATE", config.base_date)
	base_time = kwargs.get("TIME", config.base_time)
	delta = datetime.timedelta()

	if base_time == "2400": 
		base_time = "0000"
		delta = datetime.timedelta(days=1)

	_t = datetime.datetime.strptime(base_date + " " + base_time , "%d%b%Y %H%M" ) + delta

	print( repr(_t), file=sys.stderr )

	basedate = _t

	local_vars = {}
	# Read data file input
	data_file = kwargs.get("FILE", config.data_file)
	if data_file:
		f_d = open(config.data_file)
		key = None
		prefix = ""

		# This processes data file inputs, and converts ^a variables to _a.
		# Format of this file is:
		# ^
		# a
		# Some Value
		# b
		# Another value
		for line in f_d.readlines():
			line = line.strip()
			if line == "^":
				prefix = "_"
			elif not key:
				key = prefix + line
			else:
				# Check to see if the read in value is really a number, and convert it if so
				val = line.strip('"') if '=' not in line else line
				try:
					if '.' in val:
						val = float(val)
					else:
						val = int(val)
				except (TypeError, ValueError):
					pass
				local_vars[key] = val
				key = None

		f_d.close()

	# exec the definitions
	report = Report(report_data, report_file, config.compat)
	report.run(basedate, local_vars)
	output = None
	tmpname = None

	if out_file == "-":
		output = sys.stdout
	else:
		fd,tmpname = tempfile.mkstemp(text=True, prefix="repgen-")
		output = os.fdopen(fd,"wt")
	
	# build the report
	report.fill_report(output)

	if out_file != "-":
		output.close()
		shutil.move(tmpname,out_file)
		mask = os.umask(0)
		os.chmod(out_file, 0o666 & (~mask))
		os.umask(mask)

if __name__ == "__main__":
	main()