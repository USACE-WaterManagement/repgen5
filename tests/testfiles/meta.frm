#FORM
%loc
#ENDFORM
#DEF
loc = Value(
    dbtype="radar",
    tsid="KEYS.Elev.Inst.1Hour.0.Ccp-Rev",
    begin=BASDATE - datetime.timedelta(hours=24),
    DBUNITS="ft"
)
#ENDEF