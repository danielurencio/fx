import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from scipy import stats
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

class NN(object):
  def __init__(self,file_):
    self.data = pd.read_csv(file_)
    self.data.Date_Time = pd.to_datetime(self.data.Date_Time)

  def scale(self):
    std_scale = preprocessing.StandardScaler().fit(self.X)
    self.X = std_scale.transform(self.X)

  def regParams(self,S):
    x_r = [ index for index,dd in enumerate(S) ]
    y_r = [ dd for index,dd in enumerate(S) ]
    slope, intercept, rvalue, pval, stderr = stats.linregress(x_r,y_r)
    return [slope,intercept,rvalue**2]

  def create_dataset(self,x,y,t):
    dSize = self.data.shape[0]
    dataX, dataY = [], []
    for i in range(dSize-(x+y)+1):
      dates = self.data.Date_Time.values
      dates = dates.reshape(dates.shape[0],1)
      dates = dates[i:(i+x),0]
      dates = pd.to_datetime(dates[dates.shape[0]-1])
      dates = [dates.day,dates.hour,dates.minute]
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
      a_ = dates + self.regParams(l_) + self.regParams(h_) + self.regParams(c_) + self.regParams(o_)#+ c_ + l_ + h_
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
    self.X = np.array(dataX)
    self.Y = np.array(dataY)

  def train_test(self):
    self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(self.X,self.Y,test_size=0.3)

  def network(self):
    self.model = Sequential()
    self.model.add(Dense(90, input_dim = self.X.shape[1], activation='relu'))
    self.model.add(Dropout(0))
    self.model.add(Dense(90, activation='relu'))
    self.model.add(Dropout(0))
    self.model.add(Dense(90, activation='relu'))
    self.model.add(Dropout(0))
    self.model.add(Dense(90, activation='relu'))
    self.model.add(Dropout(0))
    self.model.add(Dense(90, activation='relu'))    
    self.model.add(Dropout(0))
#    self.model.add(Dense(80, activation='relu'))
#    self.model.add(Dense(70, activation='relu'))
#    self.model.add(Dense(70, activation='relu'))
    self.model.add(Dense(3,activation='softmax'))
    self.model.compile(loss='categorical_crossentropy', optimizer='RMSprop', metrics=['accuracy'])

  def fitness(self):
    p = np.around(nn.model.predict(nn.X_test)).astype(np.int)
    return f1_score(self.Y_test,p,average=None)


if(__name__ == "__main__"):
  nn = NN("EURUSD15Min.csv")
  nn.create_dataset(12*4,2*4,0.0010)
  nn.scale()
  nn.network()
  nn.train_test()
  #nn.model.fit(nn.X_train, nn.Y_train, epochs=150, batch_size=50,shuffle=True)
