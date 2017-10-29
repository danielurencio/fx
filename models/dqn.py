from backtest.backtest_candles import get_candles
import numpy as np

class MarketEnv:
  def __init__(self,token,dates):
    self.lookback = 4
    self.token = token
    self.dates = dates
    self.data = self.get_data()
    self.count = 1
    self.balance = 100
    self.units = 100

  def get_data(self):
    data = get_candles(self.dates,self.token)
    candles = np.array(map(lambda x:[x['openAsk'],x['highAsk'],x['closeAsk'],x['lowAsk']],data))
    return self.series(candles)

  def series(self,data):
    series = []
    for i in range(len(data) - (self.lookback-1) ):
      series.append(np.hstack(data[i:i+self.lookback]))
    return np.array(series)

  def reset(self):
    self.count = 1
    return self.data[0]

  def step(self,action=None):
    if(self.count < len(self.data)):
      state = self.data[self.count]
      reward = 0
      done = False
      self.count += 1
    else:
      state = self.data[self.data.shape[0]]
      reward = 0
      done = True
    return state,reward,done
