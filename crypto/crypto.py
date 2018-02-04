import requests
import numpy as np
from time import time
from datetime import datetime

def candles(dates):
  from_ = datetime.strptime(dates[0],"%Y-%m-%d")
  to_ = datetime.strptime(dates[1],"%Y-%m-%d")
  limit = str( (to_ - from_).days * 24 )
  toTs = to_.strftime("%s")
  url = "https://min-api.cryptocompare.com/data/histohour?fsym=ETH&tsym=USD&limit="+ limit +"&toTs=" + toTs
  data = requests.get(url).json()["Data"]
  data = map(lambda x:[x['open'],x['high'],x['close'],x['low']],data)
  data = np.array(data).astype(float)
  return data
