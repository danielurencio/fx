from backtest.backtest_candles import get_candles
from scipy import stats
import numpy as np

class MarketEnv:
  def __init__(self,token,dates):
    self.lookback = 12
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
    a = self.series(candles)
    b = self.series_(candles)
    return np.hstack((a,b))

  def series_(self,data):
    series = []
    for i in range( len(data) - (self.lookback-1) ):
      series.append(np.hstack(data[i:i+self.lookback]))
    return np.array(series)

  def series(self,data):
    series = []
    for i in range( len(data) - (self.lookback - 1) ):
      a = data[i:i+self.lookback]
      b = []
      for j in range(a.shape[1]):
        x_r, y_r = [], []
        for ix,dd in enumerate(a[:,j].tolist()):
          x_r.append(ix)
          y_r.append(dd)
        slope, intercept, rvalue, pval, stderr = stats.linregress(x_r,y_r)
        b.append([slope,intercept,rvalue])
      series.append(np.hstack(b))
    return np.array(series)

  def reset(self):
    self.count = 1
    state = np.append(self.data[0],0)
    return np.append(state,0)

  def step(self,action):
    state = self.State(action)
    if( self.count < len(self.data)-1 ):
      reward = self.reward_signal(state,action)
      if( len(self.trade) == 0 ): # change whether a traded is carried and its balance
	state[state.shape[0]-2] = 0
        state[state.shape[0]-1] = 0
      done = False
      self.count += 1
    else:
      if( len(self.trade) > 0 ):
	if( self.trade[0]["type"] == "sell" ):
	  remainder = self.trade[0]["price"] - self.currentPrice
	elif( self.trade[0]["type"] == "buy" ):
	  remainder = self.currentPrice - self.trade[0]["price"]
	remainder *= self.units
      else:
	remainder = 0
      reward = self.reward_signal(state,action) + remainder
      done = True
    return state,reward,done

  def tradeType(self):
    if(len(self.trade) > 0):
      if(self.trade[0]["type"] == "buy"):
        return 1
      else:
	return -1
    else:
      return 0

  def State(self,action):
    self.previousPrice = self.data[self.count-1][self.data[self.count-1].shape[0]-2]
    self.currentPrice = self.data[self.count][self.data[self.count].shape[0]-2]
    if( len(self.trade) == 0 ):
      if( action == 0 ):
        self.trade.append({ "type":"sell","price":self.previousPrice })
	self.balance = self.trade[0]["price"] - self.currentPrice
      if( action == 2 ):
        self.trade.append({ "type":"buy","price":self.previousPrice })
	self.balance = self.currentPrice - self.trade[0]["price"]
    else:
      if(self.trade[0]['type'] == "sell"):
	self.balance = self.trade[0]["price"] - self.currentPrice
      elif(self.trade[0]['type'] == "buy"):
	self.balance = self.currentPrice - self.trade[0]["price"]
    self.balance *= self.units
    state = np.append(self.data[self.count],self.tradeType())
    return np.append(state,self.balance)

  def reward_signal(self,state,action):
    if( len(self.trade) == 0 ):
      reward = 0
    else:
      if( action == 0 and self.trade[0]['type'] == 'buy'):
	reward = (self.previousPrice - self.trade[0]["price"]) * self.units
	del self.trade[0]
      if( len(self.trade) == 1 ):
        if( action == 0 and self.trade[0]['type'] == 'sell'):
	  reward = 0
      if( action == 1 ):
	reward = 0
      if( action == 2 and self.trade[0]['type'] == 'sell'):
	reward = (self.trade[0]["price"] - self.previousPrice) * self.units
	del self.trade[0]
      if( len(self.trade) == 1 ):
        if( action == 2 and self.trade[0]['type'] == 'buy'):
	  reward = 0
    return reward
