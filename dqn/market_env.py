from backtest.backtest_candles import get_candles

def data():
  token = "59f5159dcfb7d742ff3d53ddc0097be9-e760cea159c68dde7e7d22258eb9dcb5"
  dates_modelo = ('2017-01-02','2017-02-27')
  dates_bt = ('2017-02-27','2017-03-04')
  data_modelo = get_candles(dates_modelo,token)
  return data_modelo
