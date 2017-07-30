import sys
import pymongo
import numpy as np
import pandas as pd


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

    def Bars_1(self):
	self.DF()
	groupFilter1 = ["day","hour","minutes","seconds"]
        groupFilter2 = ["day","hour","minutes"]
        groupFilter3 = ["year","month"] + groupFilter2
        filterByms = self.df.groupby(groupFilter1)["ms"]
	A_close = filterByms.max().reset_index()
	A_open = filterByms.min().reset_index()
	B_close = A_close.groupby(groupFilter2)['seconds'].max().reset_index()
	B_open = A_open.groupby(groupFilter2)['seconds'].min().reset_index()
	C_close = pd.merge(B_close,A_close)
        C_open = pd.merge(B_open,A_open)
        dropCols = ['seconds','ms']
	closeP = pd.merge(C_close,self.df).drop(dropCols,1)
	openP = pd.merge(C_open,self.df).drop(dropCols,1)
	closeP.rename(columns={'bid':'close_bid','ask':'close_ask'},inplace=True)
	openP.rename(columns={'bid':'open_bid','ask':'open_ask'},inplace=True)
        ask = self.df.groupby(groupFilter3)["ask"]
        bid = self.df.groupby(groupFilter3)["bid"]
        high_ask = ask.max().reset_index()
	high_bid = bid.max().reset_index()
        low_ask = ask.min().reset_index()
	low_bid = bid.min().reset_index()
	high = pd.merge(high_ask,high_bid).rename(columns={'bid':'high_bid','ask':'high_ask'})
	low = pd.merge(low_ask,low_bid).rename(columns={'bid':'low_bid','ask':'low_ask'})
	high_low = pd.merge(high,low);
	open_close = pd.merge(openP,closeP);
	self.bars_1 = pd.merge(open_close,high_low)

    def Bars_1_toCSV(self):
	self.Bars_1()
        file_n = self.col + '_' + str(self.year) + '_' + str(self.month)
        self.file_1m = file_n + '_1m.csv'
	self.bars_1.to_csv(file_n + '_1m.csv',index=False);


if(__name__ == "__main__"):
    obj = {
      'db': 'fx',
      'collection': sys.argv[1],
      'month': int(sys.argv[3]),
      'connection': 'mongodb://localhost:27017',
      'year': int(sys.argv[2])
    }
    parity = FX(obj)
    parity.Bars_1_toCSV()
    print(parity.file_1m)
