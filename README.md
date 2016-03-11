# repgen5

This is a partial copy of HEC's (Hydrologic Engineering Center) repgen program.
The program creates fixed form text reports from a time series database, and textfiles.

The basic structure of a report input is as follows

```
#FORM
Title

Average %SCALAR
%TS
%TS
%TS
#ENDFORM
#DEF
arbitrary python code
#ENDDEF

```

Where %SCALAR is a simple fixed value and %TS are the first 3 values of a time series you've loaded.
see test/test.input.python for a full example.


## Currently Implemented

### Value 
This is the basic unit of a report, an instance can be either a time series or scalar values. Any variables using this type
will be added to a list with "%" in front of the names and can be used on the report form.


#### operations

##### Creating Values

The following keywords can be used for all Values:

Keyword | Description |
------- | ----------- |
picture | python format string or time format string, tells the system how to format the value |
misstr  | what to display when a value is missing (None) |
undef   | what to display when a value is undefdefined (this isn't implemented yet but was part of the original repgen program, general meaning is the time series you asked for doesn't actually exists the database being used) |
dbtype  | copy,gents,spkjson are the current valid values. This tells the system how it should interpret the supplied keywords |

Everytime you set a keyword, Value stores the last used value. If a keyword doesn't need to change between values (e.g. they all need to render the same) you don't have to include it when creating the additional values.


##### Scalar value

```python
SCALAR=Value(1) # except whatever the last picture was
SCALAR2=Value(2,picture="%d")
```


##### Generate Time Series 

```python
t1 = datetime.datetime.now(pytz.utc)
t1 = t1.replace(minute=0,second=0,hour=12)
t2 = t1+datetime.timedelta(hours=2)

v = Value(dbtype="gents",value=1, start=t1,end=t2, interval=datetime.timedelta(minutes=15), picture="%0.02f")
v2 = Value(dbtype="gents",value=2, start=t1,end=t2, interval=datetime.timedelta(minutes=15), picture="%0.02f")

```

##### Get times

```python
vt = v.datatimes()
vt.picture = "%Y%b%d %H%M"
```

This will get the times of v and create a new time series whos values are the times of v. The new timesseries times will also be those of v.
picture is so that when the report is filled the a time format will be used


##### Retreive Time Series

```python
ts = Value(dbtype="spkjson", 
	   dbloc="BLB BLBQ-Black Butte Outflow-Stony Cr", dbpar="Stage", dbptyp="Inst", dbint="15Minutes", dbdur="0", dbver="Combined-val",
	   dbtz=pytz.utc, dbunits="ft" )
```

The start and end could also be used, in this example the start and end from the gents section is used.
This allows you to get multiple time series of data by only changing the needed parameters.
for example if we wanted the Stages (height of water in a channel) from several differnt locations we could to the following:
```python
ts = Value(dbtype="spkjson", 
	   dbloc="BLB BLBQ-Black Butte Outflow-Stony Cr", dbpar="Stage", dbptyp="Inst", dbint="15Minutes", dbdur="0", dbver="Combined-val",
	   dbtz=pytz.utc, dbunits="ft"
	   start=datetime.datetime.now()-datetime.timedelta(hours=4)
	   end=datetime.datetime.now())
ts2 = Value( dbloc="Location2")
ts2 = Value( dbloc="Location3")
```

spkjson is a simple format that looks like the following:

```javascript
	{
		"site": "sitename",
		"units": "whatever the units are",
		"data":[
			[t1,v1,q1],
			[t2,v2,q2],
			...,
			[tn,vn,qn]
		

		]

	}

```

This particular case uses httplib to retrieve data. Host and port and be specified as keywords, or as parameters on the command line.

Adding new methods is a simple as adding a new elif block to the constructor of Value where you see the other types.

##### Math

```python
# after creating the 2 time series as above
v3 = v + v2

```

This will add the points of both time series that intersect in time. It will loop through v then through v2 and whenever the dates match add a new row with the value as the sum.
All of the basic operators are implemented.  
If v2 was a scalar value or a simple constant value v would loop through and add the value to all of its values.


###### Complex operations

If you need to do something more complex you can create a function,lamba, or callable class and use the apply function of Value.

```python
# first define a function
def func( v, v2 ):
	return v + math.log(v2)
# the parameters should be in the same order as what they represent in the function
v3 = Value.apply( func, v, v2 )
```

That was a rather contrived example. Lets say you needed to do something that has a starting value and always references the previous value.

```python
class Func:
	def __init__( self, starting_val):
		self.previous_val = starting_val

	def __call__(self, new_val, decay):
		self.previous_val = self.previous_val*decay + new_val
		return self.previous_val

func = Func(1)
v3 = Value.apply( func, v, .5 )
```

You can also return multiple values

```python
class Func:
	def __init__( self, starting_val):
		self.previous_val = starting_val

	def __call__(self, new_val, decay):
		self.previous_val = self.previous_val*decay + new_val
		return self.previous_val, new_val/self.previous_val
func = Func(1)
# tell the system how many values your function will return with the returns keyword.
v3,v4 = Value.apply( func, v, .5, returns=>2)
```
There are also other helper functions

Function|Description|
--------|-----------|
sum     | Sums all values given. You can feed it any combination of variable types, scalar, time series, or constant number|
average | Give an average of the values passed in. You can give the function EITHER multiple scalar values, or a single time series value.|
count   | Counts the number of not missing values in all values given.|
accum   | Calculates a running accumulation of the values in a provided time series.|
gettimes| Creates a new Value or data values are the times of the give timeseries. (The times of the new Value will also be that of the given time series.)|

### TODO:

Implement as many helper functions from the original repgen as make sense.

Perhaps build a tool to convert original repgen #DEF sections to the python format.


