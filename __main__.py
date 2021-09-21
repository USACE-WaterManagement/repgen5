import sys,time,datetime,pytz,tempfile,shutil,os,re
from repgen.data.value import Value
from repgen.report import Report

version = "5.0.1"

# setup base time, ex
# default formats
def parseArgs():
	import optparse
	parser=optparse.OptionParser()
	_z = os.environ.get("TZ", None)		# Get TZ from environment, if specified
	_d = time.strftime("%d%b%Y", time.localtime())
	_t = time.strftime("%H%M", time.localtime())
	parser.add_option( '-i', '--in', dest='in_file', help="INput report file", metavar="REPFILE" )
	parser.add_option( '-o', '--out', dest='out_file', default="-", help="OUTput file with filled report", metavar="REPOUTPUT")
	parser.add_option( '-d', '--date', dest='base_date', default=_d, help="base date for data", metavar="DDMMMYYY" )
	parser.add_option( '-t', '--time', dest='base_time', default=_t, help="base time for data", metavar="HHMM")
	parser.add_option( '-a', '--address', dest='host', default='localhost', help="location for data connections", metavar='IP Address:port, hostname:port, or query URL base (for JSON)')
	parser.add_option( '-z', '--tz', dest='tz', default=_z, help="default timezone", metavar='Time Zone Name')
	parser.add_option( '-c', '--compatibility', dest='compat', action="store_true", default=False, help="repgen4 compatibility; case-insensitive labels")
	parser.add_option( '-V', '--version',dest='show_ver',action='store_true',default=False, help="print version number")
	parser.add_option( '-f', '--file', dest='data_file', default=None, help="Variable data file", metavar="DATAFILE" )
	return parser.parse_args()[0]

# Pytz does't know all the aliases and abbreviations
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

if __name__ == "__main__":

	config = parseArgs()

	if config.show_ver == True:
		print(version)
		sys.exit(0)

	report_file = config.in_file
	host = config.host
	query = None

	# Check for protocol (e.g. https://)
	# We don't actually care about it, so discard it (repgen only works with http or https)
	match = re.match(r"(https?:\/\/)?(.+)", host)
	host = match.group(2)
	if '/' in host:
		(host, query) = host.split('/', 1)

	tz = None

	# Reload the timezone information based on passed in value
	if hasattr(time, 'tzset') and config.tz:
		# Windows doesn't support reloading timezone information
		os.environ['TZ'] = config.tz
		time.tzset()
	elif config.tz:
		tz = pytz.timezone(config.tz)

	if not tz:
		# Default to the system timezone
		# Convert system timezone name to pytz compatible name
		# This might fail if TIMEZONE_ALIASES is missing an entry, in which case, using the --tz argument will skip this
		tz = str(datetime.datetime.now().astimezone().tzinfo)
		tz = pytz.timezone(TIMEZONE_ALIASES.get(tz, tz))

	# set some of the default values
	Value(1, host=host, query=query, tz=tz, ucformat=config.compat)
	
	# read the report file
	f = open(report_file)
	report_data = f.read()
	f.close()

	base_date = config.base_date
	base_time = config.base_time

	if base_time == "2400": base_time = "0000"
	_t = datetime.datetime.strptime(base_date + " " + base_time , "%d%b%Y %H%M" )
	if config.base_time == "2400":
		_t = _t + datetime.timedelta(days=1)

	print( repr(_t) )

	basedate = _t

	local_vars = {}
	# Read data file input
	if config.data_file:
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

	if config.out_file == "-":
		output = sys.stdout
	else:
		fd,tmpname = tempfile.mkstemp(text=True)
		output = os.fdopen(fd,"wt")
	
	# build the report
	report.fill_report(output)

	if config.out_file != "-":
		output.close()
		shutil.move(tmpname,config.out_file)
		mask = os.umask(0)
		os.chmod(config.out_file, 0o777 & (~mask))
		os.umask(mask)
