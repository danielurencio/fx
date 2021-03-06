import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import matplotlib.pyplot as plt

def discount_rewards(r):
    gamma = 0.99
    """ take 1D float array of rewards and compute discounted reward """
    discounted_r = np.zeros_like(r)
    running_add = 0
    for t in reversed(xrange(0, r.size)):
        running_add = running_add * gamma + r[t]
        discounted_r[t] = running_add
    return discounted_r


class agent():
    def __init__(self, lr, s_size,a_size,h_size,stacks=1):
        #These lines established the feed-forward part of the network. The agent takes a state and produces an action.
        _seqlens = tf.placeholder(tf.float32,shape=[s_size])
        self.state_in= tf.placeholder(shape=[None,s_size,1],dtype=tf.float32)

	def lstm_cell_():
	  return tf.contrib.rnn.BasicLSTMCell(h_size)

	if(stacks == 1):
	  lstm_cell = tf.contrib.rnn.BasicLSTMCell(h_size)
	else:
          lstm_cell = tf.contrib.rnn.MultiRNNCell([lstm_cell_() for cell in range(stacks)])

	outputs,states = tf.nn.dynamic_rnn(lstm_cell,self.state_in,dtype=tf.float32)
	outputs = tf.transpose(outputs,[1,0,2])
	last = tf.gather(outputs,int(outputs.get_shape()[0])-1)
        self.output = slim.fully_connected(last,a_size,activation_fn=tf.nn.softmax,biases_initializer=None)
        self.chosen_action = tf.argmax(self.output,1)

        #The next six lines establish the training proceedure. We feed the reward and chosen action into the network
        #to compute the loss, and use it to update the network.
        self.reward_holder = tf.placeholder(shape=[None],dtype=tf.float32)
        self.action_holder = tf.placeholder(shape=[None],dtype=tf.int32)
        
        self.indexes = tf.range(0, tf.shape(self.output)[0]) * tf.shape(self.output)[1] + self.action_holder
        self.responsible_outputs = tf.gather(tf.reshape(self.output, [-1]), self.indexes)

#        self.loss = -tf.reduce_mean(tf.log(self.responsible_outputs)*(self.reward_holder)) #- tf.reduce_mean(self.reward_holder)))
        self.loss = -tf.reduce_mean(tf.log(self.responsible_outputs)*(self.reward_holder - tf.reduce_mean(self.reward_holder)))
        
        tvars = tf.trainable_variables()
        self.gradient_holders = []
        for idx,var in enumerate(tvars):
            placeholder = tf.placeholder(tf.float32,name=str(idx)+'_holder')
            self.gradient_holders.append(placeholder)
        
        self.gradients = tf.gradients(self.loss,tvars)
        
        optimizer = tf.train.RMSPropOptimizer(learning_rate=lr)
        #optimizer = tf.train.AdamOptimizer(learning_rate=lr)
        self.update_batch = optimizer.apply_gradients(zip(self.gradient_holders,tvars))



