import json
import numpy as np
from models.dqn import MarketEnv
from pymongo import MongoClient
from PG_AGENT import agent
from testAgent import TestAgent

token = "e77055f347d78cf98d75dbd2f5db5821-9eeb3a18e4f8484c84fd6f3267c42b26"
lr = 0
model_name = "a"
model_path = './saved_models/' + model_name + '/model_' + model_name + '.ckpt'
max_lookback = 48
dates = ('2018-01-08','2018-03-09')

env = MarketEnv(token,dates,normalization=True,max_lookback=max_lookback)
myAgent = agent(lr=lr,s_size=env.reset().shape[0],a_size=3,h_size=100,stacks=1)

testAgent = TestAgent(model_name=None,Env=env,Agent=myAgent)
test = testAgent.test()
print test
