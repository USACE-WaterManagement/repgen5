#!/usr/bin/env python3
############################################################
# Repgen 4 -> 5 report converter                           #
# Author: Daniel Osborne <Daniel.T.Osborne@usace.army.mil> #
############################################################
# This attempts to convert an existing repgen_4            #
# report script to the repgen_5 format.                    #
# Output will require manual examination and editing.      #
############################################################

import sys
import re
from datetime import datetime
from typing import Match

# Controls if #FORM data should be block-quoted, useful for debugging in an IDE and avoiding syntax errors in report definitions.
BLOCKQUOTE_FORM = False

# If True, any statements that were converted will be preserved in the output as comments (prepended with '#-')
SHOW_PREVIOUS = False

# The following is not recommended unless you know what you are doing.
# These are flags, so multiple can be specified by adding them together (though not all are valid together).
# A proper fix for this is to implement a custom datetime class in repgen which handles 2400 properly.
# Values:
#   0 = No date hacks (recommended)
#   1 = Use 1μs before specified time (23:59:59.999999 instead of 24:00)
#   2 = Don't add a day for the calculation adjustment (SPK's battery reports)
#   4 = Increment the starting day of the month by one (SPK's battery & monthly reports)
DATE_HACK = 0

##############################################
#### Careful changing anything below here ####
##############################################

HAS_RELATIVEDELTA = False
# This isn't a fool-proof detection, but if you run this on the same machine/environment as repgen, it'll work.
try:
    # Relativedelta supports months and years, but is an external library
    from dateutil.relativedelta import relativedelta as timedelta
    HAS_RELATIVEDELTA = True
except:
    pass

#region Value
class Value:
    """
    This represents a Value data object.
    Converts an optional explicit value, and a set of key=value pairs, into the proper Value() format for repgen5.
    """
    PREDEFINED = ["BTM", "BASDATE", "CURDATE", "CTM"]

    def __init__( self, *args, **kwargs ):
        print("New Value %s" % repr(args))

        self.value = None
        self.name = None
        self.parameters = {}
        self.predefined = False
        self.append = ""
        self.special_parameters = []

        if len(args) > 0:
            self.name = args[0]
        if len(args) > 1:
            self.value = args[1]

        if self.name in Value.PREDEFINED:
            print("Predefined")
            self.predefined = True

    def __str__(self):
        result = ""

        if self.predefined:
            if self.name and self.value:
                if not (self.value.startswith(".value") or self.value.startswith(f"{self.name}.value")):
                    result = f"{self.name}"
                    if self.name not in Value.PREDEFINED:
                        result = result + ".value"
                    result = result + " = "
                elif self.value.startswith(f"{self.name}.value"):
                    result = f"{self.name}"
                    if self.name in Value.PREDEFINED:
                        result = result + ".value"
                    result = result + " = "

            if self.value:
                if self.value in Value.PREDEFINED:
                    result = result + "Value(" + self.value + ")\n"
                else:
                    result = result + self.value + "\n"
            for key in self.parameters:
                result = result + f'{self.name}.{key.lower()} = {self.parameters[key]}\n'
                if key != "value":
                    result = result + f'Value.shared["{key.lower()}"] = {self.parameters[key]}\n'
        else:
            special_msg = "\t# The following labels (variables) are passed as a key=value pair string, not just a value.\n" + \
                          "\t# Python doesn't really handle this well, so this is what the result ends up as.\n"
            if self.name:
                result = f"{self.name} = "

            if self.value:
                if not re.match(r"^Value\s*[(]", self.value, re.IGNORECASE):
                    result = result + f"Value({str(self.value)}"

                    if len(self.parameters) > 0:
                        result = result + ",\n"

                    for key in self.parameters:
                        result = result + f"\t{key}={self.parameters[key]},\n"
                    # special parameters are something like ^a in the report, where ^a contains the entire key=value pair string
                    # These won't be added in the same order compared to regular parameters in the original report
                    if len(self.special_parameters) > 0: result = result + special_msg
                    for special in self.special_parameters:
                        result = result + f"\t{special},\n"

                    result = result + ")\n"
                else:
                    result = result + str(self.value) + "\n"
                    for key in self.parameters:
                        result = result + f'{self.name}.{key.lower()} = {self.parameters[key]}\n'
            else:
                result = result + "Value(\n"
                for key in self.parameters:
                    result = result + f"\t{key}={self.parameters[key]},\n"

                if len(self.special_parameters) > 0: result = result + special_msg
                for special in self.special_parameters:
                    result = result + f"\t{special},\n"

                result = result + ")\n"

        if self.append != "":
            result = result + "\n" + self.append
        return result

    def addspecial(self, value: str):
        self.special_parameters.append(value)

    def __getitem__(self, key):
        return self.parameters[key]

    def __setitem__(self, key, value):
        print(f"Adding: {key}=>{value}")
        if key.lower() == "value":
            print(f"Renaming: {key}=>missing")
            key = "missing"
        self.parameters[key] = value

    def __contains__(self, key):
        return key in self.parameters
