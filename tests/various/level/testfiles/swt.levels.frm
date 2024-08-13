#FORM
Keystone Lake Levels

%TOP_OF_DAM
%TOP_OF_CONSERVATION
%BOTTOM_OF_CONSERVATION

#ENDFORM
#DEF

toc_level =Value(
		dbtype  = "CDA",     
        levelId = "KEYS.Elev.Inst.0.Top of Conservation",
		misstr  = "-M-",
		undef   = "-?-",
		dbunits = "EN",
	)
print(str(toc_level))
#ENDDEF
    