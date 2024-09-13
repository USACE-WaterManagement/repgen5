#FORM
SPK FLOW for Black Butte
8am to 8am on 2024-06-21
TEST TSID Checks

Day                  Black Butte        Eastman Lake
                                Flow Out
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT
%DY %BB_FLOW_OUT     %EL_FLOW_OUT

#ENDFORM
# Generated with dateutil.relativedelta support.
#DEF
# !ECHO
#
UNDEF="????"
#
#     Force the %BASDATE to a midnight value, so that TIME= does not have to be
#     specified on the command line.
#
BASDATE.value = BASDATE.value.replace(hour=0,minute=0,second=0,microsecond=0)
#
CURDATE.undef = "????"
Value.shared["undef"] = "????"
CURDATE.picture = "%d %b %Y @ %K%M"
Value.shared["picture"] = "%d %b %Y @ %K%M"


BASDATE_8AM = BASDATE.value.replace(year=2024, month=6, day=21, hour=8, minute=0, second=0, microsecond=0)
BASDATE_8AM_YESTERDAY = BASDATE_8AM - datetime.timedelta(hours=24)


# FORMAT NOTES
# The %variables in the form definition are replaced with the contents,
# filling the same space the variable name took up.
# To avoid alignment issues, make sure your output fits within the length of the name (including %).
# For example:

# Datetime       Elevation  Storage
# %DT            %elev      %storage

# would be replaced to give you the following:

# Datetime       Elevation  Storage
# 20Jun2024 0800       724.73      429926

# However, if you want to keep columns aligned with headers, do this:
# Datetime       Elevation  Storage
# %DATE_TIME_VAL%elevation %storageage

# Combined with the appropriate PICTURE, you can fill the wider space with smaller width data
# Datetime       Elevation  Storage
# 20Jun2024 0800    724.73   429926

# An alternative, as used in this form, 
# is to remove the extra spaces that aren't needed inbetween the variable data,
# then let the replacement expand the line as it fills in the data.

# For example:
# Day                  Black Butte        Eastman Lake
#                                 Flow Out
# %DY %BB_FLOW_OUT     %EL_FLOW_OUT

# The large gap of spaces after the %DY reference is not present,
# and the line will expand when the datetime is substituted.
# This is useful for constant-width fields, like dates.

BB_FLOW_OUT = Value(
	dbtype="radar",
	TZ="America/Los_Angeles",
	TSID="Black Butte.Flow-Res Out.Ave.1Hour.1Hour.Calc-val",
	START=BASDATE_8AM_YESTERDAY,
	END=BASDATE_8AM,
	DBUNITS="cfs",
	PICTURE="   %12.0f",
	UNDEF="      cfs",
	MISSTR="      cfs",
)

EL_FLOW_OUT = Value(
    DBLOC="Eastman Lake"
)

DY = Value(EL_FLOW_OUT.datatimes(),
	PICTURE="%d/%b/%Y %K%M",
	UNDEF="   X",
	MISSTR="   X",
)
#
#
#ENDDEF
