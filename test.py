import pandas as pd
import numpy as np
from fx import FX

obj = {
  'collection':"eurusd_1m",
  "db":"fx",
  "connection":"mongodb://localhost:27017",
  "query": { "year": 2009, "month":5 }
}

a = FX(obj)
b = a.mm(5)
