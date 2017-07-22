import pymongo
import numpy as np
import pandas as pd

#col = pymongo.MongoClient("mongodb://localhost:27017").fx.EURUSD
obj = { 'db': 'fx', 'collection': 'EURUSD', 'month': 5, 'connection': 'mongodb://localhost:27017', 'year': 2009, 'day': 1 }

class FX(object):
    def __init__(self,obj):
	self.connection = obj["connection"]
	self.db = obj["db"]
	self.collection = obj["collection"]
	self.cursor = pymongo.MongoClient(self.connection)[self.db][self.collection]
	self.year = obj["year"]
	self.month = obj["month"]
	self.day = obj["day"]
	self.df = []

    def Buscar(self):
	projection = { "_id":0, "currency":0 }
	query = { "year":self.year, "month":self.month, "day":self.day }
	return self.cursor.find(query,projection)

    def DF(self):
	cursor = self.Buscar()
	columns = []
	for i,d in enumerate(cursor):
	    if( i == 0 ): columns = columns + d.keys()
	    self.df.append(d.values())
	self.df = np.array(self.df)
	self.df = pd.DataFrame(self.df, columns=columns)
