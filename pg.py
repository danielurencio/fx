import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import matplotlib.pyplot as plt
import gym
from sklearn import preprocessing
from PG_AGENT import agent, discount_rewards
from models.dqn import MarketEnv
from pymongo import MongoClient
from timeParse import timeParser
import sys

token = "e77055f347d78cf98d75dbd2f5db5821-9eeb3a18e4f8484c84fd6f3267c42b26"
restore = False
save = False
model_path = './saved_models/' + sys.argv[1] + '/model_' + sys.argv[1] + '.ckpt'

max_lookback = 24

dates = ('2017-01-23','2017-01-27')
#dates = (sys.argv[2],timeParser(sys.argv[2],4))
dates_ = (timeParser(dates[1],3),timeParser(dates[1],7))
dates_valid = (timeParser(dates[1],10),timeParser(dates[1],14))
print dates_,dates_valid


env = MarketEnv(token,dates,normalization=True,max_lookback=max_lookback)
env_ = MarketEnv(token,dates_,normalization=env,max_lookback=max_lookback)
env__ = MarketEnv(token,dates_valid,normalization=env,max_lookback=max_lookback)

lr = 1e-4

tf.reset_default_graph() #Clear the Tensorflow graph.


myAgent = agent(lr=lr,s_size=env.reset().shape[0],a_size=3,h_size=100)#120) #Load the agent.

total_episodes = 50000000 #Set total number of episodes to train agent on.
max_ep = 999
update_frequency = 10

col_name = "lr_" + str(lr) + "_ma_" + str(env.mas) + "_maxlb_" + str(env.max_lookback) + "_" + str(dates) + "_" + sys.argv[1] 
print col_name
col = MongoClient("mongodb://localhost:27017").PG[col_name]

saver = tf.train.Saver()
init = tf.global_variables_initializer()

# Launch the tensorflow graph
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
#        for j in range(max_ep):
            #Probabilistically pick an action given our network outputs.
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
#	        ep_history[:,2] = np.array([ np.sum( discount_rewards(ep_history[ind:,2]) ) for ind,d in enumerate(ep_history[:,2]) ])
#	        ep_history[:,2] = np.array([ np.sum( ep_history[ind:,2])  for ind,d in enumerate(ep_history[:,2]) ])

                ep_history[:,2] = discount_rewards(ep_history[:,2])
#		ep_history[:,2] = ( ep_history[:,2] - np.mean(ep_history[:,2]) ) / np.std(ep_history[:,2])
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

          test_on = False
	  test_on_ = False
	  s_ = env_.reset()
	  s_ = s_.reshape(1,s_.shape[0],1)

	  s__ = env__.reset()
	  s__ = s__.reshape(1,s__.shape[0],1)
	  test_running_reward = 0
	  valid_running_reward = 0

	  while test_on_ == False:
	    a_dist_ = sess.run(myAgent.output,feed_dict={myAgent.state_in:s_})
	    a_dist__ = sess.run(myAgent.output,feed_dict={myAgent.state_in:s__})
	    a_ = np.argmax(a_dist_)
	    a__ = np.argmax(a_dist__)

#	    a_ = np.random.choice(a_dist_[0],p=a_dist_[0])
#	    a_ = np.argmax(a_dist_ == a_)
#	    a__ = np.random.choice(a_dist__[0],p=a_dist__[0])
#	    a__ = np.argmax(a_dist__ == a__)

	    s1_,r_,test_on = env_.step(a_)
	    s1__,r__,test_on_ = env__.step(a__)

	    s_ = s1_
	    s_ = s_.reshape(1,s_.shape[0],1)
	    s__ = s1__
	    s__ = s__.reshape(1,s__.shape[0],1)

	    test_running_reward += r_
	    valid_running_reward += r__

	  _mean = np.mean(total_reward)
	  _std = np.std(total_reward)
	  _test_mean = np.mean(test_running_reward)
	  _valid_mean = np.mean(valid_running_reward)
	  doc_ = { 'ep':i,'mean':_mean,'std':_std, 'test_mean':_test_mean, 'valid_mean':_valid_mean }
	  print doc_
#	  col.insert_one(doc_)
          total_reward = []
        i += 1
#        if i > int(sys.argv[3]): sys.exit()

