import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense,Dropout
from keras import initializers
from scipy import stats
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
from datetime import datetime

class NN(object):
  def __init__(self):
    self.data = ""

  def csv(self,file_):
    self.data = pd.read_csv(file_)
    self.data.Date_Time = pd.to_datetime(self.data.Date_Time)
    self.data.set_index("Date_Time",inplace=True)

  def scale(self):
    self.std_scale = preprocessing.StandardScaler().fit(self.X)
    self.X = self.std_scale.transform(self.X)

  def regParams(self,S):
    x_r = [ index for index,dd in enumerate(S) ]
    y_r = [ dd for index,dd in enumerate(S) ]
    slope, intercept, rvalue, pval, stderr = stats.linregress(x_r,y_r)
    return [slope,intercept,rvalue**2]

  def crossover(self,price,c):
    str1 = "ma_1_" + price
    str2 = "ma_2_" + price
    self.data[str1] = self.data[price].rolling(c[0]*4).mean()
    self.data[str2] = self.data[price].rolling(c[1]*4).mean()
    #self.data.dropna(inplace=True)

  def BB_penetration(self,price,length):
    str1 = "BB_" + price
    str2 = "ma_" + price
    self.data[str1] = self.data[price].rolling(length*4).std()
    self.data[str2] = self.data[price].rolling(length*4).mean()
    self.data["up_BB_" + price] = self.data[str2] + 2*self.data[str1]
    self.data["dn_BB_" + price] = self.data[str2] - 2*self.data[str1]
    self.data["up_pn_" + price + "_" + str(length)] = self.data['ask_high'] - self.data["up_BB_"+price]
    self.data["dn_pn_" + price + "_" + str(length)] = self.data['ask_low'] - self.data["dn_BB_"+price]

  def proto_bollinger(self,price,c):
    str1 = "pbol_1_" + price
    str2 = "pbol_2_" + price
    self.data[str1] = self.data[price].rolling(c[0]*4).std()
    self.data[str2] = self.data[price].rolling(c[1]*4).std()
    #self.data.dropna(inplace=True)

  def shapedObs(self,col,i,x):
    X = self.data[col].values
    X = X.reshape(X.shape[0],1)
    X_ = X[i:(i+x),0]#.tolist()
    return X_

  def add_MAS(self):
    self.crossover('ask_close',(3,12))
    self.crossover('ask_open',(3,12))
    self.crossover('ask_low',(3,12))
    self.crossover('ask_high',(3,12))
    self.proto_bollinger('ask_close',(3,12))
    self.proto_bollinger('ask_open',(3,12))
    self.proto_bollinger('ask_high',(3,12))
    self.proto_bollinger('ask_low',(3,12))
    self.BB_penetration('ask_close',12)
    self.BB_penetration('ask_close',3)
    self.data.dropna(inplace=True)

  def create_dataset(self,x,y,t):
    self.add_MAS()
    dSize = self.data.shape[0]
    dataX, dataY = [], []
    l = self.data.ask_low.values
    l = l.reshape(l.shape[0],1)
    h = self.data.ask_high.values
    h = h.reshape(h.shape[0],1)
    for i in range(dSize-(x+y)+1):
      a_,last = self.one_observation(i,x)
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

  def one_observation(self,i,x):
    dates = self.data.index.values
    dates = dates.reshape(dates.shape[0],1)
    dates = dates[i:(i+x),0]
    dates = pd.to_datetime(dates[dates.shape[0]-1])
    dates = [dates.day,dates.hour,dates.minute]
    up_pn_c_12 = self.shapedObs('up_pn_ask_close_12',i,x).tolist()
    dn_pn_c_12 = self.shapedObs('dn_pn_ask_close_12',i,x).tolist()
    up_pn_c_3 = self.shapedObs('up_pn_ask_close_3',i,x).tolist()
    dn_pn_c_3 = self.shapedObs('dn_pn_ask_close_3',i,x).tolist()
    ma1_c = self.shapedObs('ma_1_ask_close',i,x).tolist()
    ma2_c = self.shapedObs('ma_2_ask_close',i,x).tolist()
    ma1_o = self.shapedObs('ma_1_ask_open',i,x).tolist()
    ma2_o = self.shapedObs('ma_2_ask_open',i,x).tolist()
    ma1_l = self.shapedObs('ma_1_ask_low',i,x).tolist()
    ma2_l = self.shapedObs('ma_2_ask_low',i,x).tolist()
    ma1_h = self.shapedObs('ma_1_ask_high',i,x).tolist()
    ma2_h = self.shapedObs('ma_2_ask_high',i,x).tolist()
    pbol1_c = self.shapedObs('pbol_1_ask_close',i,x).tolist()
    pbol2_c = self.shapedObs('pbol_2_ask_close',i,x).tolist()
    pbol1_o = self.shapedObs('pbol_1_ask_open',i,x).tolist()
    pbol2_o = self.shapedObs('pbol_2_ask_open',i,x).tolist()
    pbol1_h = self.shapedObs('pbol_1_ask_high',i,x).tolist()
    pbol2_h = self.shapedObs('pbol_2_ask_high',i,x).tolist()
    pbol1_l = self.shapedObs('pbol_1_ask_low',i,x).tolist()
    pbol2_l = self.shapedObs('pbol_2_ask_low',i,x).tolist()
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
    a_ = dates + self.regParams(l_) + self.regParams(h_) + self.regParams(c_) + self.regParams(o_) + self.regParams(ma1_c) + self.regParams(ma2_c) + self.regParams(ma1_o) + self.regParams(ma2_o) + self.regParams(ma1_l) + self.regParams(ma2_l) + self.regParams(ma1_h) + self.regParams(ma2_h)+ self.regParams(up_pn_c_12) + self.regParams(dn_pn_c_12) + self.regParams(up_pn_c_3) + self.regParams(dn_pn_c_3) + self.regParams(pbol1_c) + self.regParams(pbol2_c) + self.regParams(pbol1_o) + self.regParams(pbol2_o) + self.regParams(pbol1_h) + self.regParams(pbol2_h) + self.regParams(pbol1_l) + self.regParams(pbol2_l)
    return a_,last

  def get_feats(self,x):
    a = np.array(self.one_observation(0,x)[0])
    a = a.reshape(1,a.shape[0])
    return a

  def train_test(self,split_size):
    self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(self.X,self.Y,test_size=split_size)

  def network_class(self):
    self.model = Sequential()
    self.model.add(Dense(90, input_dim = self.X.shape[1], activation='relu',kernel_initializer='glorot_normal'))
    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))
    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))
    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))
    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))
    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))
    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))
    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))

