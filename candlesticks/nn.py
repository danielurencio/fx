import pandas as pd
import numpy as np

class NN(object):
  def __init__(self,file_):
    self.data = pd.read_csv(file_)

  def create_dataset(self,x,y,t):
    dSize = self.data.shape[0]
    dataX, dataY = [], []
    for i in range(dSize-(x+y)+1):
      o = self.data.ask_open.values
      o = o.reshape(o.shape[0],1)
      c = self.data.ask_close.values
      c = c.reshape(c.shape[0],1)
      l = self.data.ask_low.values
      l = l.reshape(l.shape[0],1)
      h = self.data.ask_high.values
      h = h.reshape(h.shape[0],1)
      o_ = o[i:(i+x),0].tolist()
      c_ = c[i:(i+x),0].tolist()
      l_ = l[i:(i+x),0].tolist()
      h_ = h[i:(i+x),0].tolist()
      last = c[i:(i+x),0]
      a_ = o_ + c_ + l_ + h_
      lows = l[(i+x):(i+x)+y,0]
      highs = h[(i+x):(i+x)+y,0]
      y_ = [ np.min(lows), np.max(highs) ]
      upCond = ( y_[1] - last[last.shape[0]-1] ) >= t
      downCond = ( last[last.shape[0]-1] - y_[0] ) >= t
      neither = (y_[1] - last[last.shape[0]-1] ) < t and ( last[last.shape[0]-1] - y_[0] ) < t
#      neither = not upCond and not downCond
      if( upCond ):
	y_ = [0,0,1]
      if( downCond ):
	y_ = [1,0,0]
      if( neither ):
	y_ = [0,1,0]
      dataY.append(y_)
      dataX.append(a_)
    return np.array(dataX), np.array(dataY)


if(__name__ == "__main__"):
  nn = NN("EURUSD15Min.csv")
