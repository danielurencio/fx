from backtest.backtest_candles import *
from models.nn import *
import datetime
import sys
from pymongo import MongoClient

col = MongoClient("mongodb://localhost:27017").backtests.EURUSD

token = sys.argv[1]

dates_modelo = ('2017-01-02','2017-02-27')
dates_bt = ('2017-02-27','2017-03-04')
data_modelo = get_candles(dates_modelo,token)
df_modelo = create_df(data_modelo)
modelo = NN()
chromosome = [12*4,4*4,0.003,0.1,2000,5000]
modelo.create_model(df_modelo,chromosome)
print modelo.fitness()
print modelo.recall()
print modelo.precision()


data_bt = get_candles(dates_bt,token)

nn = NN()
trade = []
balance = 100
units = 100
tp = 0.002
sl = 0.003

backtestObj = {
 'when':datetime.datetime.now().isoformat(),
 "new":1,
 'bt_dates': dates_bt,
 'chromosome':chromosome,
 'fitness':modelo.fitness().tolist(),
 'recall':modelo.recall().tolist(),
 'precision':modelo.precision().tolist(),
 'balance':balance, 
 'units':units,
 'tp':tp,
 'sl':sl,
 'backtest':[]
}

for d in data_bt:
  date = dateutil.parser.parse(d["time"])
  candles = get_LastCandles(date,modelo.lookback*2-1,token)
  df_candles = create_df(candles)
  prediction = nn.predict(df_candles,modelo)
  obs = {}
  obs["time"] = d["time"]
  obs["openBid"] = d["openBid"]
  obs["openAsk"] = d["openAsk"]
  obs["prediction"] = prediction.tolist()
  obs["balance"] = balance
  if(len(trade) == 0):
    if(prediction[0] == 1):
      action = "sell"
      trade.append({ "price":d["openBid"], "type":action })
      obs["tradePrice"] = d["openBid"]
      obs["tradeType"] = action
      backtestObj["backtest"].append(obs)
      print action
      print trade[0]
      continue
    if(prediction[1] == 1):
      action = "stay"
    if(prediction[2] == 1):
      action = "buy"
      trade.append({ "price":d["openAsk"], "type":action })
      obs["tradePrice"] = d["openBid"]
      obs["tradeType"] = action
      backtestObj["backtest"].append(obs)
      print action
      print trade[0]
      continue
  if(len(trade) == 1):
    print trade[0]["type"]
    if(trade[0]["type"] == "sell"):
      dif = trade[0]["price"] - d["openAsk"]
      print dif
      print prediction
      if(dif >= tp):
        del trade[0]
        balance += dif*units
        print "closed winning trade"
        continue
      if(dif <= -sl):
        del trade[0]
	balance += dif*units
        print "closed losing trade"
        continue
    if(trade[0]["type"] == "buy"):
      dif = d["openBid"] - trade[0]["price"]
      print dif
      print prediction
      if(dif >= tp):
	del trade[0]
	balance += dif*units
	print "closed winning trade"
        continue
      if(dif <= -sl):
        del trade[0]
	balance += dif*units
        print "closed losing trade"
	continue
  backtestObj["backtest"].append(obs)
  print d['time']
  print "Ask",d['closeAsk']," Bid:",d['closeBid']
  print balance
  print "\n"

col.insert_one(backtestObj)
print "BACKTEST SAVED"
