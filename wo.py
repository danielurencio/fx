from backtest.backtest_candles import *
import datetime
from pprint import pprint

n = 10
token = "a24e48fb2e3c61d0c1d5b2ad69938fcb-cfb1d9b2eb3e5e2d8f642b621496e771"
date_ex = datetime.datetime(2017,9,17,21,15)
g_t = lambda x:x["time"]

pprint(map(g_t,data))
dateutil.parser.parse(data[9]["time"]) - dateutil.parser.parse(data[8]["time"])
