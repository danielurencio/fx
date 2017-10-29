from backtest.backtest_candles import get_candles
import numpy as np

class MarketEnv:
  def __init__(self,token,dates):
    self.lookback = 9
    self.token = token
    self.dates = dates
    self.data = self.get_data()
    self.count = 1
    self.balance = 100
    self.units = 100
    self.trade = []

  def get_data(self):
    data = get_candles(self.dates,self.token)
    fn = lambda x:[x['openAsk'],x['highAsk'],x['closeAsk'],x['lowAsk']]
    candles = np.array(map(fn,data))
    return self.series(candles)

  def series(self,data):
    series = []
    for i in range( len(data) - (self.lookback-1) ):
      series.append(np.hstack(data[i:i+self.lookback]))
    return np.array(series)

  def reset(self):
    self.count = 1
    return np.append(self.data[0],0)

  def step(self,action):
    if( self.count < len(self.data) ):
      state = np.append(self.data[self.count],len(self.trade))
      reward = self.reward_signal(state,action)
      done = False
      self.count += 1
    else:
      state = self.data[self.data.shape[0]-1]
      reward = self.reward_signal(state,action)
      done = True
    return state,reward,done

  def reward_signal(self,state,action):
    close_price = state[state.shape[0]-3]
    if( len(self.trade) == 0 ):
      if( action == 0 ):
        self.trade.append({ "type":"sell","price":close_price })
      if( action == 2 ):
        self.trade.append({ "type":"buy","price":close_price })
      reward = 0
    else:
      if( action == 0 and self.trade[0]['type'] == 'buy'):
	reward = (self.trade[0]["price"] - close_price) * self.units
	del self.trade[0]
      if( len(self.trade) == 1 ):
        if( action == 0 and self.trade[0]['type'] == 'sell'):
	  reward = 0
      if( action == 1 ):
	reward = 0
      if( action == 2 and self.trade[0]['type'] == 'sell'):
	reward = (close_price - self.trade[0]["price"]) * self.units
	del self.trade[0]
      if( len(self.trade) == 1 ):
        if( action == 2 and self.trade[0]['type'] == 'buy'):
	  reward = 0
    return reward
