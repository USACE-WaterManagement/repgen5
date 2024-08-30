#FORM
%loc
#ENDFORM
#DEF
loc = Value(
    dbtype="radar",
    tsid="KEYS.Elev.Inst.1Hour.0.Ccp-Rev",
    start=BASDATE - datetime.timedelta(hours=24),
    end=BASDATE,
    DBUNITS="ft"
)

print(loc.meta())
#ENDEF