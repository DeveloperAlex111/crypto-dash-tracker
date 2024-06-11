import pandas as pd
import datetime as dt
import pandas_ta as ta
from binance.client import Client # pip install python-binance

client = Client()
TIME_UNITS = ['1d', '1h', '1m']
AMOUNT_OF_DAYS = ['1', '2', '3', '5', '15', '30', '60']

def get_historical_ohlc_data(symbol,past_days=30,interval='1h'): #past_days: how many days back to download the data, interval - what the interval to download 1d, 1h
    start_str=str((pd.to_datetime('today')-pd.Timedelta(str(past_days)+' days')).date())
    df = pd.DataFrame(client.get_historical_klines(symbol=symbol,start_str=start_str,interval=interval)) #using api to get dataset
    df.columns = ['open_time','open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol','is_best_match']
    df = df.astype({'open':'float', 'close':'float', 'high':'float', 'low':'float'})
    df['open_date_time'] = [dt.datetime.fromtimestamp(x/1000) for x in df.open_time]
    df['symbol'] = symbol # the currency pair of the data frame
    df['hma'] = ta.hma(df.close.astype(float)) # the Hull Moving Average 
    df['rsi'] = ta.rsi(df.close.astype(float)) # the relative strength index
    df= df[['symbol','open_date_time','open', 'high', 'low', 'close', 'volume', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'hma', 'rsi']]
    return df

def get_symbols():
    df = pd.DataFrame(client.get_all_tickers()) # a data frame of all currency pairs from binance.com
    return df['symbol'].to_list()

#print(get_historical_ohlc_data("BTCUSDT", 30, '1h'))