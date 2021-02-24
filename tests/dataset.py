import datetime
# simple timeseries data set to load in from disk
class Dataset:
    

    def __init__(self, set_name):
        self.values = []
        self.start = None
        self.end = None
        self.index = 0
        with open("tests/datasets/Set_%s.csv"%set_name,"r") as results:
            for line in results.readlines():                
                date,val,qual = line.strip().split(",")
                _d = datetime.datetime.fromisoformat(date)
                if self.start == None:
                    self.start = _d
                self.values.append( (_d,float(val),int(qual)))
                self.end = _d

    def values_all(self):
        self.index = self.index + 1
        return self.values[self.index-1]
            
    
    def values_only(self):
        self.index = self.index + 1
        return self.values[self.index-1][1]

class Result:    
    def __init__(self, result_set_name):
        self.values = []
        with open("tests/datasets/Result_%s.res" %result_set_name,"r") as results:
            for value in results.readlines():
                self.values.append( float(value) )
