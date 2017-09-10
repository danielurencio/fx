import oandapy
import pymongo
import sys

class MyStreamer(oandapy.Streamer):
    def __init__(self, func, *args, **kwargs):
        super(MyStreamer, self).__init__(*args, **kwargs)
	self.func = func

    def on_success(self, data):
#        print data, "\n"
        while(True):
	   self.func(data)

    def on_error(self, data):
        self.disconnect()



def mongoStream(year=2017,month=1):
    conn = pymongo.MongoClient('mongodb://localhost:27017')
    col = conn["fx"]["EURUSD"]
    cursor = col.find({ 'year':year,'month':month })
    return cursor

def justPrint(data):
    print data,"--","\n"


if(__name__ == "__main__"):
    account = sys.argv[1]
    token = sys.argv[2]
    stream = MyStreamer(justPrint,environment="practice",access_token=token).rates(account,instruments="EUR_USD")
