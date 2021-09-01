import sys,time,datetime,pytz,tempfile,shutil,os,operator
from inspect import isfunction
import math
from repgen.data.value import Value
from repgen.report import Report

version = "5.0.1"
# setup base time, ex
# default formats
def parseArgs():
	import optparse
	parser=optparse.OptionParser()
	_d = time.strftime("%d%b%Y", time.localtime() )
	_t = time.strftime("%H%M", time.localtime() )
	parser.add_option( '-i', '--in', dest='in_file', help="INput report file", metavar="REPFILE" )
	parser.add_option( '-o', '--out', dest='out_file', default="-", help="OUTput file with filled report", metavar="REPOUTPUT")
	parser.add_option( '-d', '--date', dest='base_date', default=_d, help="base date for data", metavar="DDMMMYYY" )
	parser.add_option( '-t', '--time', dest='base_time', default=_t, help="base time for data", metavar="HHMM")
	parser.add_option( '-a', '--host', dest='host', default='localhost', help="host for data connections", metavar='IP ADDRESS OR HOSTNAME')
	parser.add_option( '-p', '--port', dest='port', default=80, help="port for data connection", metavar='0-65535')
	parser.add_option( '-z', '--tz', dest='tz', default='UTC', help="default timezone", metavar='Time Zone Name')
	parser.add_option( '-c', '--compatibility', dest='compat', action="store_true", default=False, help="repgen4 compatibility; case-insensitive labels")
	parser.add_option( '-V', '--Version',dest='show_ver',action='store_true',default=False, help="print version number")
	parser.add_option( '-f', '--file', dest='data_file', default=None, help="Variable data file", metavar="DATAFILE" )
	return parser.parse_args()[0]

if __name__ == "__main__":

	config = parseArgs()

	if config.show_ver == True:
		print(version)
		sys.exit(0)

	report_file = config.in_file
	Value(1,host=config.host, port= int(config.port),tz=pytz.timezone(config.tz) )
	
	f = open(report_file) 
	report_data = f.read()
	f.close()
	#os.environ['TZ'] = config.tz
	#time.tzset()
	_t = time.strptime(config.base_date+" " + config.base_time  , "%d%b%Y %H%M" )
	# make sure we have basedate in a reasonable time zone
	print( repr(_t) )
	_t = list(_t[0:6])
	_t.append(0)
	_t.append(pytz.timezone(config.tz))
	print( repr(_t) )
	basedate = datetime.datetime( *_t )
	print( basedate.strftime("%d%b%Y %H%M %Z"), file=sys.stderr)

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
				val = line.strip('"')
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


	report = Report(report_data, report_file, config.compat)
	report.run(basedate, local_vars)
	output = None
	tmpname = None

	# set some of the default values
	if config.out_file == "-":
		output = sys.stdout
	else:
		fd,tmpname = tempfile.mkstemp(text=True)
		output = os.fdopen(fd,"w")

	
	report.fill_report(output)

	if config.out_file != "-":
		output.close()
		shutil.move(tmpname,config.out_file)


	# read the report file


	# exec the definitions

	# build the report
