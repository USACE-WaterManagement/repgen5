# repgen5

This is a partial copy of HEC's (Hydrologic Engineering Center) repgen program.
The program creates fixed form text reports from a time series database, and textfiles.


## Requirements
* Python 3.6 or higher
* pytz>=2022.1


### Optional
* python-dateutil>=2.8.2
    * Recommended for proper leap year adjustment for some date computations


## Using
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


#### Operations

##### Creating Values

The following keywords can be used for all Values:

Keyword | Description |
------- | ----------- |
picture | python format string or time format string, tells the system how to format the value |
misstr  | what to display when a value is missing (None) |
undef   | what to display when a value is undefined (this isn't implemented yet but was part of the original repgen program, general meaning is the time series you asked for doesn't actually exists the database being used) |
dbtype  | copy,gents,spkjson,radar are the current valid values. This tells the system how it should interpret the supplied keywords |

Every time you set a keyword, Value stores the last used value. If a keyword doesn't need to change between values (e.g. they all need to render the same) you don't have to include it when creating the additional values.


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

This will get the times of v and create a new time series whose values are the times of v. The new times series times will also be those of v.
picture is so that when the report is filled the time format will be used


##### Retrieve Time Series

```python
ts = Value(dbtype="radar", 
	   dbloc="Black Butte-Outflow", dbpar="Stage", dbptyp="Inst", dbint="15Minutes", dbdur="0", dbver="Combined-val",
	   dbtz="UTC", dbunits="ft", dbofc="SPK" )
```

The start and end could also be used, in this example the start and end from the gents section is used.
This allows you to get multiple time series of data by only changing the needed parameters.
for example if we wanted the Stages (height of water in a channel) from several different locations we could to the following:
```python
ts = Value(dbtype="radar", 
	   dbloc="Black Butte-Outflow", dbpar="Stage", dbptyp="Inst", dbint="15Minutes", dbdur="0", dbver="Combined-val",
	   dbtz="PST8PDT", dbunits="ft", dbofc="SPK"
	   start=datetime.datetime.now()-datetime.timedelta(hours=4)
	   end=datetime.datetime.now())
ts2 = Value( dbloc="Location2")
ts3 = Value( dbloc="Location3")
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
		// tn is a javascript timestamp in local time (not UTC)
		// vn is the value
		// qn is the quality code (0 is normal, 5 means value is missing)
	}
```

This particular case uses httplib to retrieve data. Host and port and be specified as keywords, or as parameters on the command line.

Adding new methods is a simple as adding a new elif block to the constructor of Value where you see the other types.


##### GROUPing

Grouping of multiple timeseries can be done by building a Python array of values and constructing a new Value with that array.
This roughly maps to the GROUP function in repgen4.

```python
group = Value([ts, ts2, ts3])
```

Note: Not all operations or functions are currently implemented for arrays/groups. Most mathematical operators and functions are, however.


###### Building dynamic groups (IGROUP)

The repgen4 function IGROUP is not implemented. However the equivalent is possible with regular Python code.

The following is a template showing how to do this:
```python
<RESULT> = Value([l[re.sub(<MARKER>, str(idx), <NAME TEMPLATE>)] for l in (locals(),) for idx in range(<START>, <END>+1)])
```

To build a group of all time series values named with the pattern **tsxx** (where _xx_ is a number; e.g. ts1, ts2, etc...), starting from **1**, to the number stored in the **YRS** value (50, in this case):

In repgen4, this would be done with the following code
```fortran
%YRS=50
	PICTURE=ZZ
%ts1
	DB=%DB
	DBLOC="Black Butte-Pool" DBPAR=Stor DBPTYP=Inst DBINT=~1Day DBDUR=0 DBVER=Calc-val
	DBUNITS=ac-ft
	DBTZ=PST8PDT
	TIME=%T1
	PICTURE=NNNNNNZ     MISSTR="   -NR-"    UNDEF="   -NR-"
%ts2
	TIME=%T2
%ts3
	TIME=%T3

%ABT=IGROUP(xx,1,%YRS,%tsxx)
```

In repgen5, this can be implemented with
```python
YRS = Value(50,
	PICTURE="%2.0f",
)
ts1 = Value(
	dbtype="radar",
	DBLOC="Black Butte-Pool", DBPAR="Stor", DBPTYP="Inst", DBINT="~1Day", DBDUR=0, DBVER="Calc-val",
	DBUNITS="ac-ft", 
	DBTZ="PST8PDT",
	TIME=T1,
	PICTURE="%7.0f",
	MISSTR="   -NR-",
	UNDEF="   -NR-",
)
ts2 = Value(
	TIME=T2,
)
ts3 = Value(
	TIME=T3,
)

ABT = Value([l[re.sub("xx", str(idx), "tsxx")] for l in (locals(),) for idx in range(1, l["YRS"].value+1)])
```

