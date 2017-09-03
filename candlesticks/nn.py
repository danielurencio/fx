import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras import initializers
from scipy import stats
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

class NN(object):
  def __init__(self,file_):
    self.data = pd.read_csv(file_)
    self.data.Date_Time = pd.to_datetime(self.data.Date_Time)
    self.data.set_index("Date_Time",inplace=True)

  def scale(self):
    std_scale = preprocessing.StandardScaler().fit(self.X)
    self.X = std_scale.transform(self.X)

  def regParams(self,S):
    x_r = [ index for index,dd in enumerate(S) ]
    y_r = [ dd for index,dd in enumerate(S) ]
    slope, intercept, rvalue, pval, stderr = stats.linregress(x_r,y_r)
    return [slope,intercept,rvalue**2]

  def crossover(self,price,c):
    str1 = "ma_1_" + price
    str2 = "ma_2_" + price
    self.data[str1] = nn.data[price].rolling(c[0]*4).mean()
    self.data[str2] = nn.data[price].rolling(c[1]*4).mean()
    self.data.dropna(inplace=True)

  def shapedObs(self,col,i,x):
    X = self.data[col].values
    X = X.reshape(X.shape[0],1)
    X_ = X[i:(i+x),0]#.tolist()
    return X_

  def create_dataset(self,x,y,t):
    self.crossover('ask_close',(3,12))
    self.crossover('ask_open',(3,12))
    self.crossover('ask_low',(3,12))
    self.crossover('ask_high',(3,12))
    dSize = self.data.shape[0]
    dataX, dataY = [], []
    for i in range(dSize-(x+y)+1):
      dates = self.data.index.values
      dates = dates.reshape(dates.shape[0],1)
      dates = dates[i:(i+x),0]
      dates = pd.to_datetime(dates[dates.shape[0]-1])
      dates = [dates.day,dates.hour,dates.minute]
      ma1_c = self.shapedObs('ma_1_ask_close',i,x).tolist()
      ma2_c = self.shapedObs('ma_2_ask_close',i,x).tolist()
      ma1_o = self.shapedObs('ma_1_ask_open',i,x).tolist()
      ma2_o = self.shapedObs('ma_2_ask_open',i,x).tolist()
      ma1_l = self.shapedObs('ma_1_ask_low',i,x).tolist()
      ma2_l = self.shapedObs('ma_2_ask_low',i,x).tolist()
      ma1_h = self.shapedObs('ma_1_ask_high',i,x).tolist()
      ma2_h = self.shapedObs('ma_2_ask_high',i,x).tolist()
      l = self.data.ask_low.values
      l = l.reshape(l.shape[0],1)
      h = self.data.ask_high.values
      h = h.reshape(h.shape[0],1)
      o_ = self.shapedObs('ask_open',i,x).tolist()
      c = self.shapedObs('ask_close',i,x)
      c_ = c.tolist()
      l_ = l[i:(i+x),0].tolist()
      h_ = h[i:(i+x),0].tolist()
      last = c
      a_ = dates + self.regParams(l_) + self.regParams(h_) + self.regParams(c_) + self.regParams(o_) + self.regParams(ma1_c) + self.regParams(ma2_c) + self.regParams(ma1_o) + self.regParams(ma2_o) + self.regParams(ma1_l) + self.regParams(ma2_l) + self.regParams(ma1_h) + self.regParams(ma2_h)
      lows = l[(i+x):(i+x)+y,0]
      highs = h[(i+x):(i+x)+y,0]
      y_ = [ np.min(lows), np.max(highs) ]
      upCond = ( y_[1] - last[last.shape[0]-1] ) >= t
      downCond = ( last[last.shape[0]-1] - y_[0] ) >= t
      upCond_ = upCond and not downCond
      downCond_ = downCond and not upCond
      neither = (y_[1] - last[last.shape[0]-1] ) < t and ( last[last.shape[0]-1] - y_[0] ) < t
      neither_ = neither or (upCond and downCond)
      if( upCond_ ):
	y_ = [0,0,1]
      if( downCond_ ):
	y_ = [1,0,0]
      if( neither_ ):
	y_ = [0,1,0]
      dataY.append(y_)
      dataX.append(a_)
    self.X = np.array(dataX)
    self.Y = np.array(dataY)

  def train_test(self):
    self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(self.X,self.Y,test_size=0.3)

  def network_class(self):
    self.model = Sequential()
    self.model.add(Dense(90, input_dim = self.X.shape[1], activation='relu',kernel_initializer='glorot_normal'))
    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))
    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))
    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))
#    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))
    self.model.add(Dense(3,activation='softmax',kernel_initializer='glorot_normal'))
    self.model.compile(loss='categorical_crossentropy', optimizer='RMSprop', metrics=['accuracy'])

  def fitness(self):
    p = np.around(nn.model.predict(nn.X_test)).astype(np.int)
    return f1_score(self.Y_test,p,average=None)


if(__name__ == "__main__"):
  nn = NN("EURUSD15Min.csv")
  nn.create_dataset(12*4,3*4,0.0015)
  nn.scale()
  nn.network_class()
  nn.train_test()
#  nn.model.fit(nn.X_train, nn.Y_train, epochs=300, batch_size=400,shuffle=True)
#  nn.fitness()