#endregion

# Write to stderr, but flush stdout so redirected output is in sync
def error(message: str):
    sys.stdout.flush()
    print(message, file=sys.stderr)

#region Picture conversions
# Long format specifiers need to be separate, to avoid ambiguity during lookup
DATE_PICTURE_MAP_LONG = {
    r"A{4,}": "%B",
    "YYYY": "%Y",
    # These are special pictures, using generic 'N's for dates
    "NN/NN/NN": "%m/%d/%y",
    "NN/NN": "%m/%d",
    "NN AAA NNNN": "%d %b %Y",
}

DATE_PICTURE_MAP = {
    "ZD": "%d",
    "DD": "%d",
    "ZM": "%m",
    "AAA": "%b",
    "ZZZY": "%Y",
    "YY": "%y",
    "ZY": "%y",
    "ZH": "%K",
    "HH": "%K",
    "ZT": "%M",
    "ZZ:ZT": "%K:%M",
    "ZZZT": "%K%M",
    "b": " ",
    '"': "",
}

def convert_picture_format(picture):
    count = 0
    decimal = False
    decimal_count = 0
    sign = False
    leading_zero = False
    first_zero_position = -1
    result = ""
    string = False
    current = ""
    triad_separator = ""
    prefix = ""
    extra = ""
    original_picture = picture
    picture = picture.strip()
    picture = re.sub(r'[Bb]', ' ', picture)

    result = picture

    while picture:
        #print(f"Checking: {picture}")
        # Some reports can use ZZZZ on a datetime to print only the hour minute, as HHMM.
        # Since this converter can't know the context of the picture; warn the user so they can check.
        if picture == "ZZZZ": error("WARNING: Possible ambiguous use of 'ZZZZ' format, check conversion!")

        # For simplicity of code, we'll build up each item until it matches in the lookup table, then reset.
        no_more = False
        while not no_more:
            no_more = True
            for pic,after in DATE_PICTURE_MAP_LONG.items():
                match = re.match(r"(" + pic + r")(\s*)", picture)
                if match:
                    picture = picture.replace(match.group(0), '', 1)
                    result = result.replace(match.group(1), after, 1)
                    #result = result + after + match.group(2)
                    no_more = False

            for pic,after in DATE_PICTURE_MAP.items():
                match = re.match(r"(?!%)(" + pic + r")(\s*)", picture)
                if match:
                    picture = picture.replace(match.group(0), '', 1)
                    result = result.replace(match.group(1), after, 1)
                    #result = result + after + match.group(2)
                    no_more = False
                    break   # if we got a short one, always end early and restart at a long specifier check

        if picture:
            char = picture[0]
            picture = picture[1:]

            if char == "S": sign = True
            else:
                if char == 'N':
                    count = count + 1

                    if decimal:
                        decimal_count = decimal_count + 1
                    extra = ""
                elif count > 0 and char == '.':
                    decimal = True

                    if first_zero_position > 0 and first_zero_position < count:
                        leading_zero = True

                    count = count + 1       # Width specifier includes the decimal separator
                    extra = ""
                elif count > 0 and char == ',':
                    triad_separator = ','
                    count = count + 1       # Width specifier includes the group separators, assume we have just one
                    extra = ""
                elif char == 'Z':
                    count = count + 1

                    if not decimal and first_zero_position == -1:
                        first_zero_position = count

                    if decimal:
                        decimal_count = decimal_count + 1
                    extra = ""
                else:
                    if count == 0 and decimal_count == 0:
                        prefix = prefix + char
                    else:
                        extra = extra + char
                    continue

                current = current + char

    if decimal_count > 0:
        result = result.replace(current, f"%{count}{triad_separator}.{decimal_count}f")
    elif count > 0:
        result = result.replace(current, f"%{count}{triad_separator}.0f")
    count = 0
    decimal_count = 0

    if "AA" in result: error("WARNING: Possible ambiguous use of 'A' format, check conversion!")

    print("Picture converted '%s' -> '%s'" % (original_picture, result))
    return result

def convert_picture(variable, picture):
    picture = convert_picture_format(picture)
    result = '%s.picture = "%s"' % (variable, picture)
    return result
#endregion

#region Math conversions
def map_ACCUM(*args):
    print("map_ACCUM( %s )" % repr(args))
    dest = args[0]
    flag = args[1].strip('"')
    source = args[2]
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + 'Value.accum(%s, treat="%s")' % (source, flag)
    return result

def map_DIFF(*args):
    print("map_DIFF( %s )" % repr(args))
    dest = args[0]
    flag = args[1].strip('"')
    source = args[2]
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + 'Value.diff(%s, treat="%s")' % (source, flag)
    return result