Both constants, and variables, can be used for the range elements. When using a variable, the `l["NAME"].value` syntax must be used.

Note that the template string (e.g. "tsxx") _must_ contain the marker string ("xx").


##### Math

```python
# after creating the 2 time series as above
v3 = v + v2
```

This will add the points of both time series that intersect in time while ignoring those that don't. It will loop through v then through v2 and whenever the dates match add a new row with the value as the sum.
All of the basic operators are implemented.  
If v2 was a scalar value or a simple constant value v would loop through and add the value to all of its values.


###### Complex operations

If you need to do something more complex you can create a function, lambda, or callable class and use the apply function of Value.

```python
# first define a function
def func( v, v2 ):
	return v + math.log(v2)
# the parameters should be in the same order as what they represent in the function
v3 = Value.apply( func, v, v2 )
```

Since that was a rather contrived example let's try something more complicated. Lets say you needed to do something that has a starting value and always references the previous value.

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


#### Common helper functions

There are also other helper functions, which are analogous to their repgen4 counterparts:

Function  | Description|
----------|------------|
sum       | Sums all values given. You can feed it any combination of variable types, scalar, time series, or constant number|
min       | Gives the minimum of all values given. You can feed it any combination of variable types, scalar, time series, or constant number|
max       | Gives the maximum of all values given. You can feed it any combination of variable types, scalar, time series, or constant number|
average   | Give an average of the values passed in. You can give the function EITHER multiple scalar values, or a single time series value.|
count     | Counts the number of not missing values in all values given.|
accum     | Calculates a running accumulation of the values in a provided time series.|
diff      | Generates a new timeseries calculated from the difference of a respective time series value and it's prior value. |
gettimes  | Creates a new Value or data values composed of the times of the given timeseries. (The times of the new Value will also be that of the given time series.)|
element*  | Returns the element in a timeseries at the supplied datetime.|
last*     | Returns the last element of a timeseries as a scalar.|
roundpos* | Rounds the decimal position of all values to the specified range.|
datatimes*| Gets a timeseries where the values are composed of the times.|
known*    | Returns a boolean indicating if a scalar has a value defined, or a timeseries has at least one value defined.|
ismissing*| Returns a boolean indicating if a scalar, or all values of a timeseries, are missing.|


\* Indicates the function is an instance member, which operates directly on the Value it's referencing, such as 
```python
lastval = ts.last()
```

### Converting repgen4 reports

There is a tool to help convert report files from repgen4 format to repgen5.

This tool most likely won't be a 100% conversion, but it should do at least 80% of the effort.

The tool is composed of the primary conversion script: [convert_report.py](converter/convert_report.py); as well as a wrapper to process entire directories: [convert.sh](converter/convert.sh).


#### Usage

Using the tool is accomplished by passing in the source file, and the destination it should be written to:

`./convert_report.py <input_file> <output_file>`

For example:

`./convert_report.py ~/repgen4/reports/i-blb ~/repgen5/reports/i-blb`

To convert an entire directory at once:

`./convert.sh ~/repgen4/reports ~/repgen5/reports`

Note that the output is very verbose, and contains a lot of information for debugging report conversion. It is recommended to redirect this output to a file for closer review.

`./convert.sh ~/repgen4/reports ~/repgen5/reports > convert.log 2>&1`

Warnings and errors will be output to stderr and will contain an **ERROR** or **WARNING** prefix.


#### Customization

More than likely, the tool will require adjustments to successfully migrate with a minimal amount manual work afterwards.

The options available for customization are documented at the top of the script. It is recommended to copy this file to customize the changes, as they may vary from report to report.

Option         |Description|
---------------|-----------|
BLOCKQUOTE_FORM| Wraps #FORM and #ENDFORM with Python-style block-quote characters ("""). This doesn't change the result, but aids for debugging and visualization with syntax highlighters by hiding the FORM, since it's not valid Python.|
SHOW_PREVIOUS  | If `True`, the original repgen4 statements will be included as comments with the respective converted repgen5 statements. Also useful for debugging and documentation.|
DATE_HACK      | A flag to change how datetime calculations are performed. Full description of allowed values and what they do is provided in the script itself.|


### TODO:

Implement as many helper functions from the original repgen as make sense.

Integrate https://github.com/gyanz/pydsstools
