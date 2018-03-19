import json
import tensorflow as tf
import numpy as np
from sklearn import preprocessing
from models.dqn import MarketEnv
from pymongo import MongoClient
from PG_AGENT import agent
import json
import re

class TestAgent:
  def __init__(self,model_name=None,Env=None,Agent=None):
    self.model_name = model_name
    if(self.model_name):
      self.model_path = './saved_models/' + self.model_name + '/model_' + self.model_name + '.ckpt'
    self.env = Env
    self.agent = Agent

  def test(self):
#    env = self.env
    self.env.reset()
    self.env.monto = 100
    self.env.balance = 0
    self.env.trade = []
    trades = []
#    myAgent = self.agent
    init = tf.global_variables_initializer()
    saver = tf.train.Saver()

    with tf.Session() as sess:
      if(self.model_name):
        saver.restore(sess,self.model_path)
      else:
	sess.run(init)

      finished = False

      s = self.env.reset()
      s = s.reshape(1,s.shape[0],1)

      while finished == False:
        a_dist = sess.run(self.agent.output,feed_dict={ self.agent.state_in:s })
        a = np.argmax(a_dist)
        s1,r,finished = self.env.step(a)
        s = s1
        s = s.reshape(1,s.shape[0],1)
        tradeType = str(self.env.trade[0]["type"]) if len(self.env.trade) else None
        doc = { 'time':self.env.Dates()[self.env.count],"balance":self.env.monto,"reward":r,"tradeType":tradeType }
        
        if(len(trades)>0):
          lastDoc = trades[len(trades)-1]
          if(lastDoc["tradeType"] and not doc["tradeType"]):
	    if(lastDoc["tradeType"] == 'buy'):
	      doc['closed'] = "long"
	    else:
	      doc['closed'] = "short"
	trades.append(doc)
	

      total_reward = np.sum(map(lambda x:x["reward"],trades))
      closed = filter(lambda x: x["closed"] if "closed" in x else None, trades)
      longs = filter(lambda x:x["closed"] == "long",closed)
      shorts = filter(lambda x:x["closed"] == "short",closed)

      if(trades[len(trades)-1]["tradeType"] == 'buy'):
	longs.append(trades[len(trades)-1])
      else:
	shorts.append(trades[len(trades)-1])


      result = {}
      result["test_reward"] = total_reward
      result["n_shorts"] = len(shorts)
      result["shorts_reward"] = np.sum(map(lambda x:x["reward"],shorts))
      result["n_longs"] = len(longs) 
      result["longs_reward"] = np.sum(map(lambda x:x["reward"],longs))

      return result
