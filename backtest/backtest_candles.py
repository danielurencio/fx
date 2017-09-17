import pandas as pd
import numpy as np
import oandapy as opy
import datetime
import sys

def get_candles(dates,token):
  oanda = opy.API(environment="practice", access_token=token)
  data = oanda.get_history(instrument="EUR_USD", start=dates[0],end=dates[1],granularity="M15")
  return data["candles"]


def last_n(date,n):
  minute = date.minute
  minutes = [0,15,30,45]
  difs = [minute - i for i in minutes]
#  difs = filter(lambda x: x if x >= 0 and x != None else None,difs)
  difs = [i for i in difs if i >= 0]
  ix = [i for i,d in enumerate(minutes) if minute-d >= 0 and minute-d == min(difs)]
  ix = minutes[ix[0]]
  end = datetime.datetime(date.year,date.month,date.day,date.hour,ix)
  start = end -datetime.timedelta(minutes=15*n)
  return (start.isoformat(),end.isoformat())

def create_df(data):
  dic = {
   'Date_Time':map(lambda x:x['time'],data),
   'ask_open':map(lambda x:x['openAsk'],data),
   'ask_high':map(lambda x:x['highAsk'],data),
   'ask_low':map(lambda x:x['lowAsk'],data),
   'ask_close':map(lambda x:x['closeAsk'],data),
   'bid_open':map(lambda x:x['openBid'],data),
   'bid_high':map(lambda x:x['highBid'],data),
   'bid_low':map(lambda x:x['lowBid'],data),
   'bid_close':map(lambda x:x['closeBid'],data)
  }
  df = pd.DataFrame(dic)
  df.Date_Time = pd.to_datetime(df.Date_Time)
  df.set_index("Date_Time",inplace=True)
  return df
