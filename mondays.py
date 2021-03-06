import pandas as pd
import numpy as np

def mondays(year):
    fechas = pd.date_range(start=str(year), end=str(year+1), 
                         freq='W-MON').strftime('%Y-%m-%d').tolist()
    fechas = pd.DataFrame({ 'fechas': np.array(fechas) })
    return fechas


if __name__ == "__main__":
  mondays(2017).to_csv("fechas.csv",index=False, header=False)
