from pymongo import MongoClient
import numpy as np
import datetime
import dateutil.parser
import matplotlib.pyplot as plt
from pprint import pprint as pp

col = MongoClient("mongodb://localhost:27017").backtests.EURUSD
arr = []

for i in col.find({ 'new':7 }):
  arr.append(i)

a = arr[0]["backtest"]


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

def repulsores_(key,variable,n):
  data = map(lambda x:x[key],variable)
  levels = []
  arr = []
  for i,d in enumerate(data):
    if i > 0:
      a = data[i] - data[i-1]
      arr.append(a)
  count = 0
  while count < n:
    Min_inx = arr.index(min(arr)) + 0
    Min_val = data[Min_inx]
    arr[Min_inx - 0] = 0
    Max_inx = arr.index(max(arr)) + 0
    Max_val = data[Max_inx]
    arr[Max_inx - 0] = 0
    levels.append(Min_val)
    levels.append(Max_val)
    count += 1
  return levels


def levels_(data,n):
##  data = map(lambda x:x[key],variable)
  levels = []
  chunks = np.array_split(np.array(data),n)
  for i in chunks:
    levels.append(np.min(i))
    levels.append(np.max(i))
    levels.append(np.mean(i))
  return levels


def graph_levels(data,levels):
  plt.plot(data,"black")
  for l in levels:
    plt.plot((0,len(data)),(l,l),"red")
  plt.show()


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

def fitnessVSbalance(arr):
  balances = map(lambda x:x["backtest"][len(x["backtest"]) - 1]["balance"],arr)
  balances = np.array(balances)
  fitness = map(lambda x:np.mean(x["fitness"]),arr)
  fitness = np.array(fitness)
  plt.scatter(fitness,balances)
  plt.show()