#    self.model.add(Dense(90, activation='relu',kernel_initializer='glorot_normal'))

    self.model.add(Dense(3,activation='softmax',kernel_initializer='glorot_normal'))
    self.model.compile(loss='categorical_crossentropy', optimizer='RMSprop', metrics=['accuracy'])

  def create_model(self,data,chromosome):
    t0 = datetime.now()
    self.data = data
    self.lookback = chromosome[0]
    self.lookforward = chromosome[1]
    self.targeted_pips = chromosome[2]
    self.test_split = chromosome[3]
    self.epochs = chromosome[4]
    self.batch_size = chromosome[5]
    self.create_dataset(self.lookback,self.lookforward,self.targeted_pips)
    self.scale()
    self.network_class()
    self.train_test(self.test_split)
    self.model.fit(self.X_train,self.Y_train,epochs=self.epochs,batch_size=self.batch_size,shuffle=True,verbose=0)
    t1 = datetime.now() - t0
    print "Model trained in:",str(t1)

  def predict(self,data,instance):
    self.data = data
    self.add_MAS()
    observation = self.get_feats(instance.lookback)
    scaled_observation = instance.std_scale.transform(observation)
    prediction = instance.model.predict(scaled_observation)
    prediction = np.around(prediction).astype(np.int)[0]
    return prediction

  def fitness(self):
    p = np.around(self.model.predict(self.X_test)).astype(np.int)
    return f1_score(self.Y_test,p,average=None)

  def precision(self):
    p = np.around(self.model.predict(self.X_test)).astype(np.int)
    return precision_score(self.Y_test,p,average=None)

  def recall(self):
    p = np.around(self.model.predict(self.X_test)).astype(np.int)
    return recall_score(self.Y_test,p,average=None)


if(__name__ == "__main__"):
  nn = NN()
  nn.csv("EURUSD15Min.csv")
  nn.create_dataset(12*4,3*4,0.002)
  nn.scale()
  nn.network_class()
  nn.train_test(0.10)
#  nn.model.fit(nn.X_train, nn.Y_train, epochs=1000, batch_size=5000,shuffle=True)
#  nn.fitness()
