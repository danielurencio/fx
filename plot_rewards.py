import matplotlib.pyplot as plt
from pymongo import MongoClient
import pandas as pd

col = MongoClient("mongodb://localhost:27017").backtests.EURUSD

arr = []

for doc in col.find():
  arr.append(doc)

rewards = map(lambda x:x["R"],arr)
ixs = [i for i,d in enumerate(rewards) ]
ma = pd.DataFrame({ "val":rewards }).rolling(window=100).mean().val.values

plt.plot(rewards)
plt.plot(ma)
plt.show()
