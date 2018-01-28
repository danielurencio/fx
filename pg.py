import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import matplotlib.pyplot as plt
import gym
from sklearn import preprocessing
from PG_AGENT import agent, discount_rewards
from models.dqn import MarketEnv
from pymongo import MongoClient

token = "e77055f347d78cf98d75dbd2f5db5821-9eeb3a18e4f8484c84fd6f3267c42b26"
#env = gym.make("CartPole-v0")
dates = ('2017-01-02','2017-01-27')
env = MarketEnv(token,dates,True)
lr = 1e-4

tf.reset_default_graph() #Clear the Tensorflow graph.

myAgent = agent(lr=lr,s_size=env.data.shape[1]+2,a_size=3,h_size=120) #Load the agent.

total_episodes = 5000 #Set total number of episodes to train agent on.
max_ep = 999
update_frequency = 10

col_name = "lr_" + str(lr) + "_ma_" + str(env.mas) + "_maxlb_" + str(env.max_lookback) + "_" + str(dates) 
print col_name
col = MongoClient("mongodb://localhost:27017").PG[col_name]

init = tf.global_variables_initializer()

# Launch the tensorflow graph
with tf.Session() as sess:
    sess.run(init)
    i = 0
    total_reward = []
    total_lenght = []
        
    gradBuffer = sess.run(tf.trainable_variables())
    for ix,grad in enumerate(gradBuffer):
        gradBuffer[ix] = grad * 0
        
    while True:
        s = env.reset()
        running_reward = 0
        ep_history = []
        for j in range(max_ep):
            #Probabilistically pick an action given our network outputs.
            a_dist = sess.run(myAgent.output,feed_dict={myAgent.state_in:[s]})
	    
            a = np.random.choice(a_dist[0],p=a_dist[0])
            a = np.argmax(a_dist == a)
            s1,r,d = env.step(a) #Get our reward for taking an action given a bandit.
            ep_history.append([s,a,r,s1])
            s = s1
            running_reward += r
            if d == True:
                #Update the network.
                ep_history = np.array(ep_history)
                ep_history[:,2] = discount_rewards(ep_history[:,2])
                feed_dict={myAgent.reward_holder:ep_history[:,2],
                        myAgent.action_holder:ep_history[:,1],myAgent.state_in:np.vstack(ep_history[:,0])}
                grads = sess.run(myAgent.gradients, feed_dict=feed_dict)
                for idx,grad in enumerate(grads):
                    gradBuffer[idx] += grad

                if i % update_frequency == 0 and i != 0:
                    feed_dict =  dict(zip(myAgent.gradient_holders, gradBuffer))
                    _ = sess.run(myAgent.update_batch, feed_dict=feed_dict)
                    for ix,grad in enumerate(gradBuffer):
                        gradBuffer[ix] = grad * 0
                
                total_reward.append(running_reward)
                total_lenght.append(j)
                break

        
            #Update our running tally of scores.
        if i % 100 == 0 and i != 0:
	  d_ = { 'ep':i,'mean':np.mean(total_reward),'std':np.std(total_reward) }
	  print d_
	  col.insert_one(d_)
          #print(i,np.mean(total_reward), np.std(total_reward),len(ep_history))
          total_reward = []
        i += 1

