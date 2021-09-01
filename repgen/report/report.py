import sys,time,datetime,pytz,tempfile,shutil,os,operator
from repgen.data.value import Value

class Report:
	def __init__(self, report, file_name):
		self.repfilename = file_name
		self.repfile = report
		self.replines = []
		self.datadef = ""
		lines = report.splitlines()
		self.data = {}
		deflines = []
		state="none"
		for line in lines:
			if state == "none":
				deflines.append( "" )		# Append blank line to align definition line numbers
				if "#FORM" in line.upper():
					print( "Found Report Section",file=sys.stderr)
					state="INREP"
				elif "#DEF" in line.upper():
					print( "Found Definition Section", file=sys.stderr)
					state="INDEF"
			elif state == "INREP":
				deflines.append( "" )		# Append blank line to align definition line numbers
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

	def run( self,basedate, local_vars: dict = None ):
		# setup the base data
		#
		my_locals = {
			"BASDATE": Value(basedate,picture="%Y%b%d %H%M"),
			"BTM": Value(basedate,picture="%Y%b%d %H%M"),
			"CURDATE": Value(datetime.datetime.now(Value.shared["tz"]),picture="%Y%b%d %H%M"),
			"CTM": Value(datetime.datetime.now(Value.shared["tz"]),picture="%Y%b%d %H%M")
		}

		# If locals were passed in, set them too
		if local_vars:
			for key, value in local_vars.items():
				my_locals[key] = value

		# Compile the report, so source and line number information can be reported to the user
		exec(compile(self.datadef, self.repfilename, "exec"),globals(),my_locals )

		# loop through my_locals and add them
		# to a dictionary with the % in front of the them
		# to mark location on the report
		self.data = { }

		for key in my_locals:
			if isinstance(my_locals[key], Value ):
				self.data["%"+key] = my_locals[key]
