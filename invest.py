##NUS INVEST VOLATILITY MODELLING

import talib
import pickle
import pandas as pd

"""
Output of Script: DB structure with ["pair1 open", "pair1 high"..."pair1 feature1", "pair1 feature2"..."pairN featureN"]

Data Source: OHLCV time series data

Alternative Data (is indicative of):
VIX Index (expectation of equity volatility)
Macro Indicators

Feature (is indicative of): 
ATR (Volatility)
BBands (Volatility)
RSI (Momentum)
OBV (Volume)
...
"""

instruments = [
    "EUR_USD",
    "AUD_USD", 
    "GBP_USD",
    "USD_CAD", 
    "NZD_USD", 
    "USD_CHF", 
    "USD_JPY", 
    "USD_NOK", 
    "USD_SEK"
]

def get_fx_db():
    ohlcv = pd.read_excel("./database/dwx_ohlcv.xlsx").set_index("date")
    fx_database = pd.DataFrame(index=ohlcv.index)
    cols = ["open", "high", "low", "close", "volume"]
    for inst in instruments:
        for col in cols:
            fx_database["{} {}".format(inst, col)] = ohlcv["{} {}".format(inst, col)]
    return fx_database


# filehandler = open("fx_db.obj","wb")
# pickle.dump(get_fx_db(),filehandler)
# filehandler.close()

# exit()

file = open("fx_db.obj",'rb')
fx_db = pickle.load(file)
file.close()

import datetime
import pandas_datareader as pdr

def format_date(series):
    ymd = list(map(lambda x: int(x), str(series).split(" ")[0].split("-")))
    return datetime.date(ymd[0], ymd[1], ymd[2])

vix_index = pdr.get_data_yahoo("^VIX", fx_db.index[1], fx_db.index[-1])
vix_index.columns = list(map(lambda x: "{} {}".format("VIX", x), list(vix_index)))
vix_index = vix_index.reset_index()
fx_db = fx_db.reset_index().rename(columns={"date": "Date"})
vix_index["Date"] = vix_index["Date"].apply(lambda x: format_date(x))
fx_db["Date"] = fx_db["Date"].apply(lambda x: format_date(x))

df = fx_db.merge(vix_index, how="inner", on="Date")

print(fx_db)
print(vix_index)
print(df)

for inst in instruments:
    """ATR"""
    df["{} {}".format(inst, "ATR")] = talib.ATR(df["{} high".format(inst)], df["{} low".format(inst)], df["{} close".format(inst)], timeperiod = 14)
    
    """OBV"""
    df["{} {}".format(inst, "OBV")] = talib.OBV(df['{} close'.format(inst)], df['{} volume'.format(inst)])

    """RSI"""
    df["{} {}".format(inst, "RSI")] = talib.RSI(df["{} close".format(inst)], timeperiod = 14)

    """BBANDS"""
    bband = pd.DataFrame()
    bband["MA"] = df["{} close".format(inst)].rolling(14).mean()
    bband["stdev"] = df["{} close".format(inst)].rolling(14).std() 
    bband["BB_up"] = bband["MA"] + 2 * bband["stdev"]
    bband["BB_dn"] = bband["MA"] - 2 * bband["stdev"]
    df["{} BB_up".format(inst)] = bband["BB_up"]
    df["{} BB_dn".format(inst)] = bband["BB_dn"]

    
print(df)
df.to_excel("df.xlsx")