def map_SUM(*args):
    print("map_SUM( %s )" % repr(args))
    dest = args[0]
    flag = args[1].strip('"')
    source = ", ".join(args[2:])
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + 'Value.sum(%s, treat="%s")' % (source, flag)
    return result

def map_MIN(*args):
    print("map_MIN( %s )" % repr(args))
    dest = args[0]
    flag = args[1].strip('"')
    source = ", ".join(args[2:])
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + 'Value.min(%s, treat="%s")' % (source, flag)
    return result

def map_MAX(*args):
    print("map_MAX( %s )" % repr(args))
    dest = args[0]
    flag = args[1].strip('"')
    source = ", ".join(args[2:])
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + 'Value.max(%s, treat="%s")' % (source, flag)
    return result

def map_AVERAGE(*args):
    print("map_AVERAGE( %s )" % repr(args))
    dest = args[0]
    flag = args[1].strip('"')
    source = ", ".join(args[2:])
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + 'Value.average(%s, treat="%s")' % (source, flag)
    return result

def map_RNDPOS(*args):
    print("map_RNDPOS( %s )" % repr(args))
    dest = args[0]
    source = args[1].strip('"')
    places = args[2]
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + '%s.roundpos(%s)' % (source, places)
    return result
#endregion

#region Date/Time conversions
# Convert timezones to ones recognized by Python and Oracle
ZONE_MAP = {
    # "PST8PDT": "America/Los_Angeles",
    "PST": "Etc/GMT+8",                   # Special one, no DST; +8 is correct, see: https://en.wikipedia.org/wiki/Tz_database#Area
    # "MST7MDT": "America/Denver",
    # "MST": "Etc/GMT+7",                 # Maybe America/Phoenix instead?
    # "CST6CDT": "America/Chicago",
    # "CST": "Etc/GMT+6",
    # "EST5EDT": "America/New_York",
    # "EST": "Etc/GMT+5",
}

def convert_timeop(dest, source, op, value, duration):
    DURATION_MAP = {
        "M": "months",
        "MONTH": "months",
        "D": "days",
        "DAY": "days",
        "Y": "years",
        "YEAR": "years",
        "H": "hours",
        "HOUR": "hours",
        "MIN": "minutes",
        "MINUTE": "minutes",
    }

    if not HAS_RELATIVEDELTA:
        # Relative delta isn't present, so we have to manipulate the arguments to estimate the same time range for months and years
        if duration.upper() == "YEAR" or duration.upper() == "Y":
            newduration = "DAY"
            newvalue = int(value) * 365
            error(f"WARNING: dateutil module not present, estimating '{duration.upper()}={value}' as '{newduration.upper()}={newvalue}'")
            duration = newduration
            value = newvalue
        if duration.upper() == "MONTH" or duration.upper() == "M":
            newduration = "DAY"
            newvalue = int(value) * 30
            error(f"WARNING: dateutil module not present, estimating '{duration.upper()}={value}' as '{newduration.upper()}={newvalue}'")
            duration = newduration
            value = newvalue
    else:
        # reports use DAY math for adding/subtracting years, which assumes no leap days exist
        # Python includes leap days in calculations, so account for that
        if duration.upper().startswith('D') and int(value) % 365 == 0:
            years = int(value) / 365
            leap_days = (years % 4) + 1   # not accurate every 100 years (e.g. 2000)
            duration = "YEAR"
            value = leap_days
            result = "%s%ctimedelta(%s=%d)" % (source, op, DURATION_MAP[duration.upper()], years)
            return result

    result = "%s%ctimedelta(%s=%d)" % (source, op, DURATION_MAP[duration.upper()], int(value))
    return result

def map_DATATIME(*args):
    print("map_DATATIME( %s )" % repr(args))
    dest = args[0]
    source = args[1]
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + "%s.datatimes()" % (source)
    return result


# TIME is a no-op, since the data is already in time format
def map_TIME(*args):
    print("map_TIME( %s )" % repr(args))
    dest = args[0]
    source = args[1]
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + source
    return result

