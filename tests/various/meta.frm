#FORM
=========================================
Location MetaData for %meta.publicName
=========================================
Current Elev Value: %loc

meta.active             %meta.active
meta.boundingOfficeId   %meta.boundingOfficeId
meta.countyName         %meta.countyName
meta.description        %meta.description
meta.elevation          %meta.elevation
meta.horizontalDatum    %meta.horizontalDatum
meta.latitude           %meta.latitude
meta.locationKind       %meta.locationKind
meta.locationType       %meta.locationType
meta.longName           %meta.longName
meta.longitude          %meta.longitude
meta.mapLabel           %meta.mapLabel
meta.name               %meta.name
meta.nation             %meta.nation
meta.nearestCity        %meta.nearestCity
meta.officeId           %meta.officeId
meta.publicName         %meta.publicName
meta.publishedLatitude  %meta.publishedLatitude
meta.publishedLongitude %meta.publishedLongitude
meta.stateInitial       %meta.stateInitial
meta.timezoneName       %meta.timezoneName
meta.verticalDatum      %meta.verticalDatum

=========================================
Location MetaData for %meta2.publicName
=========================================
Current Elev Value: %loc

Now to stress test the ability to import the value anywhere
meta2.active             %meta2.active
meta2.boundingOfficeId   %meta2.boundingOfficeId
meta2.countyName         %meta2.countyName
meta2.description        %meta2.description
meta2.elevation          %meta2.elevation    %meta2.locat%%ionKind
meta2.horizontalDatum    %meta2.horizontalDatum
meta2.latitude           %meta2.latitude %meta2.horizontalDatum
meta2.locationKind   what about some random text    %meta2.locationKind
meta2.locationType       %meta2.locationType
meta2.longName           %meta2.longName
meta2.longitude     or an actual %loc value in the middle?     %meta2.longitude
meta2.mapLabel           %meta2.mapLabel or the end: %loc
meta2.name               %meta2.name
meta2.nation             %meta2.nation a few more %loc %loc
meta2.nearestCity        %meta2.nearestCity
meta2.officeId    %meta2.officeId text here       %meta2.officeIdforgot a space here orhere%meta2.officeId
meta2.%locpublicName         %meta2.publicName
meta2.publ%locishedLatitude  %meta2.publishedLatitude
meta2.publishedLongitude %meta2.publishedLongitude
meta2.stateInitial       %meta2.stateInitial
me%locta2.timezoneName       %meta2.timezoneName
meta2.verticalDatum      %meta2.verticalDatum

#ENDFORM
#DEF
loc = Value(
    dbtype="radar",
    tsid="KEYS.Elev.Inst.1Hour.0.Ccp-Rev",
    start=BASDATE - datetime.timedelta(hours=24),
    end=BASDATE,
    DBUNITS="ft"
)

meta = loc.meta()

loc = Value(
    dbtype="radar",
    tsid="FOSS.Elev.Inst.1Hour.0.Ccp-Rev",
    start=BASDATE - datetime.timedelta(hours=24),
    end=BASDATE,
    DBUNITS="ft"
)

meta2 = loc.meta()

#ENDEF