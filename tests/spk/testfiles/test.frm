#FORM
%mgcElevStat
#ENDFORM

#DEF


BASDATE.value = BASDATE.value.replace(hour=8,minute=0,second=0,microsecond=0)
BASDATE.picture = "%Y-%m-%d"
CUR_YEAR = BASDATE.value.year
CUR_MONTH = BASDATE.value.month
CUR_DAY = BASDATE.value.day

BASDATE_Elev_Pool_Stor = BASDATE.value.replace(hour=8,minute=0,second=0,microsecond=0)

mgcElev=Value(
dbtype="radar",
DBTZ="US/CENTRAL",
tz="US/CENTRAL",
DBLOC="MGCO2",
DBPAR="Elev",
DBPTYP="Inst",
DBINT="1Hour",
DBDUR="0",
DBVER="Ccp-Rev",
start=BASDATE_Elev_Pool_Stor,
end=BASDATE_Elev_Pool_Stor,
PICTURE="%3.2f",
MISSTR="--",
UNDEF="--",
DBUNITS="ft",
)

#ENDDEF