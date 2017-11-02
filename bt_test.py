from backtest.backtest_candles import *
from models.nn import *
import datetime
import sys
from pymongo import MongoClient

col = MongoClient("mongodb://localhost:27017").backtests.EURUSD

token = "104dd2e9ef92e4390fc2c542f7b308c2-1c10699f58f077cb9b4392a74777a7fe"#sys.argv[1]

dates_modelo = ('2017-01-02','2017-02-27')
dates_bt = ('2017-02-27','2017-03-04')
data_modelo = get_candles(dates_modelo,token)
df_modelo = create_df(data_modelo)
modelo = NN()
chromosome = [12*4,3*4,0.002,0.1,1000,5000] # 60,400
modelo.create_model(df_modelo,chromosome)
print modelo.fitness()
print modelo.recall()
print modelo.precision()


data_bt = get_candles(dates_bt,token)

nn = NN()
trade = []
balance = 100
units = 100
tp = 0.0015
sl = 0.0015

backtestObj = {
 'when':datetime.datetime.now().isoformat(),
 "new":7, ## <-- Recuerda !
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
