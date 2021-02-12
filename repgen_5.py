#!/bin/env python3
import sys,time,datetime,pytz,tempfile,shutil,os,operator
from inspect import isfunction
import math
from repgen.data.value import Value



def TZ(tz):
	return pytz.timezone(tz)

class Report:
	def __init__(self,report ):
		self.repfile = report
		self.replines = []
		self.datadef = ""
		lines = report.splitlines()
		self.data = {}
		deflines = []
		state="none"
		for line in lines:
			if state == "none":
				if "#FORM" in line.upper():
					
					print( "Found Report Section",file=sys.stderr)
					state="INREP"
				elif "#DEF" in line.upper():
					print( "Found Definition Section", file=sys.stderr)
					state="INDEF"
			elif state == "INREP":
				if "#ENDFORM" in line.upper():
					print( "End of Report", file=sys.stderr)
					state = "none"
					continue
				self.replines.append( line )
			elif state == "INDEF":
				if "#ENDDEF" in line.upper():
					print("End of Report", file=sys.stderr)
					state = "none"
					continue
				deflines.append( line )

		self.datadef = "\n".join(deflines)
	

	def fill_report(self, output ):
		values = sorted(self.data.keys())
		#values.sort()
		values.reverse() # need to be able to match the longest first
		
		for line in self.replines:
			tmp = line
			for v in values:
				if v in tmp:
					#print >>sys.stderr, "Found a marker for %s" % v
					start = tmp.find(v)
					newval = self.data[v].pop()
					#print >>sys.stderr, "Using %s" % newval
					if newval is None:
						newval = self.data[v].misstr
					
					end = len(newval)
					
					if end < len(v):
						end = len(v) # make sure the replacement eats the whole variable
					if start+end > len(tmp):
						# we need to extend the line
						tmp = tmp + " "*end
					#print start
					tmp2 = list(tmp)
					for i in range(0,end):
						if i < len(newval):tmp2[start+i] = newval[i]
						else: tmp2[start+i] = " "
					#tmp2[start:start+end] = newval
					tmp = "".join(tmp2)
			output.write( tmp +"\n" )
			
	def run( self,basedate ):
		# setup the base data
		#
		
		
		my_locals = {
			"BASDATE": Value(basedate,picture="%Y%b%d %H%M"),
			"BTM": Value(basedate,picture="%Y%b%d %H%M"),
			"CURDATE": Value(datetime.datetime.now(Value.shared["tz"]),picture="%Y%b%d %H%M"),
			"CTM": Value(datetime.datetime.now(Value.shared["tz"]),picture="%Y%b%d %H%M")
		}
		exec(self.datadef,globals(),my_locals )

		# loop through my_locals and add them
		# to a dictionary with the % in front of the them
		# to mark location on the report
		self.data = { }

		for key in my_locals:
			if isinstance(my_locals[key], Value ):
				self.data["%"+key] = my_locals[key]


		
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
	return parser.parse_args()[0]

if __name__ == "__main__":

	config = parseArgs()

	report_file = config.in_file
	Value(1,host=config.host, port= int(config.port),tz=pytz.timezone(config.tz) )
	
	f = open(report_file) 
	data = f.read()
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
	
	report = Report(data)
	report.run(basedate)
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
		shutil.move(tmpname,config.out_file)
		output.close()


	# read the report file


	# exec the definitions

	# build the report
