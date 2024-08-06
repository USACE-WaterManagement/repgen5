#FORM
SPK FLOW for Black Butte
8am to 8am on 2024-06-21
TEST TSID Checks

Day 				Black Butte			Eastman Lake
								Flow Out
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT
%DY                %BB_FLOW_OUT    %EL_FLOW_OUT

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


BB_FLOW_OUT = Value(
	dbtype="radar",
	TSID="Black Butte.Flow-Res Out.Ave.1Hour.1Hour.Calc-val",
	START=BASDATE_8AM_YESTERDAY,
	END=BASDATE_8AM,
	DBUNITS="cfs",
	PICTURE="   %4.0f",
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
