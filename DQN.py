from pymongo import MongoClient
from models.dqn import MarketEnv
import random, numpy, math, gym, sys
from keras import backend as K
from keras.models import Sequential
from keras.layers import *
from keras.optimizers import *
from sklearn import preprocessing
import tensorflow as tf

col = MongoClient("mongodb://localhost:27017").backtests.EURUSD

#----------
HUBER_LOSS_DELTA = 1
LEARNING_RATE = 0.00025
MEMORY_CAPACITY = 100000
BATCH_SIZE = 50
GAMMA = 0.99
MAX_EPSILON = 1
MIN_EPSILON = 0.01
LAMBDA = 0.001      # speed of decay
UPDATE_TARGET_FREQUENCY = 1000


#----------
def huber_loss(y_true, y_pred):
    err = y_true - y_pred

    cond = K.abs(err) < HUBER_LOSS_DELTA
    L2 = 0.5 * K.square(err)
    L1 = HUBER_LOSS_DELTA * (K.abs(err) - 0.5 * HUBER_LOSS_DELTA)

    loss = tf.where(cond, L2, L1)   # Keras does not cover where function in tensorflow :-(

    return K.mean(loss)

#-------------------- BRAIN ---------------------------

class Brain:
    def __init__(self, stateCnt, actionCnt):
        self.stateCnt = stateCnt
        self.actionCnt = actionCnt

        self.model = self._createModel()
	#self.model.load_weights("weights.h5")
        self.model_ = self._createModel() 
	#self.model_.load_weights("weights.h5")

    def _createModel(self):
        model = Sequential()

        model.add(Dense(300, activation='relu', input_dim=stateCnt))
        model.add(Dense(300, activation='relu'))
        model.add(Dense(300, activation='relu'))
        model.add(Dense(actionCnt, activation='linear'))

        opt = RMSprop(lr=LEARNING_RATE)
        model.compile(loss=huber_loss, optimizer=opt)

        return model

    def train(self, x, y, epochs=1, verbose=0):
        std_scale = preprocessing.StandardScaler().fit(x)
        X = std_scale.transform(x)
        self.model.fit(X, y, batch_size=BATCH_SIZE, epochs=epochs, verbose=verbose)

    def predict(self, s, target=False):
        if target:
            return self.model_.predict(s)
        else:
            return self.model.predict(s)

    def predictOne(self, s, target=False):
        return self.predict(s.reshape(1, self.stateCnt), target=target).flatten()

    def updateTargetModel(self):
        self.model_.set_weights(self.model.get_weights())

#-------------------- MEMORY --------------------------
class Memory:   # stored as ( s, a, r, s_ )
    samples = []

    def __init__(self, capacity):
        self.capacity = capacity

    def add(self, sample):
        self.samples.append(sample)        

        if len(self.samples) > self.capacity:
            self.samples.pop(0)

    def sample(self, n):
        n = min(n, len(self.samples))
        return random.sample(self.samples, n)

    def isFull(self):
        return len(self.samples) >= self.capacity

#-------------------- AGENT ---------------------------

class Agent:
    steps = 0
    epsilon = MAX_EPSILON

    def __init__(self, stateCnt, actionCnt):
        self.stateCnt = stateCnt
        self.actionCnt = actionCnt

        self.brain = Brain(stateCnt, actionCnt)
        self.memory = Memory(MEMORY_CAPACITY)
        
    def act(self, s):
        if random.random() < self.epsilon:
            return random.randint(0, self.actionCnt-1)
        else:
            return numpy.argmax(self.brain.predictOne(s))

    def observe(self, sample):  # in (s, a, r, s_) format
        self.memory.add(sample)        

        if self.steps % UPDATE_TARGET_FREQUENCY == 0:
            self.brain.updateTargetModel()

        # debug the Q function in poin S
#        if self.steps % 100 == 0:
#            S = numpy.array([-0.01335408, -0.04600273, -0.00677248, 0.01517507])
#            pred = self.brain.predictOne(S)
#            print(pred[0])
#            sys.stdout.flush()

        # slowly decrease Epsilon based on our eperience
        self.steps += 1
        self.epsilon = MIN_EPSILON + (MAX_EPSILON - MIN_EPSILON) * math.exp(-LAMBDA * self.steps)

    def replay(self):    
        batch = self.memory.sample(BATCH_SIZE)
        batchLen = len(batch)

        no_state = numpy.zeros(self.stateCnt)

        states = numpy.array([ o[0] for o in batch ])
        states_ = numpy.array([ (no_state if o[3] is None else o[3]) for o in batch ])

        p = agent.brain.predict(states)
        p_ = agent.brain.predict(states_, target=True)

        x = numpy.zeros((batchLen, self.stateCnt))
        y = numpy.zeros((batchLen, self.actionCnt))
        
        for i in range(batchLen):
            o = batch[i]
            s = o[0]; a = o[1]; r = o[2]; s_ = o[3]
            
            t = p[i]
            if s_ is None:
                t[a] = r
            else:
                t[a] = r + GAMMA * numpy.amax(p_[i])

            x[i] = s
            y[i] = t

        self.brain.train(x, y)


class RandomAgent:
    memory = Memory(MEMORY_CAPACITY)

    def __init__(self, actionCnt):
        self.actionCnt = actionCnt

    def act(self, s):
        return random.randint(0, self.actionCnt-1)

    def observe(self, sample):  # in (s, a, r, s_) format
        self.memory.add(sample)

    def replay(self):
        pass

#-------------------- ENVIRONMENT ---------------------
class Environment:
    def run(self, aagent,market_env,episode):
        s = market_env.reset()
        R = 0 

        while True:            
            # self.env.render()

            a = aagent.act(s)

            s_, r, done = market_env.step(a)

            if done: # terminal state
                s_ = None

            aagent.observe( (s, a, r, s_) )
            aagent.replay()            

            s = s_
            R += r

            if done:
                break

	col.insert_one({ "R":R, "episode":episode })
        print("Total reward:", R)

#-------------------- MAIN ----------------------------
if __name__ == "__main__":
  token = sys.argv[1]
  mkt_env = MarketEnv(token,('2017-07-31','2017-08-25'))
  env = Environment()

  stateCnt  = mkt_env.data.shape[1] + 2#(mkt_env.lookback*1) + 2
  actionCnt = 3#env.env.action_space.n

  agent = Agent(stateCnt, actionCnt)
  randomAgent = RandomAgent(actionCnt)
  episode = 0

  try:
    while randomAgent.memory.isFull() == False:
        env.run(randomAgent,mkt_env,episode)
	episode += 1

    agent.memory.samples = randomAgent.memory.samples
    randomAgent = None

    print("Random is over");

    while True:
        env.run(agent,mkt_env,episode)
	episode += 1
  finally:
    agent.brain.model.save("weights.h5")
