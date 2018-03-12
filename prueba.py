import json
import tensorflow as tf
import numpy as np
from sklearn import preprocessing
from models.dqn import MarketEnv
from pymongo import MongoClient
from PG_AGENT import agent

token = "e77055f347d78cf98d75dbd2f5db5821-9eeb3a18e4f8484c84fd6f3267c42b26"
lr = 0
model_name = "a"
model_path = './saved_models/' + model_name + '/model_' + model_name + '.ckpt'
max_lookback = 48
dates = json.load(open('data_2018-01-08_2018-03-09.json'))
#dates = ('2018-01-08','2018-03-09')
#dates = ('2017-07-03','2018-01-05')
env = MarketEnv(token,dates,normalization=True,max_lookback=max_lookback)
myAgent = agent(lr=lr,s_size=env.reset().shape[0],a_size=3,h_size=100)

init = tf.global_variables_initializer()
saver = tf.train.Saver()

with tf.Session() as sess:
  saver.restore(sess,model_path)
  print env.balance
  finished = False

  s = env.reset()
  s = s.reshape(1,s.shape[0],1)

  while finished == False:
    a_dist = sess.run(myAgent.output,feed_dict={ myAgent.state_in:s })
    a = np.argmax(a_dist)
    s1,r,finished = env.step(a)
    s = s1
    s = s.reshape(1,s.shape[0],1)
    print env.Dates()[env.count],env.monto,r
