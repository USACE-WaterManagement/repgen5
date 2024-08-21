#FORM
Keystone Lake Levels

Top of Dam      %TOP_OF_DAM         %TOD_DT
Top of Dam      %TOP_OF_DAM         %TOD_DT
Top of Dam      %TOP_OF_DAM         %TOD_DT
Top of Cons     %TOP_OF_CONSERVATION         %TOC_DT
Bottom of Cons  %BOTTOM_OF_CONSERVATION       %BOC_DT

#ENDFORM
#DEF
TOP_OF_DAM = Value(
    dbtype  = "CDA",     
    misstr  = "-M-",
    undef   = "-?-",
    levelId = "KEYS.Elev.Inst.0.Top of Dam",
    dbunits = "EN",
)

TOP_OF_CONSERVATION =Value(
        levelId = "KEYS.Elev.Inst.0.Top of Conservation",
	)

BOTTOM_OF_CONSERVATION = Value(
    levelId = "KEYS.Elev.Inst.0.Bottom of Conservation",
    picture = "%5.3f",
)
TOD_DT = Value(TOP_OF_DAM.datatimes(),
	PICTURE="%d%b%Y %K%M",
)
TOC_DT = Value(TOP_OF_CONSERVATION.datatimes())
BOC_DT = Value(BOTTOM_OF_CONSERVATION.datatimes())
#ENDDEF
    