def map_SETTIME(*args, **kwargs):
    print("map_SETTIME( %s )" % repr(args))
    dest = args[0]
    source = args[1]
    result = ""
    extra = None
    show_comment = True

    if source.startswith("%"): source = source[1:]
    if dest.startswith("%"): dest = dest[1:]

    if "comment" in kwargs: show_comment = bool(kwargs["comment"])

    arguments = {}
    for x in range(2, len(args), 2):
        component = args[x]
        value = args[x + 1]
        ucomp = component.upper().strip()

        if value.startswith("%"):
            # Variable passed as 3rd argument
            if ucomp == "HOUR":
                arguments["hour"] = f"{value}.value.hour"
            if ucomp == "MINUTE":
                arguments["minute"] = f"{value}.value.minute"
            if ucomp == "SECOND":
                arguments["second"] = f"{value}.value.second"
                arguments["microsecond"] = 0        # Always clear the microseconds
            if ucomp == "TIME":
                arguments["hour"] = f"{value}.value.hour"
                arguments["minute"] = f"{value}.value.minute"
                arguments["second"] = 0
                arguments["microsecond"] = 0
            if ucomp == "DAY":
                arguments["day"] = f"{value}.value.day"
            if ucomp == "MONTH":
                arguments["month"] = f"{value}.value.month"
            if ucomp == "YEAR":
                arguments["year"] = f"{value}.value.year"
            if ucomp == "DATE":
                arguments["day"] = f"{value}.value.day"
                arguments["month"] = f"{value}.value.month"
                arguments["year"] = f"{value}.value.year"
        else:
            if ucomp == "HOUR":
                arguments["hour"] = value
            if ucomp == "MINUTE":
                arguments["minute"] = value
            if ucomp == "SECOND":
                arguments["second"] = value
                arguments["microsecond"] = 0        # Always clear the microseconds
            if ucomp == "TIME":
                arguments["hour"] = value[:2]
                arguments["minute"] = value[2:]
                arguments["second"] = 0
                arguments["microsecond"] = 0

            if ucomp == "DAY":
                # Hack to fix monthly reports
                if DATE_HACK & 4 and value == "1":
                    arguments["day"] = int(value) + 1
                    if DATE_HACK & 2 == 0:
                        source += "-timedelta(days=1)"
                else:
                    arguments["day"] = value
            if ucomp == "MONTH":
                arguments["month"] = value
            if ucomp == "YEAR":
                arguments["year"] = value
            if ucomp == "DATE":
                arguments["day"] = value[:2]
                arguments["month"] = datetime.strptime("%b", value[2:5]).strftime("%d")
                arguments["year"] = value[5:]

    if "hour" in arguments and arguments["hour"] == "24":
        # Python doesn't support 24 as a valid hour, so use 0, but set the date forward a day
        # Note, for month ranges, use the second block
        if DATE_HACK & 1:
            # This is sometimes needed for computing monthly or annual reports;
            # proper fix is to implement a custom datetime class
            arguments["hour"] = 23
            arguments["minute"] = 59
            arguments["second"] = 59
            arguments["microsecond"] = 999999
        else:
            arguments["hour"] = 0
            arguments["minute"] = 0
            arguments["second"] = 0
            arguments["microsecond"] = 0
            
            if DATE_HACK & 2 == 0:
                extra = "+ timedelta(days=1)"
                if show_comment: extra = extra + "    # Add a day to offset setting the time to 00, instead of 24"

    for key, value in arguments.items():
        # Strip leading zeros
        if isinstance(value, str): arguments[key] = re.sub(r"\b(?<!_)0([0-9]+)\b", r"\1", value)

    if source != dest:
        result = result + "Value(%s)\n" % source
        result = result + "%s.value = %s.value.replace(" % (dest, dest)
    else:
        result = result + "%s.value.replace(" % dest

    result = result + ','.join("%s=%s" % (key, val) for key, val in arguments.items())
    result = result + ")"

    if extra is not None:
        result = result + " %s" % extra

    print("Method converted -> %s" % result)
    return result

# Last hour is a specialized version of SETTIME
def map_LASTHOUR(*args):
    print("map_LASTHOUR( %s ) -> SETTIME" % repr(args))
    return map_SETTIME(args[0], args[1], "MINUTE", 0, "SECOND", 0)

def map_DAYOFYR(*args):
    print("map_DAYOFYR( %s )" % repr(args))
    dest = args[0]
    source = args[1]
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + "%s.value.timetuple().tm_yday" % (source)
    return result

def map_MONOFYR(*args):
    print("map_MONOFYR( %s )" % repr(args))
    dest = args[0]
    source = args[1]
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + "%s.value.timetuple().tm_mon" % (source)
    return result

def map_YEAR(*args):
    print("map_YEAR( %s )" % repr(args))
    dest = args[0]
    source = args[1]
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + "%s.value.timetuple().tm_year" % (source)
    return result

def map_MONTH(*args):
    print("map_MONTH( %s )" % repr(args))
    dest = args[0]
    source = args[1]

    if source.startswith("%"): source = source[1:]

    result = f"{source}.value.strftime('%B')"
    return result

def map_DAY(*args):
    print("map_DAY( %s )" % repr(args))
    dest = args[0]
    source = args[1]
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + "%s.value.timetuple().tm_mday" % (source)
    return result

def map_NDAYS(*args):
    print("map_NDAYS( %s )" % repr(args))
    dest = args[0]
    source = args[1]

    if source.startswith("%"): source = source[1:]

    result = "calendar.monthrange(%s.value.timetuple().tm_year, %s.value.timetuple().tm_mon)[1]" % (source, source)
    return result

