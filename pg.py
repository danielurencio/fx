import json
import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import matplotlib.pyplot as plt
from timeit import default_timer as timer
from sklearn import preprocessing
from PG_AGENT import agent, discount_rewards
from models.dqn import MarketEnv
from testAgent import TestAgent
from pymongo import MongoClient
from timeParse import timeParser
from pprint import pprint
import sys



token = "e77055f347d78cf98d75dbd2f5db5821-9eeb3a18e4f8484c84fd6f3267c42b26"

restore = False
save = True
mongo_save = True

model_name = "a"#sys.argv[1]
model_path = './saved_models/' + model_name + '/model_' + model_name + '.ckpt'

max_lookback = 48

#dates = ('2017-10-02','2018-01-05')
#dates_ = ('2018-01-08','2018-03-09')

dates = json.load(open('data_a.json'))
dates_ = json.load(open('data_b.json'))


env = MarketEnv(token,dates,normalization=True,max_lookback=max_lookback)
env_ = MarketEnv(token,dates_,normalization=env,max_lookback=max_lookback)

lr = 1e-4

tf.reset_default_graph() #Clear the Tensorflow graph.

myAgent = agent(lr=lr,s_size=env.reset().shape[0],a_size=3,h_size=100,stacks=1)

total_episodes = 50000000 #Set total number of episodes to train agent on.
max_ep = 999
update_frequency = 10

__dates = ('2017-10-02','2018-01-05')


col_name = "lr_" + str(lr) + "_ma_" + str(env.mas) + "_maxlb_" + str(env.max_lookback) + "_" + str(__dates) + "_" + model_name 
print col_name
col = MongoClient("mongodb://localhost:27017").PG[col_name]

testAgent = TestAgent(model_name=None,Env=env_,Agent=myAgent)

saver = tf.train.Saver()
init = tf.global_variables_initializer()


with tf.Session() as sess:
    if restore:
      saver.restore(sess,model_path)
    else:
      sess.run(init)

    i = 0
    total_reward = []
    test_total_reward = []
    total_lenght = []
        
    gradBuffer = sess.run(tf.trainable_variables())
    for ix,grad in enumerate(gradBuffer):
        gradBuffer[ix] = grad * 0
        
    while True:
        s = env.reset()
        s = s.reshape(1,s.shape[0],1)
        running_reward = 0
        ep_history = []
        while True:
            a_dist = sess.run(myAgent.output,feed_dict={myAgent.state_in:s})
            a = np.random.choice(a_dist[0],p=a_dist[0])
            a = np.argmax(a_dist == a)
            s1,r,d = env.step(a) #Get our reward for taking an action given a bandit.
            ep_history.append([s,a,r,s1])
            s = s1
            s = s.reshape(1,s.shape[0],1)
            running_reward += r
            if d == True:
                #Update the network.
                ep_history = np.array(ep_history)
	        rewards_onwards = np.array([ np.sum( discount_rewards(ep_history[ind:,2]) ) for ind,d in enumerate(ep_history[:,2]) ])
		ep_history[:,2] = rewards_onwards.reshape(rewards_onwards.shape[0])
#	        ep_history[:,2] = np.array([ np.sum( ep_history[ind:,2])  for ind,d in enumerate(ep_history[:,2]) ])
#                ep_history[:,2] = discount_rewards(ep_history[:,2])

#	        std = 1 if np.std(ep_history[:,2]) == 0 else np.std(ep_history[:,2])
#		ep_history[:,2] = ( ep_history[:,2] - np.mean(ep_history[:,2])  / std)
                feed_dict={myAgent.reward_holder:ep_history[:,2],
                        myAgent.action_holder:ep_history[:,1],myAgent.state_in:np.vstack(ep_history[:,0])}
                grads = sess.run(myAgent.gradients, feed_dict=feed_dict)
                for idx,grad in enumerate(grads):
                    gradBuffer[idx] += grad

                if i % update_frequency == 0 and i != 0:
#########################################################################################################33#
                    for idx,grad in enumerate(grads):
                      gradBuffer[idx] /= update_frequency
#########################################################################################################33#

                    feed_dict =  dict(zip(myAgent.gradient_holders, gradBuffer))
                    _ = sess.run(myAgent.update_batch, feed_dict=feed_dict)
                    for ix,grad in enumerate(gradBuffer):
                        gradBuffer[ix] = grad * 0
                
                total_reward.append(running_reward)
                #total_lenght.append(j)
                break

        
            #Update our running tally of scores.
        if i % 100 == 0 and i != 0:
          if save:
            saver.save(sess,model_path)

	  test_results = testAgent.test()
          _mean = np.mean(total_reward)
	  _std = np.std(total_reward)
          doc_ = { 'ep':i,'mean':_mean,'std':_std, 'test':test_results }
          pprint(doc_)
	  print "\n"
          if mongo_save: col.insert_one(doc_)
          total_reward = []
        i += 1
#        if i > int(7000): sys.exit()



