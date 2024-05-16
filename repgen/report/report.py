import sys,time,datetime,pytz,tempfile,shutil,os,operator,calendar,re
from repgen.data.value import Value
try:
	# Relativedelta supports months and years, but is external library
	from dateutil.relativedelta import relativedelta as timedelta
except:
	# Included with python, but doesn't support longer granularity than days.
	from datetime import timedelta

class Report:
	def __init__(self, report, file_name, compatibility):
		self.repfilename = file_name
		self.repformfile = ""
		self.repfile = report
		self.replines = []
		self.datadef = ""
		self.compatibility = compatibility
		self.data = {}
		
		self._validate_report(report)
		
		lines = map(lambda s: s.strip('\r'),  report.split(sep='\n'))
		deflines = []
		state="none"
		for line in lines:
			deflines.append( "" )		# Append blank line to align definition line numbers
			if state == "none":
				# Check the longer hash commands first
				if "#FORMFILE" in line.upper():
					print( "Found Report File",file=sys.stderr)
					state = "none"
					self.repformfile = line.split("#FORMFILE ")[1].strip()
					if not os.path.isfile(self.repformfile):
						if self.repformfile.startswith("."):
							print("\n\tConsider using an absolute path for #FORMFILE full/path/to/your/template", file=sys.stderr)
						raise FileNotFoundError(f"Could not find #FORMFILE {self.repformfile}! Exiting...")
					with open(self.repformfile) as f:
						self.repfile = f.read()
					print(f"Read in file {self.repformfile}", file=sys.stderr)
					self.replines = self.repfile.split("\n")
				elif "#FORM" in line.upper():
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
				deflines[-1] = line		# replace existing blank line

		self.datadef = "\n".join(deflines)
	

	def fill_report(self, output):
		values = sorted(self.data.keys())
		#values.sort()
		values.reverse() # need to be able to match the longest first

		# Map the variable names in the data, so we can find it even when we have uppercased name
		if self.compatibility:
			data_keys = {k.upper(): k for k in self.data.keys()}
		else:
			data_keys = {k: k for k in self.data.keys()}


		for line in self.replines:
			tmp = line
			for v in values:
				# if compat mode on, uppercase everything
				if self.compatibility:
					v = v.upper()
					tmpupper = tmp.upper()
				else:
					tmpupper = tmp
				# Loop to catch multiple instances of a variable usage
				while v in tmpupper:
					#sys.stderr.write("Found a marker for %s (%d)\n" % (v, len(v)))
					if self.compatibility:
						start = tmp.upper().find(v.upper())
					else:
						start = tmp.find(v)

					newval = self.data[data_keys[v]].pop()
					#sys.stderr.write("Using %s\n" % newval)
					if newval is None:
						newval = self.data[data_keys[v]].misstr

					end = len(newval)
					#sys.stderr.write("Newval: %s (%d)\n" % (newval, len(newval)))
					#sys.stderr.write("line: %s\n" % tmp)
					#sys.stderr.write("Before: Start: %d; End: %d; Len: %d\n" % (start, end, len(v)))
					if end < len(v):
						end = len(v) # make sure the replacement eats the whole variable
					#sys.stderr.write("After: Start: %d; End: %d; Len: %d\n" % (start, end, len(v)))
					if start+end > len(tmp):
						# we need to extend the line
						tmp = tmp + " "*end
					tmp2 = list(tmp)
					#sys.stderr.write(repr(tmp2) + "\n")
					for i in range(0,end):
						if i < len(newval):tmp2[start+i] = newval[i]
						else: tmp2[start+i] = " "
					#tmp2[start:start+end] = newval
					tmp = "".join(tmp2)

					if self.compatibility:
						tmpupper = tmp.upper()
					else:
						tmpupper = tmp
			output.write( tmp + "\n" )
			
	def _validate_report(self, report: str) -> None:
		"""Validate the structure of a report.

		Args:
			report (str): The report .frm content to validate.

		Raises:
			ValueError: If the report contains both a '#FORM/#ENDFORM' and a '#FORMFILE' tag.
			ValueError: If the report does not contain a '#FORM'/'#ENDFORM' or '#FORMFILE' tag.
		"""
		# TODO: What else should we be validating in a report?
		# Pick one or the other, not both
		if ("#FORM\n" in report or "#ENDFORM\n" in report) and "#FORMFILE" in report:
			raise ValueError("\n\tReport contains both a #FORM/#ENDFORM and a #FORMFILE tag. You must choose ONE.\n")
		# Have at least one or the other
		if ("#FORM" not in report or "#ENDFORM" not in report) and "#FORMFILE" not in report:
			raise ValueError("\n\tReport does not contain a #FORM or #FORMFILE tag.\n")
		
	def run( self, basedate, local_vars: dict = None ):
		# setup the base data
		#
		my_locals = {
			"BASDATE": Value(basedate,picture="%Y%b%d %H%M"),
			"BTM": Value(basedate,picture="%Y%b%d %H%M"),
			"CURDATE": Value(datetime.datetime.now(tz=Value.shared["tz"]).replace(tzinfo=None),picture="%Y%b%d %H%M"),
			"CTM": Value(datetime.datetime.now(tz=Value.shared["tz"]).replace(tzinfo=None),picture="%Y%b%d %H%M"),
		}

		# If locals were passed in, set them too
		if local_vars:
			for key, value in local_vars.items():
				my_locals[key] = value

		print("Timezone: %s" % Value.shared["tz"], file=sys.stderr)
		print("BASDATE: %s" % repr(my_locals["BASDATE"]), file=sys.stderr)
		print("BTM: %s" % repr(my_locals["BTM"]), file=sys.stderr)
		print("CURDATE: %s" % repr(my_locals["CURDATE"]), file=sys.stderr)
		print("CTM: %s" % repr(my_locals["CTM"]), file=sys.stderr)

		# Compile the report, so source and line number information can be reported to the user
		exec(compile(self.datadef, self.repfilename, "exec"), globals(), my_locals)

		# loop through my_locals and add them
		# to a dictionary with the % in front of the them
		# to mark location on the report
		self.data = { }

		for key in my_locals:
			if isinstance(my_locals[key], Value ):
				self.data["%"+key] = my_locals[key]
