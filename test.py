import numpy as np
from backtest.backtest_candles import get_candles
from models.dqn import MarketEnv

token = "e77055f347d78cf98d75dbd2f5db5821-9eeb3a18e4f8484c84fd6f3267c42b26"
dates = ('2017-01-02','2017-01-27')

env = MarketEnv(token,dates,True)

data = get_candles(dates,token)
fn = lambda x:[x['openAsk'],x['highAsk'],x['closeAsk'],x['lowAsk']]
candles = np.array(map(fn,data))

def series_(data,lookback):
  series = []
  for i in range( len(data) - (lookback-1) ):
    series.append(np.hstack(data[i:i+lookback]))
  return np.array(series)

 