def map_EOM(*args):
    print("map_EOM( %s )" % repr(args))
    dest = args[0]
    source = args[1]

    if source.startswith("%"): source = source[1:]

    if DATE_HACK & 4 and DATE_HACK & 2 == 0:
        source = "(%s-timedelta(days=1))" % source
    result = "calendar.monthrange(%s.value.timetuple().tm_year, %s.value.timetuple().tm_mon)[1]" % (source, source)
    # The object to be returned should be a date object, so pass through SETTIME
    # Since this is a function call mapping, the 'source' doesn't matter, as it's transitive.
    # The EOM is also assumed to be 2400 on the last day, so make sure that's explicitly set.
    return map_SETTIME(args[1], args[1], "YEAR", "%s.value.timetuple().tm_year" % source, "MONTH", "%s.value.timetuple().tm_mon" % source, "DAY", result, "HOUR", "24", comment=None)

# This assumes the values passed in are scalar Value types
def map_DMY2DATE(*args):
    print("map_DMY2DATE( %s )" % repr(args))
    dest = args[0]
    day = args[1]
    month = args[2]
    year = args[3]

    if day.startswith("%"): day = day[1:]
    if month.startswith("%"): month = month[1:]
    if year.startswith("%"): year = year[1:]

    if not day.isdigit():
        day = day + ".value"
    if not month.isdigit():
        month = month + ".value"
    if not year.isdigit():
        year = year + ".value"

    # bump day forward since python doesn't support hour 24
    result = f"datetime.datetime({year}, {month}, {day}) + timedelta(days=1)"
    return result

def convert_timezone(timezone):
    match = re.search(r'"?([A-Za-z0-9/_]+)"?', timezone)
    if match is not None:
        zone = match.group(1)
        newzone = ZONE_MAP.get(zone, zone)
        if newzone != zone:
            print("Convert timezone: %s -> %s" % (zone, newzone))

        timezone = timezone.replace(zone, newzone)
    return timezone
#endregion

#region Misc conversions
def map_GROUP(*args):
    print("map_GROUP( %s )" % repr(args))
    dest = args[0]
    source = ", ".join(args[1:])
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + '[%s]' % source
    return result

def map_IGROUP(*args):
    print("map_IGROUP( %s )" % repr(args))
    dest = args[0]
    index_str = args[1]
    start = args[2]
    end = args[3]
    index_var = args[4]

    result = ""
    arg_list = []

    # Since the index arguments can be variables, generate the code to build the list, instead of building it
    if index_var.startswith("%"): index_var = index_var[1:]
    if start.startswith("%"): start = start[1:]
    if end.startswith("%"): end = end[1:]

    # If start or end indexes aren't numbers, then they're probably variables, so grab the direct value
    try: start = int(start)
    except ValueError: start = f'l["{start}"].value'

    try: end = int(end)
    except ValueError: end = f'l["{end}"].value'

    result = result + f'[l[re.sub("{index_str}", str(idx), "{index_var}")] for l in (locals(),) for idx in range({start}, {end}+1)]'
    return result

def map_ELEMENT(*args):
    print("map_ELEMENT( %s )" % repr(args))
    dest = args[0]
    source = args[1]
    seek = args[2]
    time = args[3]
    missval = args[4]
    result = ""

    if source.startswith("%"): source = source[1:]

    result = result + f'{source}.element("{seek}", {time}, "{missval}")'
    return result

#endregion

