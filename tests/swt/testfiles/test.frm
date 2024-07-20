#FORM
loc   Elev 8am
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations
%proj %elevations


#ENDFORM

#DEF

PROJECTS = [
"ALTU",
"ARBU",
"ARCA",
"BIGH",
"BIRC",
"BROK",
"CANT",
"CHEN",
"COPA",
"COUN",
"DENI",
"ELDR",
"ELKC",
"EUFA",
"FALL",
"FCOB",
"FGIB",
"FOSS",
"FSUP",
"GSAL",
"HEYB",
"HUDS",
"HUGO",
"HULA",
"JOHN",
"KAWL",
"KEMP",
"KEYS",
"MARI",
"MCGE",
"MERE",
"OOLO",
"PATM",
"PENS",
"PINE",
"SARD",
"SKIA",
"TENK",
"THUN",
"TOMS",
"TORO",
"WAUR",
"WIST"
]
BASDATE.value = BASDATE.value.replace(hour=8,minute=0,second=0,microsecond=0)
BASDATE.picture = "%Y-%m-%d"
CUR_YEAR = BASDATE.value.year
CUR_MONTH = BASDATE.value.month
CUR_DAY = BASDATE.value.day

BASDATE_Elev_Pool_Stor = BASDATE.value.replace(hour=8,minute=0,second=0,microsecond=0)

# elevations = Value()
elevations = Value()
for project in PROJECTS:
    elevations.values.append(Value(
        dbtype="radar",
        DBTZ="US/CENTRAL",
        tz="US/CENTRAL",
        DBLOC=project,
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
        ))


#ENDDEF