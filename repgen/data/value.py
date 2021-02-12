import pytz
from inspect import isfunction
# types
string_types = ("".__class__,u"".__class__)
number_types = (int,float,complex)

class Value:
	shared = {
		"picture" : "NNZ",
		"misstr"  : "-M-",
		"undef"   : "-?-",

		# shared and updated between calls
		"host" : None, # ip address/hostname or file name
		"port" : None,
		"dbtype" : None, # file or spkjson
		"tz" : pytz.utc,
		"start": None,
		"end": None,
		"interval": None,
		"value": None, # this value is only used for generating time series
	}
	

	
	def __init__( self, *args, **kwargs ):
		self.index = None
		self.type="SCALAR"
		self.value = None
		self.values = []
		self.picture="%s"

		# go through the keyword args,
		# set them as static variables for the next call

		# update the shared keywords
		for key in kwargs:
			value = kwargs[key]
			if key.lower()=="tz" and isinstance(value, string_types):
				value = pytz.timezone(value)
			if (key.lower() == "start" or key.lower() == "end" or key.lower() == "time")  and isinstance(value,(Value)):	
				value = value.value # internally we want the actual datetime
			if key.lower() == "time":
				Value.shared["start"] = value
				Value.shared["end"] = value
			
			Value.shared[key.lower()] = value
		
		# load the keywords for this instance
		for key in Value.shared:
			self.__dict__[key] = Value.shared[key] 

		if len( args ) == 1: 
			self.value = args[0]
			return
		elif len(args)> 0: raise Exception ("Only 1 non named value is allowed")
		
		self.type = "TIMESERIES"	
		self.values = [ ] # will be a touple of (time stamp, value, quality )
		
		if self.dbtype is None:
			raise Exception("you must enter a scalar quantity if you aren't specifying a data source")
		elif self.dbtype.upper() == "FILE":
			pass
		elif self.dbtype.upper() == "COPY":
			pass
		elif self.dbtype.upper() == "GENTS":
			current_t = self.start
			end_t = self.end
			while current_t <= end_t:
				if isinstance(self.value, number_types):
					self.values.append( ( current_t.astimezone(self.tz),self.value,0 ) )
				elif isinstance(self.value, Value ):
					self.value = self.value.value 
					self.values.append( ( current_t.astimezone(self.tz),self.value,0 ) )
				elif isfunction(self.value):
					self.values.append( ( current_t.astimezone(self.tz),self.value(),0 ) )
					
				current_t = current_t + self.interval
			
		elif self.dbtype.upper() == "SPKJSON":
			try:
				import json
			except:
				try:
					import simplejson as json
				except:
					print >>sys.stderr, "To run this program you either need to update to a newer python, or install the simplejson module."

			import httplib, urllib
	
			fmt = "%d-%b-%Y %H%M"
			tz = self.tz
			units= self.dbunits
			ts_name = ".".join( (self.dbloc, self.dbpar, self.dbptyp, self.dbint, self.dbdur, self.dbver) )
			
			print >> sys.stderr, "Getting %s from %s to %s in tz %s, with units %s" % (ts_name,self.start.strftime(fmt),self.end.strftime(fmt),str(tz),units)
			query = "/fcgi-bin/get_ts.py?"
			params = urllib.urlencode( {
				"site": ts_name,
				"units": units,
				"start_time": self.start.strftime(fmt),
				"end_time":   self.end.strftime(fmt),
				"tz": str(self.tz)
			})
			try:
				conn = httplib.HTTPConnection( self.host + ":" + str(self.port))
				conn.request("GET", query+params )
				r1 = conn.getresponse()
				data =r1.read()

				data_dict = json.loads(data)
				# get the depth
				prev_t = 0
				#print repr(data_dict)
				for d in data_dict["data"]:
					_t = float(d[0])/1000.0 # spkjson returns times in javascript time, milliseconds since epoch, convert to unix time of seconds since epoch
					# this seems to work to have the data in the right time
					# will need to keep an eye on it though
					_dt = datetime.datetime.fromtimestamp(_t,pytz.utc)
					#print _dt
					#_dt = _dt.astimezone(self.tz)
					_dt = _dt.replace(tzinfo=self.tz)
					#print _dt
					if d[1] is not None:
						_v = float(d[1]) # does not currently implement text operations
					else:
						_v = None
					_q = int(d[2])
					self.values.append( ( _dt,_v,_q  ) )

				if self.start == self.end:
					self.type = "SCALAR"
					self.value = self.values[0][1]
			except Exception as err:
				print( repr(err) + " : " + str(err) )
		elif self.dbtype.upper() == "DSS":
			raise Exception("DSS retrieval is not currently implemented")
			
	# math functions
	def __add__( self, other ):
		return self.domath(operator.add,other)


	def __sub__( self, other ):
		return self.domath( operator.sub, other )

	def __mul__( self, other ):
		return self.domath( operator.mul, other)

	def __truediv__(self,other):
		return self.domath( operator.div,other)

	
	def domath(self,op,other):
		typ = Value.shared["dbtype"]
		tmp = Value(dbtype="copy")
		Value.shared["dbtype"]=typ
		print( "Doing Op %s on %s with other %s" % (repr(op),repr(self),repr(other) ) )
		if isinstance( other, number_types ) and self.type=="TIMESERIES":
			for v in self.values:
				if (v is not None) and (other is not None):
					tmp.values.append( (v[0],op(v[1], other),v[2]) )
				else:
					tmp.values.append( ( v[0], None, v[2] ) )
		elif isinstance( other, (int,float,complex,datetime.timedelta) ) and self.type=="SCALAR":
			if (self.value is not None) and (other is not None):
				tmp.value = op(self.value,other)
			else:
				tmp.value = None
			tmp.type="SCALAR"
		elif isinstance( other, Value ):
			if self.type == "SCALAR" and other.type == "SCALAR":
				if (self.value is not None) and (other.value is not None):
					tmp.value = op(self.value,other.value)
				else:
					tmp.value = None
				tmp.type = "SCALAR"
			elif self.type =="TIMESERIES" and other.type == "SCALAR":
				for v in self.values:
					if (v[1] is not None) and (other.value is not None):
						tmp.values.append( (v[0], op(v[1],other.value), v[1] ) )
					else:
						tmp.values.append( (v[0], None, v[1] ) )
			elif self.type =="SCALAR" and other.type == "TIMESERIES":
				for v in other.values:
					if (v[1] is not None) and (self.value is not None):
						tmp.values.append( (v[0], op(v[1],self.value), v[1] ) )
					else:
						tmp.values.append( (v[0], None, v[1] ) )
						
			elif self.type=="TIMESERIES" and other.type == "TIMESERIES":
			# loop through both arrays
				# for now just implement intersection
				for v_left in self.values:
					for v_right in other.values:
						if v_left[0] == v_right[0]: # times match
							if (v_left[1] is not None) and (v_right[1] is not None):
								tmp.values.append( (v_left[0],op( v_left[1], v_right[1] ), v_left[2] ) )
							else:
								tmp.values.append( (v_left[0], None, v_left[2] ) )
			else:
				return NotImplemented
		else:
			return NotImplemented
		return tmp
		
	

		
	def __str__(self):
		if self.type=="SCALAR":
			return self.format(self.value)
		else:
			return "Unable to process at this time"
	def __repr__(self):
		return "<Value,type=%s,value=%s,len values=%d, picture=%s>" % (self.type,str(self.value),len(self.values),self.picture)

	def format(self,value):
		#print repr(value)
		if isinstance(value, number_types):
			return self.picture % value
		elif isinstance(value, datetime.datetime) :

			if "%K" in self.picture:
				tmp = self.picture.replace("%K","%H")
				tmpdt = value.replace(hour=value.hour)
				if value.hour == 0 and value.minute==0:
					tmp = tmp.replace("%H","24")
					tmpdt = tmpdt - datetime.timedelta(hours=1) # get into the previous data
				return tmpdt.strftime(tmp)
				
				# special case, 2400 hours needs to be displayed
			return value.strftime(self.picture)
	# will need implementations of add, radd, mult, div, etc for use in math operations.
	def pop(self):
		if self.type == "SCALAR":
			return self.format(self.value)
		elif self.type == "TIMESERIES":
			if self.index is None:
				self.index = 0
			self.index = self.index+1
			try:
				#print repr(self.values[self.index-1])
				return self.format(self.values[self.index-1][1])
			except Exception as err:
				print(repr(err) + " : " + str(err), file=sys.stderr)
				return self.misstr

	def datatimes(self):
		"""
			Returns a new Value where the values are replaced by the datetimes
		
		"""
		typ = Value.shared["dbtype"]
		tmp = Value(dbtype="copy")
		Value.shared["dbtype"]=typ
		
		for v in self.values:
			tmp.values.append( (v[0],v[0],v[2]) )
		return tmp

	def qualities(self):
		"""
			Returns a new Value where the values are replace by the qualities
		"""
		typ = Value.shared["dbtype"]
		tmp = Value(dbtype="copy")
		Value.shared["dbtype"]=typ
		for v in self.values:
			tmp.values.append( (v[0],v[2],v[2]) )
		return tmp

	def set_time( self, **kwarg  ):
		if self.type == "SCALAR" and isinstance( self.value, datetime.datetime ):
			self.value = self.value.replace( **kwarg )
		else:
			raise Exception("Not implemented for the requested change")

	def last(self):
		if self.type =="TIMESERIES":
			
			typ = Value.shared["dbtype"]
			tmp = Value(dbtype="copy")
			Value.shared["dbtype"]=typ
			tmp.value = None
			tmp.type ="SCALAR"
			try:
				tmp.value = self.values[ len(self.values)-1 ] [1]
			except Exception as err:
				print >>sys.stderr, "Issue with getting last value -> %s : %s" % (repr(err),str(err))
			return tmp
		else:
			raise Exception("operation only valid on a time series")
	
	def __getitem__( self, arg ):
			dt = arg
			if isinstance(arg,Value):
				dt = arg.value
			if self.type == "TIMESERIES":
				typ = Value.shared["dbtype"]
				tmp = Value(dbtype="copy")
				Value.shared["dbtype"]=typ
				tmp.value = None
				tmp.type ="SCALAR"
				haveval =False
				for v in self.values:
					if v[0] == dt:
						tmp.value = v[1]
						haveval = True
						break
				if haveval == True:
					return tmp
				else:
					raise KeyError("no value at %s" % str(dt) )
			else:
				raise Exception("date index only valid on a timeseries")

	"""
		The following are static methods as they can be applied to multiple time series/values at a time

		all functions should process a keyword treat which determines how the function will reponsd
		to missing values

		valid values for treat will be the following:

		a number   - if a value is missing (None) use this number in its place
		a touple of numbers - if a value is missing, substitude in order of the arguments these replacement values
		"IGNORE"   - operate as if that row/value wasn't there
		"MISS"     - if any given value is missing, the result is missing (This is the default)
	
		Generally args should be either a list of SCALAR values (actual number types are okay)
		or a single time series.
		
		
	"""
				

	@staticmethod
	def apply( function, *args, **kwargs ):
		"""
			apply an arbitrary user function to the provided data.
			the inputs to the function must the same number of and in the same order as passed into args
			the function is called using function(*args)
			
			the function must return a number or None
			the function can be any callable object: function,lambda, class with a __call__ method, etc
			
		"""
		returns = 1 #
		try:
			returns = int(kwargs["returns"])
		except:
			pass
		values = []
		typ = Value.shared["dbtype"]
		for i in range(0,returns):
			tmp = Value(dbtype="copy")
			tmp.values = []
			tmp.value = None
			values.append( tmp )
			Value.shared["dbtype"]=typ
		
		times = Value.gettimes(*args,**kwargs)
		if len(times)==0:
			tmp.type = "SCALAR"
			# get the numbers of everything
			#tmp.value = function( *args )
			ret = function( *args )
			if isinstance( ret, (list,tuple) ):
				for i in range(len(ret)):
					values[i].value = ret[i]
					
			else:
				values[0].value = ret
		elif len(times) > 0:
			for t in times:
				vars = []
				for arg in args:
					if isinstance( arg, (int,float,complex) ):
						vars.append(arg) 
					elif isinstance( arg, Value ) and arg.type=="SCALAR":
						vars.append( arg.value) # need to handle missing value (.value is None)						
					elif isinstance( arg, Value ) and arg.type=="TIMESERIES":
						try:
							v = arg[t].value
							vars.append(v)
						except KeyError as err:
							vars.append(None) # here we handle the missing value logic
				res = None
				try:
					res = function( *vars )
				except Exception as err:					
					print >> sys.stderr, "Failed to compute a values %s : %s" % (repr(err),repr(str))
				if isinstance( res, (list,tuple)):
					for i in range(len(res)):
						values[i].values.append( (t,res[i],0) )
				else:
					values[0].values.append( ( t,res,0) )

		return values
	@staticmethod	
	def sum( *args, **kwarg ):
		"""
			this is an exception to the one timeseries rule.
			we assume the user wants whatever values passed summed up into 
			one value
		"""
		tmp = Value.mktmp()
		tmp.value = 0
		tmp.type="SCALAR"
		treat=Value.gettreat(**kwarg)
		
		for arg in args:
			if isinstance( arg, number_types ):
				tmp.value += arg
			if arg.type =="SCALAR":
				if arg.value is not None:
					tmp.value += arg.value
				else:
					if isinstance( treat, number_types):
						tmp.value += treat
					elif treat=="MISS":
						tmp.value = None
						return tmp
					# else, move to the next value
			elif arg.type == "TIMESERIES":
				for row in arg.values:
					v = row[1]
					if v is not None:
						tmp.value += v
					else:
						if isinstance( treat, number_types):
							tmp.value += treat
						elif treat=="MISS":
							tmp.value = None
							return tmp
			
		return tmp

	@staticmethod
	def average( *args, **kwarg ):
		tmp = Value.mktmp()
		tmp.value = 0
		tmp.type="SCALAR"
		treat = Value.gettreat(**kwarg)
		numvals = 0
		if len(args) > 1:
			for arg in args:
				if arg.type=="TIMESERIES":
					raise Exception("Time series not allowed with mulitple values")
		
		if len(args) == 1:
			if args[0].type == "SCALAR":
				tmp.value = args[0].value
			else: # time series
				for row in args[0].values:
					v = row[1]
					if v is not None:
						tmp.value += v
						numvals += 1
					elif treat == "MISS":
						tmp.value = None
						return tmp

				tmp.value = tmp.value/float(numvals)
		else:
			for arg in args:
				if isinstance( arg, number_types ):
					tmp.value += arg
					numvals += 1
				else:
					if arg.value is not None:
						tmp.value += arg.value
						numvals += 1
					elif treat=="MISS":
						tmp.value = None
						return tmp
			tmp.value = tmp.value/float(numvals)
		return tmp
		

	@staticmethod
	def count(*args ):
		"""		
			This function ignores the only 1 timeseries rule and just counts the number of non-missing
			values in all the variables passed in.
			It also doesn't take any keywords
		"""
		tmp = Value.mktmp()
		tmp.value = 0
		tmp.type = "SCALAR"
		for arg in args:
			if isinstance(arg, number_types):
				tmp.value+=1
			elif isinstance(arg, Value) and arg.type =="SCALAR" and arg.value is not None:
				tmp.value+=1
			elif isinstance(arg, Value) and arg.type =="TIMESERIES":
				for row in arg.values:
					if row[1] is not None:
						tmp.value+=1
			
		
		return tmp

	@staticmethod
	def accum(arg,**kwarg ):
		"""	
			This function requires a single time series and nothing else

			treat
			number = use the number
			ignore = current value is missing, but otherwise keep accumulating
			miss = stop accumulating after the first missing input
			
		"""
		tmp = Value.mktmp()
		tmp.type="TIMESERIES"
		tmp.values = []
		treat = Value.gettreat(**kwarg)
		accum = 0
		previous = 0
		for row in arg.values:
			dt,v,q = row
			cur = None
			
			if v is not None and not ((previous is None) and (treat=="MISS")) :
				accum += v				
				cur = accum
			elif v is None and ((previous is None) and (treat=="MISS")): 
				cur = None
			elif isinstance(treat, number_types):
				accum += v
			else:
				cur = None
		
			previous=v
				
		
			tmp.values.append( (dt,cur,q) )
		return tmp

	@staticmethod
	def gettimes( *args,**kwargs ):
		# build a new last that has the interestion or union (user specified, just implement intersection for now
		# scalar values will just get copied in time, we do need to maintain the order of the input args.
		timesets = []	
		times = []
		for arg in args:
			if isinstance( arg, Value) and arg.type == "TIMESERIES":
				timesets.append( set( [x[0] for x in arg.values ]) )	
		if len(timesets) > 0:
			if len(timesets)==1:
				times = list(timesets[0])
			else:
				times =list( timesets[0].intersection( *timesets[1:] ) ) # here we should check for intersection or union

		times.sort() # make sure everything is in time ascending order
		return times

	@staticmethod
	def mktmp():
		typ = Value.shared["dbtype"]
		tmp = Value(dbtype="copy")
		Value.shared["dbtype"]=typ
		return tmp
	@staticmethod
	def gettreat(**kwarg):
		treat = "MISS"
		for key in kwarg:
			if key.lower() == "treat":
				treat= kwarg[key]
		if isinstance(treat, string_types):
			treat=treat.upper()
		return treatg