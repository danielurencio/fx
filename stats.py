from scipy import stats
import numpy as np
from backtest.backtest_candles import get_candles

data = get_candles(('2017-08-21','2017-08-25'),"b21ba3086bf42a9ea9da12c795a86cf4-c1315644d084a99afd88faeaab8036ac")
fn = lambda x:[x['openAsk'],x['highAsk'],x['closeAsk'],x['lowAsk']]
candles = np.array(map(fn,data))

def series(data):
  series = []
  for i in range( len(data) - (12 - 1) ):
    a = data[i:i+12]
    b = []
    for j in range(a.shape[1]):
      x_r, y_r = [], []
      for ix,dd in enumerate(a[:,j].tolist()):
	x_r.append(ix)
	y_r.append(dd)
      slope, intercept, rvalue, pval, stderr = stats.linregress(x_r,y_r)
      b.append([slope,intercept,rvalue])
    series.append(np.hstack(b))
  return np.array(series)

def series_(data):
    series = []
    for i in range( len(data) - (12-1) ):
      series.append(np.hstack(data[i:i+12]))
    return np.array(series)
