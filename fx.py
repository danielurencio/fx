import pymongo
import numpy as np
import pandas as pd

#col = pymongo.MongoClient("mongodb://localhost:27017").fx.EURUSD
obj = { 'db': 'fx', 'collection': 'EURUSD', 'month': 5, 'connection': 'mongodb://localhost:27017', 'year': 2009 }

class FX(object):
    def __init__(self,obj):
	self.conn = obj["connection"]
	self.db = obj["db"]
	self.col = obj["collection"]
	self.cursor = pymongo.MongoClient(self.conn)[self.db][self.col]
	self.year = obj["year"]
	self.month = obj["month"]
	self.df = []

    def Buscar(self):
	projection = { "_id":0, "currency":0 }
	query = { "year":self.year, "month":self.month }
	return self.cursor.find(query,projection)

    def DF(self):
	cursor = self.Buscar()
	columns = []
	for i,d in enumerate(cursor):
	    if( i == 0 ): columns = columns + d.keys()
	    self.df.append(d.values())
	self.df = np.array(self.df)
	self.df = pd.DataFrame(self.df, columns=columns)

    def Bars(self):
	self.DF()
	groupFilter = ["day","hour","minutes"]
	self.closeP = self.df.groupby(groupFilter)["ms"].max().reset_index()
#	self.openP = self.df.groupby(groupFilter)["ms"].min()
#        self.highP = self.df.groupby(groupFilter)["ask"].max() 
#        self.lowP = self.df.groupby(groupFilter)["ask"].min() 
