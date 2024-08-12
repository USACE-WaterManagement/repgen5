#FORM
    Tulsa District
    US Army Corps of Engineers
    Keystone Lake Report
DATE            Elevation       Storage     Inflow           Outflow         Precip
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
%DT             %elev	        %stor       %flow_res_in    %flow_res_out    %precip_inc
#ENDFORM

#DEF
PROJECT = "KEYS"
PARAM_TSIDS = [
    "Elev.Inst.1Hour.0.Ccp-Rev",
    "Stor.Inst.1Hour.0.Ccp-Rev",
    "Flow-Res In.Ave.1Hour.1Hour.Rev-Regi-Computed",
    "Flow-Res Out.Ave.1Hour.1Hour.Rev-Regi-Flowgroup",
    "Precip-Inc.Total.1Hour.1Hour.Ccp-Rev",
]

UNIT_MAP = {
    "precip_inc": {"units": "in", "picture": "%3.3f"},
    "flow_res_in": {"units": "cfs", "picture": "%4.0f"},
    "flow_res_out": {"units": "cfs", "picture": "%4.0f"},
    "elev": {"units": "ft", "picture": "%3.2f"},
    "stor": {"units": "ac-ft", "picture": "%5.0f"},
}

PARAM_TSIDS = [p.split(".") for p in PARAM_TSIDS]

BASDATE.value = BASDATE.value.replace(hour=8, minute=0, second=0, microsecond=0)
BASDATE.picture = "%Y-%m-%d"
CUR_YEAR = BASDATE.value.year
CUR_MONTH = BASDATE.value.month
CUR_DAY = BASDATE.value.day

BASDATE_8AM = BASDATE.value.replace(year=2024, month=6, day=21, hour=8, minute=0, second=0, microsecond=0)
BASDATE_8AM_YESTERDAY = BASDATE_8AM - datetime.timedelta(hours=24)

for dbpar, dbptyp, dbint, dbdur, dbver in PARAM_TSIDS:
    print("GET " + '.'.join([PROJECT,dbpar, dbptyp, dbint, dbdur, dbver]))
    # Create a variable friendly name for the parameter
    dbpar_norm = dbpar.replace(" ", "_").replace("-", "_").lower()
    # Dynamically add the project to the locals for printing to the form
    print(UNIT_MAP.get(dbpar_norm, "ft"))
    param = UNIT_MAP.get(dbpar_norm, "ft")
    _value = Value(
        dbtype="radar",
        DBTZ="US/CENTRAL",
        tz="US/CENTRAL",
        DBLOC=PROJECT,
        DBPAR=dbpar,
        DBPTYP=dbptyp,
        DBINT=dbint,
        DBDUR=dbdur,
        DBVER=dbver,
        start=BASDATE_8AM_YESTERDAY,
        end=BASDATE_8AM,
        PICTURE=param["picture"],
        MISSTR="--",
        UNDEF="~~",
        DBUNITS=param["units"],
    )
    print(param)
    print(_value.values)
    locals().update(
        {
            dbpar_norm: _value
        }
    )
    # This will end up being the last elev to get looped. 
    # TODO: Consider creating a sep value for just the date range that should always exist
    print("datatimes", str(_value.values))
    DT = Value(_value.datatimes(),
        PICTURE="%d%b%Y %K%M",
    )


# ENDDEF