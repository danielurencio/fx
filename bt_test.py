from backtest.backtest_candles import *
from models.nn import *
import datetime
import sys

token = sys.argv[1]

dates_modelo = ('2017-01-02','2017-02-27')
dates_bt = ('2017-02-27','2017-03-04')
data_modelo = get_candles(dates_modelo,token)
df_modelo = create_df(data_modelo)
modelo = NN()
chromosome = [12*4,3*4,0.002,0.1,1000,5000]
modelo.create_model(df_modelo,chromosome)

data_bt = get_candles(dates_bt,token)
#dates_bt = map(lambda x:dateutil.parser.parse(x["time"]),data_bt)

nn = NN()
trade = []
balance = 100


for d in data_bt:
  date = dateutil.parser.parse(d["time"])
  candles = get_LastCandles(date,modelo.lookback*2-1,token)
  df_candles = create_df(candles)
  prediction = nn.predict(df_candles,modelo)
  if(prediction[0] == 1):
    action = "sell"
    if(len(trade) == 0):
      trade.append(d)
      print "pass\n"
      continue
  if(prediction[1] == 1):
    action = "stay"
  if(prediction[2] == 1):
    action = "buy"
  print d['time']
  print "Ask",d['closeAsk']," Bid:",d['closeBid']
  print prediction
  print balance
  print action
  print trade 
  print "\n"