def main(input: str, output: str):
    remapped_variables = {}             # If any variables had to be renamed, keep track of this mapping

    def getName(name: str):
        """Get a mapped name, if one exists. Returns argument if not mapped."""
        match = re.match(r'([%$])?([0-9][A-Z0-9_]+)', name, re.IGNORECASE)
        if match:
            result = remapped_variables.get(match.group(2), match.group(2))
            if match.group(1):
                result = match.group(1) + result
            return result
        return remapped_variables.get(name, name)
    def mapName(name: str):
        """Check if the passed in name is a valid identifier, if not, map it to a valid one in Python."""
        match = re.match(r'[%$]?([0-9][A-Z0-9_]+)', name, re.IGNORECASE)
        if match:
            remapped_name = f"_{match.group(1)}"
            remapped_variables[name] = remapped_name
            print(f"Mapping identifier '{match.group(1)}' -> {remapped_name}")
            return remapped_name
        return name

    with open(input) as reader:
        with open(output, "w") as writer:
            newline = ""
            oldline = ""
            is_value_decl = False
            value_declared = False
            value_printed = False
            dest = ""
            pending_variables = {}
            processed_variables = {}    # to avoid duplicate keys
            pending_picture = ""
            in_conditional = False      # We are inside an IF/ELSE
            is_conditional = False      # Current line is an IF/ELSE
            in_definition = False
            current_value = None
            indent_level = 0

            def cleanup(indent=False):
                nonlocal newline
                nonlocal oldline
                nonlocal is_value_decl
                nonlocal value_printed
                nonlocal value_declared
                nonlocal current_value

                if current_value:
                    print(f"Writing value: {current_value.name}; indent: {indent}; indent_level: {indent_level}")
                    output = str(current_value)

                    # If preserving old statements as comments, write those before the new
                    if SHOW_PREVIOUS and oldline != "":
                        writer.write(oldline)
                        oldline = ""

                    if indent:
                        # Python multiline matches CR and LF separately, so filter it out, if it exists
                        output = re.sub(r"^(.*)\r?\n", '\t' * indent_level + r"\1\n", output, flags=re.MULTILINE)

                    writer.write(output)
                    current_value = None

                    # Flush anything else remaining
                    if newline != "":
                        writer.write(newline + "\n")
                        newline = ""

            # Regex for matching KEY=VALUE pairs for Value assignment
            regex = re.compile(r'''
                                ([\S]+)\s*=            # a key (any word followed by optional space and an equal sign)
                                \s*                    # then optional space in between
                                ((?:
                                \s*                    # then optional space in between
                                    (?!\S+\s*=)\S+     # then a value (any word not followed by an equal sign)
                                )+)                    # match multiple values if present
                                ''', re.VERBOSE)

            while True:
                line = reader.readline()
                if line == '': break

                curline = line = line.strip("\r\n")
                curline = re.sub("^" + " " * 8, "\t", curline)
                stripped = curline.strip()
                #newline = stripped

                # Any comments, just pass through untouched
                if in_definition and not stripped.startswith("#"):
                    print(f"Processing line: {curline}")
                    # Transform each line, then write it to the output
                    if re.match(r"![-~]FUNCTION", curline): newline = "#"     # FUNCTION line isn't necessary
                    if re.match(r"!ECHO", curline): newline = "#"             # ignore !ECHO

                    # Loop through the line, grabbing tokens
                    # Parsing order matters
                    stripped = curline.strip()
                    found_match = False

                    # For name=value pairs, add a comma (,) to separate them
                    # Also quote them if they aren't special (have %)
                    result = ""
                    matches = regex.findall(curline.strip())
                    if stripped.startswith("%"):
                        cleanup(in_conditional)

                        value_declared = False
                        is_value_decl = True
                        processed_variables = {}

                        # Get the variable name
                        match = re.match(r"%([A-Z0-9_]+)", stripped, re.IGNORECASE)
                        dest = mapName(match.group(1))
                        print(f"Found variable name: {dest}; matches: {len(matches)}")

                        if not matches or len(matches) == 0:
                            current_value = Value(dest)
                    else:
                        if curline.startswith("MISSTR") or curline.startswith("UNDEF"):
                            match = matches.pop(0)
                            pending_variables[match[0]] = match[1]
                        if curline.startswith("VALUE"):
                            # Ignore VALUE lines
                            match = matches.pop(0)
                            newline = f'Value.shared["missing"] = "{match[1].upper()}"'

                    if len(matches) > 0:
                        for match in matches:
                            print(f"Found KVP for '{dest}': {match}")
                            key = getName(match[0].upper())
                            value = match[1]

                            # Make sure any referenced identifiers are valid, replacing with mapped value, if present
                            value = re.sub(r'%([A-Z0-9_]+)', lambda m: "%" + getName(m.group(1)), value)

                            reference_value = value

                            # variables with ^ prefix are special, convert those to _ for substitution
                            if re.match(r"[\^]([a-z])", value) or re.search(r'[%]', value):
                                value = re.sub(r"[\^]", "_", value)
                            else:
                                value = re.sub(r"[\^]([a-z])", r"{_\1}", value)

                            # If _a variables are by themselves, leave them as-is;
                            # but if they're mixed with other data, then wrap them in formatted strings (e.g. f"{_a}")
                            if not re.search(r"(?:[%$]|\b_[a-z]\b)", value) and not re.match(r"^\s*[0-9.-]+\s*$", value):
                                value = '"' + value.strip('"') + '"'
                            elif re.search(r"[{}]", value) and not re.search(r'[%"\']', value):
                                value = 'f"' + value.strip('"') + '"'

                            # Simple picture assignment
                            if key.upper() == "PICTURE":
                                found_match = True
                                pending_picture = convert_picture_format(match[1])
                                value = f'"{pending_picture}"'

                            # Time expression
                            match = re.search(r"%([A-Z0-9_]+)\s*([-+])\s*([0-9]+)([ADEHIMNORTUY]{1,6})(.*)", reference_value, re.IGNORECASE)
                            if match is not None:
                                found_match = True
                                value_declared = True
                                source = re.sub(r"[%$]", "", match.group(1))
                                operation = match.group(2)
                                time_value = match.group(3)
                                duration = match.group(4)
                                extra = match.group(5)

                                newvalue = convert_timeop(dest, source, operation, time_value, duration)
                                reference_value = reference_value.replace(match.group(0), newvalue + extra, 1)
                                value = value.replace(match.group(0), newvalue + extra)
                                print(f"Time expression: {match.group(0)} -> {newvalue}")

                            # Indexing operation
                            while True:
                                # First regex handles something like: "%VARK( %01OCT-1D , %EOMOCT )" second one handles something like: "%OCTK(LAST) - %OCTK(1)"
                                index_regex = r"%([A-Z0-9_]+)\s*\((.+\)?)\)" if ',' in reference_value else r"%([A-Z0-9_]+)\s*\((.+?\)?)\)"
                                match = re.search(index_regex, reference_value, re.IGNORECASE)
                                if match is not None:
                                    found_match = True
                                    value_declared = True
                                    source = re.sub("%", "", match.group(1))
                                    index = match.group(2)

                                    if index.upper() == "END" or index.upper() == "LAST": index = ".last()"
                                    elif index.upper() == "START": index = "[0]"
                                    else:
                                        indexers = [x.strip() for x in index.split(',')]
                                        newindexers = []
                                        for index in indexers:
                                            if index.upper() == "END" or index.upper() == "LAST": index = 0
                                            elif index.upper() == "START": index = 1
                                            
                                            # Convert repgen4 1-based index to python's 0-based
                                            # Note, this doesn't touch variable indexors, only constants
                                            if isinstance(index, int) or (isinstance(index, str) and index.isnumeric()):
                                                index = str(int(index) - 1)

                                            newindexers.append(index)
                                        index = f"[{':'.join(newindexers)}]"

                                    reference_value = reference_value.replace(match.group(0), '', 1)
                                    value = value.replace(match.group(0), f"{source}{index}")
                                    print(f"Indexing operation: {match.group(0)} -> {value}")
                                else:
                                    break

                            # Function call
                            while True:
                                match = re.search(r"(?!%)([A-Za-z0-9_]+)\s*\((.+?)(?:\)(?!\s*,))", reference_value)
                                if match is not None:
                                    print(f"reference_value: {reference_value}")
                                    found_match = True
                                    function = match.group(1).strip()
                                    arguments = match.group(2).strip()

                                    if function == "timedelta": break

                                    args = tuple(x.strip() for x in arguments.split(','))
                                    func = None

                                    try:
                                        func = globals()[f"map_{function}"] #FUNCTION_MAP.get(function, None)
                                    except KeyError:
                                        pass

                                    reference_value = reference_value.replace(match.group(0), '', 1)
                                    if func is not None:
                                        value = value.replace(match.group(0), func(dest, *args))
                                        print(f"Function mapped: '{match.group(0)}' -> '{value}'")
                                    else:
                                        error(f"ERROR: Unable to map function: {function}")
                                else:
                                    break

                            if key == "COL" or key == "LINE":
                                # file column/line range, special value, just convert to string
                                reference_value = reference_value.replace(value, '')
                                value = f'"{value}"'

                            # Special case, we need to convert DB= to dbtype=
                            if key == "DB":
                                if value == "%DB":
                                    key = "dbtype"
                                    value = '"radar"'
                                    error(f"WARNING: Oracle connectivity is not supported. Use dbtype='radar' with RADAR.")
                                elif value.lower() == "local":
                                    error(f"WARNING: LOCAL DB connectivity is not supported.")
                                else:
                                    error(f"WARNING: DB option unsupported. Use dbtype='radar' with RADAR.")
                            elif key == "TYPE":
                                key = "dbtype"

                            if "TZ" in curline:
                                value = convert_timezone(value)

                            if key != "PICTURE":
                                value = re.sub(r"(?<!')[%$]", '', value)

                            if dest == "": continue
                            if not current_value:
                                print(f"key: {key}; dest: {dest}")
                                if key != f"%{dest.upper()}":
                                    current_value = Value(dest)
                                elif key == f"%{dest.upper()}":
                                    current_value = Value(dest, value)
                                    continue

                            for pkey in pending_variables.keys():
                                current_value[pkey] = pending_variables[pkey]
                            pending_variables = {}

                            if current_value:
                                current_value[key] = value

                    else:
                        # Repgen4 supported using a label in replacement of an entire key=value pair, this might be that
                        if re.match(r'[\^][a-z]', stripped) and current_value:
                            value = re.sub(r"[\^]([a-z])", r"_\1", stripped)
                            value = f'**dict(item.split("=") for item in {value}.split(", "))'
                            current_value.addspecial(value)

                    # Picture format isn't carried over to the next, so save it for later
                    if pending_picture and dest.endswith("TIME") and current_value and 'PICTURE' not in current_value:
                        current_value["PICTURE"] = f'"{pending_picture}"'

                else:
                    # This is most often comments, but can be conditional expressions

                    if in_definition:
                        #print(f"indent_level: {indent_level}")
                        # Convert #IF to python if expression
                        if stripped.upper().startswith("#IF") or stripped.upper().startswith("#ELSEIF"):
                            match = re.match(r"#(ELSE)?IF\s+(.+)", stripped, re.IGNORECASE)
                            if match is not None:
                                cleanup(in_conditional)
                                if not in_conditional and match.group(1):
                                    # This condition usually means a broken report
                                    # Just ignore the conditionals and print the statements as if they weren't there
                                    error(f"WARNING: Unmatched #ELSEIF: {stripped}")
                                    newline = "# REPGEN: Unmatched conditional"
                                else:
                                    in_conditional = True
                                    is_conditional = True
                                    is_elif = False

                                    if match.group(1):
                                        newline = "el"
                                        is_elif = True

                                    newline = newline + f"if {match.group(2)}:"
                                    newline = re.sub(r"=([><])", r"\1=", newline)
                                    newline = re.sub("<>", "!=", newline)
                                    newline = re.sub(r"\s*[^<>!]=[^!<>]\s*", r" == ", newline)

                                    for f in re.findall(r"\b(?<!%)(AND|OR|NOT)\b", newline):
                                        newline = newline.replace(f, f.lower())

                                    # Strip leading '%' from variable names
                                    newline = re.sub('%', '', newline)

                                    # Python doesn't accept leading zeros for numeric literals
                                    newline = re.sub(r'\b0+([0-9]+)\b', r'\1', newline)

                                    # Hack to detect 'KNOWN' function in #IF statement
                                    match = re.search(r"(KNOWN)\s*\(\s*([A-Z0-9_]+)\s*\)", newline, re.IGNORECASE)
                                    if match:
                                        newline = newline.replace(match.group(0), f"{match.group(2)}.{match.group(1).lower()}()", 1)

                                    # Special case indenting for elif
                                    if is_elif:
                                        newline = '\t' * (indent_level - 1) + newline
                                    else:
                                        newline = '\t' * indent_level + newline
                                        indent_level = indent_level + 1

                                    print(f"Converting '{stripped}' -> '{newline}'")
                        elif stripped.upper().startswith("#ELSE"):
                            cleanup(in_conditional)
                            if not in_conditional:
                                # This condition usually means a broken report
                                # Just ignore the conditionals and print the statements as if they weren't there
                                error(f"WARNING: Unmatched #ELSE: {stripped}")
                                newline = "# REPGEN: Unmatched conditional"
                            else:
                                is_conditional = True
                                newline = '\t' * (indent_level - 1) + "else:"
                        elif stripped.upper().startswith("#ENDIF"):
                            cleanup(in_conditional)

                            if not in_conditional:
                                error("WARNING: Found unmatched #ENDIF")

                            indent_level = indent_level - 1
                            if indent_level <= 0:
                                indent_level = 0
                                in_conditional = False

                            newline = '\t' * (indent_level + 1)
                        elif curline == "#ENDDEF":
                            in_definition = False
                            cleanup(in_conditional)
                        else:
                            # Comment
                            if current_value:
                                newline = (newline + "\n" + '\t' * (indent_level) + stripped).strip()
                    else:
                        if curline == "#DEF":
                            in_definition = True
                            if HAS_RELATIVEDELTA: writer.write("# Generated with dateutil.relativedelta support.\n")
                        elif BLOCKQUOTE_FORM:
                            if curline == "#FORM":
                                line = '"""' + line
                            elif curline == "#ENDFORM":
                                line = line + '"""'

                        # If we're in the middle of a value declaration, print the comment immediately, and continue
                        # Comments may end up out of order, but it prevents Value declarations from messing up.
                        writer.write(line + "\n")
                        continue
                        # The code below will fix comment order, but mess up Value declarations with comments inside
                        # is_value_decl = False
                        # value_printed = False
                        # if len(oldline) > 0:
                        #     writer.write(oldline)
                        # if len(newline) > 0:
                        #     writer.write(newline + "\n")
                        # newline = ""
                        # oldline = ""

                #print(f"in_conditional: {in_conditional}; is_conditional: {is_conditional}; line: {newline}")
                if in_conditional and not is_conditional:
                    #cleanup(in_conditional)
                    if newline.strip() != "":
                        newline = "\t" + newline    # Always indent if inside a conditional

                is_conditional = False
                #print(f"found_match: {found_match}; newline: {newline}")

                if current_value:
                    if in_definition and not stripped.startswith('#') and newline != line:
                        oldline = oldline + "#-%s\n" % line
                elif in_definition and newline != "":
                    if SHOW_PREVIOUS: writer.write("#-%s\n" % line)
                    writer.write(newline + "\n")
                    newline = ""
                else:
                    writer.write(line + "\n")

            if newline != "":
                writer.write(newline + "\n")
        print(f"Saving to: {output}")

if __name__ == "__main__":
    input = sys.argv[1]
    output = sys.argv[2]
    main(input, output)
    
# vim: ts=4 sw=4 expandtab
