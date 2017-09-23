from backtest.backtest_candles import *
from models.nn import *
from datetime import datetime
import sys


# GET THE DATE TO TRAIN A MODEL.
t0 = datetime.now()
# RANGE OF DATES FROM WHICH THE DATA IS EXTRACTED.
dates_modelo = ('2017-01-02','2017-03-01')
# PASS THE OANDA TOKEN AS A COMMAND LINE ARGUMENT
token = sys.argv[1]
# GET CANDLES FROM THE RANGE.
data_modelo = get_candles(dates_modelo,token)
# CONVERT DATA TO A DATAFRAME
df_modelo = create_df(data_modelo)
# CREATE AN INSTANCE OF THE MODEL
modelo = NN()
# CHOOSE THE MODELS HYPERPARAMETERS
chromosome = [12*4,3*4,0.002,0.1,1000,5000]
# COMPILE AND FIT THE MODEL
modelo.create_model(df_modelo,chromosome)

# GET THE DATA FOR THE MOST RECENT OBSERVATION
dates_feed = last_n(datetime.now(),modelo.lookback*2-1)
# GET THE LATEST CANDLES
data_feed = get_candles(dates_feed,token)
# CONVERT DATA TO DATAFRAME
df_feed = create_df(data_feed)
# CREATE ANOTHER INSTANCE FOR THE MOST RECENT OBSERVATION
nn = NN()
# GENERATE A PREDICTION WITH BOTH INSTANCES
prediction = nn.predict(df_feed,modelo)
print prediction

t1 = datetime.now() - t0
print(t1)
