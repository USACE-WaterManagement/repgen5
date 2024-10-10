#FORM
    KEYSTONE LAKE
    US Army Corps of Engineers
    Elevation, Storage, Flow Out, Precip for 8am to 8am on 2024-06-21
    
DATE	 Elevation    Storage   Flow Out       Precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
%DT
        %elevation   %storage  %flow_out      %precip
#ENDFORM

#DEF
BASDATE.value = BASDATE.value.replace(hour=8, minute=0, second=0, microsecond=0)
BASDATE.picture = "%Y-%m-%d"
CUR_YEAR = BASDATE.value.year
CUR_MONTH = BASDATE.value.month
CUR_DAY = BASDATE.value.day

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


# ==============================================================================
#                         Storage
# ==============================================================================
storage = Value(
    dbtype="radar",
    DBTZ="US/CENTRAL",
    tz="US/CENTRAL",
    TSID="KEYS.Stor.Inst.1Hour.0.Ccp-Rev",
    start=BASDATE_8AM_YESTERDAY,
    end=BASDATE_8AM,
    PICTURE="%8.0f",
    MISSTR="--",
    UNDEF="~~",
    DBUNITS="ac-ft",
)
print(storage.values)
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
    # The picture width should match where it fits into the form if you want to keep the alignment
    PICTURE="%9.0f",
    DBUNITS="cfs"
)

# # ==============================================================================
# #                         Elevation
# # ==============================================================================
elevation = Value( 
    PICTURE="%10.2f",
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
    PICTURE="%7.3f",
    DBUNITS="in"
)
DT = Value(elevation.datatimes(),
    PICTURE = "%d%b%Y %K%M ",
)



# ENDDEF
