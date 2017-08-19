import pandas as pd
import sys

file0 = sys.argv[1]
file1 = sys.argv[2]

data_frame = pd.read_csv(file0, names=['Symbol', 'Date_Time', 'Bid', 'Ask'],index_col=1, parse_dates=True)

data_ask =  data_frame['Ask'].resample('15Min').ohlc()
data_bid =  data_frame['Bid'].resample('15Min').ohlc()

data_ask_bid=pd.concat([data_ask, data_bid], axis=1, keys=['Ask', 'Bid'])

data_ask_bid.to_csv("data" + str(file1) + ".csv", header=None)
