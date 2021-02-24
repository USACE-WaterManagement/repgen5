import unittest
from nose2.tools import params
import sys
import datetime
sys.path.append("../")

from . dataset import Dataset,Result
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


def test_simple_sum():
    v1 = Value(1)
    v2 = Value(2)
    v3 = v1+v2
    assert v3.value == 3

def test_multiply():
    stage = Dataset("SimpleStage")    
    assert stage.start != None
    assert stage.end != None
    assert len(stage.values) > 0

    def data():
        data.index += 1
        return stage.values[data.index-1][1]
    data.index = 0
    data.stage = stage

    v1 = Value(dbtype="GENTS", value = data, tz="UTC",start=stage.start,end=stage.end, interval = datetime.timedelta(minutes=15), picture="%0.02f")
    assert len(v1.values) > 0
    
    v2 = v1*2

    result = Result("SimpleStageTimes2")
    assert len(v2.values) > 0
    
    for i in range(len(v2.values)):        
        assert int(v2.values[i][1]) == int(result.values[i])