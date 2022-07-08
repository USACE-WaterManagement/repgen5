import unittest
import sys
import datetime
sys.path.append("../")


from repgen.data import Value
from repgen.util import TZ

def test_gents_scalar():
    t_end = datetime.datetime.now().replace(minute=0,second=0,microsecond=0,tzinfo=TZ("UTC"))
    t_start = t_end-datetime.timedelta(hours=2)
    v = Value(dbtype="gents",value=2, tz="PST8PDT", start=t_start,end=t_end, interval=datetime.timedelta(minutes=15), picture="%0.02f")
    assert len( v.values ) == 9
    assert v.values[0][1] == 2
    assert v.pop() == "2.00"
    
def test_gents_generator():  
      
    def data():
        data.index+=1
        return data.thedata[data.index-1]
    data.index = 0
    data.thedata = range(9)
    t_end = datetime.datetime.now().replace(minute=0,second=0,microsecond=0,tzinfo=TZ("UTC"))
    t_start = t_end-datetime.timedelta(hours=2)
    v = Value(dbtype="gents",value = data,tz="PST8PDT", start=t_start,end=t_end, interval=datetime.timedelta(minutes=15), picture="%0.02f")
    assert len( v.values ) == 9
    assert v.pop() == "0.00"
    assert v.values[0][1] == 0
    assert v.values[1][1] == 1
    assert v.values[2][1] == 2
    assert v.values[3][1] == 3
    assert v.values[4][1] == 4
    assert v.values[8][1] == 8
