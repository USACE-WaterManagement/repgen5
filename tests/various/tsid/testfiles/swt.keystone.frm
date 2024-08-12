#FORM
    KEYSTONE LAKE
    US Army Corps of Engineers
    Elevation, Storage, Flow Out, Precip for 8am to 8am on 2024-06-21
    
DATE	Elevation    Storage    Flow Out       Precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
%DT
        %elev        %stor        %flow_out    %precip
#ENDFORM

#DEF
BASDATE.value = BASDATE.value.replace(hour=8, minute=0, second=0, microsecond=0)
BASDATE.picture = "%Y-%m-%d"
CUR_YEAR = BASDATE.value.year
CUR_MONTH = BASDATE.value.month
CUR_DAY = BASDATE.value.day

BASDATE_8AM = BASDATE.value.replace(year=2024, month=6, day=21, hour=8, minute=0, second=0, microsecond=0)
BASDATE_8AM_YESTERDAY = BASDATE_8AM - datetime.timedelta(hours=24)



# ==============================================================================
#                         Storage
# ==============================================================================
stor = Value(
    dbtype="radar",
    DBTZ="US/CENTRAL",
    tz="US/CENTRAL",
    TSID="KEYS.Stor.Inst.1Hour.0.Ccp-Rev",
    start=BASDATE_8AM_YESTERDAY,
    end=BASDATE_8AM,
    PICTURE="%7.0f",
    MISSTR="--",
    UNDEF="~~",
    DBUNITS="ac-ft",
)
# ==============================================================================
#                         Dates
# ==============================================================================



# # ==============================================================================
# #                         Flow
# # ==============================================================================
flow_out = Value(
    DBPAR="Flow-Res Out",
    DBPTYP="Ave",
    DBINT="1Hour",
    DBDUR="1Hour",
    DBVER="Rev-Regi-Flowgroup",
    PICTURE="%4.0f",
    DBUNITS="cfs"
)

# # ==============================================================================
# #                         Elevation
# # ==============================================================================
elev = Value( 
    PICTURE="%3.2f",
    dbloc="KEYS",
    dbpar="Elev",
    DBPTYP="Inst",
    DBINT="1Hour",
    DBDUR="0",
    DBVER="Ccp-Rev",
    DBUNITS="ft"
)

precip = Value(
    TSID="KEYS.Precip-Inc.Total.1Hour.1Hour.Ccp-Rev",
    PICTURE="%3.3f",
    DBUNITS="in"
)
DT = Value(elev.datatimes(),
    PICTURE = "%d%b%Y %K%M ",
)



# ENDDEF