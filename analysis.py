from pymongo import MongoClient
import numpy as np
import datetime
import dateutil.parser
import matplotlib.pyplot as plt
from pprint import pprint as pp

col = MongoClient("mongodb://localhost:27017").backtests.EURUSD
arr = []

for i in col.find({ 'new':1 }):
  arr.append(i)

a = arr[0]["backtest"]

#time = np.array(map(lambda x:dateutil.parser.parse(x["time"]),a))
#ask = np.array(map(lambda x:x["openAsk"],a))
#bid = np.array(map(lambda x:x["openBid"],a))

#trades = filter(lambda x:x["tradeType"] if "tradeType" in x else None,a)
#sell = filter(lambda x:x["tradeType"] == "sell", trades)
#buy = filter(lambda x:x["tradeType"] == "buy", trades)

#buy_time = np.array(map(lambda x:dateutil.parser.parse(x["time"]),buy))
#sell_time = np.array(map(lambda x:dateutil.parser.parse(x["time"]),sell))

#buy_prices = np.array(map(lambda x:x["tradePrice"],buy))
#sell_prices = np.array(map(lambda x:x["tradePrice"],sell))


def values_(key,variable):
  values = np.array(map(lambda x:x[key],variable))
  return values

def time_(key_time,variable):
  values = np.array(map(lambda x:dateutil.parser.parse(x[key_time]),variable))
  return values

def trades_(keys,variable,f):
   trades = filter(lambda x:x["tradeType"] if "tradeType" in x else None,variable)
   trade_type = filter(lambda x:x["tradeType"] == keys[0],trades)
   return f(keys[1],trade_type)


def graph_(a,values_,time_,trades_): 
  time, ask, bid, balance = time_('time',a), values_('openAsk',a), values_('openBid',a), values_('balance',a)
  sell_prices, sell_time = trades_(('sell','tradePrice'),a,values_), trades_(('sell','time'),a,time_)
  buy_prices, buy_time = trades_(('buy','tradePrice'),a,values_), trades_(('buy','time'),a,time_)
  fig,ax1 =plt.subplots()
  ax2 = ax1.twinx()
  ax1.plot(time,ask,c='gray')
  ax1.scatter(buy_time,buy_prices,c='green',s=60,lw=0)
  ax1.scatter(sell_time,sell_prices,c='red',s=60,lw=0)
  ax1.set_ylabel("Price")
  ax2.set_ylabel("Balance")
  ax2.plot(time,balance)
  plt.show()
