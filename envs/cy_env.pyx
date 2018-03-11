from backtest.backtest_candles import get_candles
from scipy import stats
from dateutil import parser
from sklearn import preprocessing
from crypto import crypto
import numpy as np
cimport numpy as cnp

cdef class MarketEnv:

  def __init__(self,token,dates,normalization,max_lookback=24):
    self.mas = [8,24]
    self.lookback = None
    self.max_lookback = max_lookback
    self.token = token
    self.dates = dates
    self.normalization = normalization
    self.data = self.MA_state()#self.get_data()
    self.hours_ = self.Hours()
    self.closing_prices = self.closingPrices()
    self.count = 1
    self.balance = 100
    self.units = self.balance * 1
    self.trade = []

  def get_data(self):
    data = get_candles(self.dates,self.token)
#    fn = lambda x:[x['openAsk'],x['highAsk'],x['closeAsk'],x['lowAsk']]#,parser.parse(x['time']).hour]
    fn = lambda x:x['closeAsk']
    self.hours = np.array(map(lambda x:parser.parse(x['time']).hour,data))
    self.candles = np.vstack(np.array(map(fn,data)))
#    a = self.series(candles)
#    b = self.series_(candles)
#    return np.hstack((a,b))

  def Hours(self):
    dif = self.hours.shape[0] - self.data.shape[0]
    return self.hours[dif:]

  def closingPrices(self):
    dif = self.candles.shape[0] - self.data.shape[0]
    return self.candles[dif:]

  def series_(self,data):
    series = []
    for i in range( len(data) - (self.lookback-1) ):
      series.append(np.hstack(data[i:i+self.lookback]))
    return np.array(series)

  def moving_averages(self):
    self.get_data()
#    self.candles = crypto.candles(self.dates)
    _series = []
    for ma in self.mas:
      lowerBound = ma - min(self.mas)
      self.lookback = ma
      serie = self.series_(self.candles[:,0])
      serie = map(lambda x:np.mean(x),serie)
      serie = np.vstack(serie)
      _series.append(serie)
    lengths = map(lambda x:x.shape[0],_series)
    difs = map(lambda x: x - min(lengths),lengths)
    for i,d in enumerate(_series):
      _series[i] = _series[i][difs[i]:,]
    self.computed_movingAverages = np.hstack(_series) 

  def MA_state(self):
    self.moving_averages()
    self.lookback = self.max_lookback
    lowerBound = self.candles.shape[0] - self.computed_movingAverages.shape[0]
    data = self.candles[lowerBound:,:]
    data = np.hstack([data,self.computed_movingAverages])
#############################################################33333
    a = np.vstack(data[:,0] - data[:,1])
    b = np.vstack(data[:,0] - data[:,2])
    c = np.vstack(data[:,1] - data[:,2])
    data = np.hstack([a,b,c])
#############################################################33333
    arr = []
    for i in xrange(data.shape[1]):
      arr.append(self.series_(data[:,i]))
    data = np.hstack(arr)
#    self.closingPriceIndex = (1 * self.max_lookback) - 1
    if self.normalization == True: # ---------------------------------------------   normalization fix
      self.scaler = preprocessing.StandardScaler().fit(data)
      data = self.scaler.transform(data)
    elif isinstance(self.normalization,MarketEnv) == True:
      data = self.normalization.scaler.transform(data)
    return data

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
#    cdef cnp.ndarray state
#    cdef float reward
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
#    cdef cnp.ndarray state
#    self.previousPrice = self.data[self.count-1][self.closingPriceIndex]
#    self.currentPrice = self.data[self.count][self.closingPriceIndex]
#    print self.previousPrice,self.currentPrice
    self.previousPrice = self.closing_prices[self.count-1]
    self.currentPrice = self.closing_prices[self.count]
#    print self.previousPrice,self.currentPrice
#    if self.normalization == True: # -----------------------------------     normalization fix
#      temp_data = self.scaler.inverse_transform(self.data)
#      self.previousPrice = temp_data[self.count-1][self.closingPriceIndex]
#      self.currentPrice = temp_data[self.count][self.closingPriceIndex]
#    elif isinstance(self.normalization,MarketEnv) == True:
#      temp_data = self.normalization.scaler.inverse_transform(self.data)
#      self.previousPrice = temp_data[self.count-1][self.closingPriceIndex]
#      self.currentPrice = temp_data[self.count][self.closingPriceIndex]
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
    state = np.append(state,self.balance)
    return state

  def reward_signal(self,state,action):
#    cdef float reward
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
