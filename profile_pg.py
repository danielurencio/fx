import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import matplotlib.pyplot as plt
from timeit import default_timer as timer
from sklearn import preprocessing
from PG_AGENT import agent, discount_rewards
from models.dqn import MarketEnv
from pymongo import MongoClient
from timeParse import timeParser
import json


token = ''

max_lookback = 48
dates = json.load(open('data_2017-07-03_2018-01-05.json'))
env = MarketEnv(token,dates,normalization=True,max_lookback=max_lookback)
lr = 1e-5

tf.reset_default_graph() #Clear the Tensorflow graph.

myAgent = agent(lr=lr,s_size=env.reset().shape[0],a_size=3,h_size=100)#120) #Load the agent.
col_name = "profiler"
print col_name
col = MongoClient("mongodb://localhost:27017").PG[col_name]

init = tf.global_variables_initializer()


with tf.Session() as sess:
    sess.run(init)

    while True:
        CUT_A = timer()
        s = env.reset()
        s = s.reshape(1,s.shape[0],1)
        running_reward = 0
        ep_history = []
        while True:
#        for j in range(max_ep):
            a_dist = sess.run(myAgent.output,feed_dict={myAgent.state_in:s})
            a = np.random.choice(a_dist[0],p=a_dist[0])
            a = np.argmax(a_dist == a)
            s1,r,d = env.step(1)
            ep_history.append([s,a,r,s1])
            s = s1
            s = s.reshape(1,s.shape[0],1)
            running_reward += r
            if d == True:
                CUT_B = timer()
                print CUT_B - CUT_A
		break
