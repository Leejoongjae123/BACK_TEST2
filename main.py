import pandas as pd
import numpy as np
import time
import datetime
import json
import math
import json
import time
import requests
import datetime
import traceback
import talib
import ccxt
import os
import uuid
import hashlib
from urllib.parse import urlencode
import telepot
import telegram
import pandas
import openpyxl
from scipy import stats
from urllib.parse import urlencode
import requests
from collections import deque
import pandas as pd

with open("binance.txt") as f: #binance.txt파일을 불러와서 로그인한다.
    lines = f.readlines()
    api_key = lines[0].strip()
    secret = lines[1].strip()

market_type = 'future'  # 선물 거래를 할시 아래 두줄을 사용한다.
binance = ccxt.binance(config={'apiKey': api_key, 'secret': secret, 'enableRateLimit': True,
                               'options': {'defaultType': market_type}})  # 바이낸스 선물 로그인

profit_total=[]

# markets=['ARPA/USDT','ATOM/USDT','CHZ/USDT','DENT/USDT','FIL/USDT','FLOW/USDT','ROSE/USDT','LINA/USDT','LINK/USDT','MATIC/USDT']
markets=['RLC/USDT','SKL/USDT','CTSI/USDT','UNFI/USDT','RUNE/USDT','MASK/USDT','KNC/USDT','BTS/USDT','AAVE/USDT','TRB/USDT']

for market in markets:
    result=[]
    for i in range(0,10*5):
        if i==0:
            df = binance.fetch_ohlcv(symbol=market, timeframe='5m', since=None, limit=200)
            # print("처음")
        else:
            # print(i,"번째")
            end_date=df[0][0]-300000
            df = binance.fetch_ohlcv(symbol=market, timeframe='5m', since=None, limit=200, params={'endTime': end_date})
        result=df+result
        time.sleep(0.1)

    df=pd.DataFrame(result,columns=['datetime','open','high','low','close','volume'])
    df['datetime']=pd.to_datetime(df['datetime'],unit='ms')+datetime.timedelta(hours=9)
    df.set_index('datetime',inplace=True)

    CCI_raw = talib.CCI(df['high'], df['low'], df['close'], timeperiod=14)
    #
    MFI_raw = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=14)

    ADX_raw = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)

    PLUS_DI_raw = talib.PLUS_DI(df['high'], df['low'], df['close'], timeperiod=14)
    MINUS_DI_raw = talib.MINUS_DI(df['high'], df['low'], df['close'], timeperiod=14)


    # print(df)
    # print("행의갯수:",len(df))

    # print(CCI_raw)
    time_sell=0
    profit_sum=0
    profit_history=[]
    # print(CCI_raw)
    # CCI_raw.to_excel("CCI.xlsx")
    count=0
    for i in range(0,len(df)):
        if CCI_raw[i] < -100 and MFI_raw[i] < 50 and ADX_raw[i]<25:

            price_buy=(df.iloc[i]['open']+df.iloc[i]['close'])/2

            if i<=time_sell:
                continue

            for j in range(i,len(df)):
                if ADX_raw[j]>30:
                    price_sell = (df.iloc[j]['open'] + df.iloc[j]['close']) / 2
                    print("short")
                    print("시간:", CCI_raw.index[i], "CCI:", round(CCI_raw[i],1),"ADX:",round(ADX_raw[i],1),"MFI:",round(MFI_raw[i],1), "구매가격:", price_buy)
                    print("시간:", CCI_raw.index[j], "CCI:", round(CCI_raw[j],1),"ADX:",round(ADX_raw[j],1),"MFI:",round(MFI_raw[j],1), "판매가격:", price_sell)
                    profit=round((price_buy - price_sell) / price_buy * 100,2)
                    profit_sum=round(profit_sum+profit,2)
                    count=count+1
                    profit_history.append([df.index[i],profit_sum])
                    print("수익률:",round(profit,2),"누적수익률:",round(profit_sum,2),"횟수:",count)
                    # print("-----------------------------------------------------------------")
                    time_sell=j
                    break

        if 100<CCI_raw[i] and MFI_raw[i] > 50 and ADX_raw[i]<25:
            price_buy=(df.iloc[i]['open']+df.iloc[i]['close'])/2

            if i<=time_sell:
                continue

            for j in range(i,len(df)):
                if ADX_raw[j]>30:
                    price_sell = (df.iloc[j]['open'] + df.iloc[j]['close']) / 2
                    print("long")
                    print("시간:", CCI_raw.index[i], "CCI:", round(CCI_raw[i], 1), "ADX:", round(ADX_raw[i], 1), "MFI:", round(MFI_raw[i], 1), "구매가격:", price_buy)
                    print("시간:", CCI_raw.index[j], "CCI:", round(CCI_raw[j], 1), "ADX:", round(ADX_raw[j], 1), "MFI:", round(MFI_raw[j], 1), "판매가격:", price_sell)
                    profit=round((price_sell-price_buy) / price_buy * 100,2)
                    profit_sum=round(profit_sum+profit,2)
                    count=count+1
                    profit_history.append([df.index[i],profit_sum])
                    print("수익률:",profit,"누적수익률:",profit_sum,"횟수:",count)
                    # print("-----------------------------------------------------------------")
                    time_sell=j
                    break
    print("--------------------------{}----------------------------".format(market))
    profit_history = pd.DataFrame(data=profit_history, columns=["date", "profit"])
    profit_history.set_index('date', inplace=True)
    non_slash_market = market.replace("/", "")
    profit_history.to_excel("history_{}.xlsx".format(non_slash_market))
    profit_total.append([market,profit_sum])
profit_total = pd.DataFrame(data=profit_total, columns=["market", "profit_total"])
profit_total.set_index('market', inplace=True)
datetime_now=datetime.datetime.now()
datetime_now=datetime_now.strftime("%H%M%S")
profit_total.to_excel("profit_total_{}.xlsx".format(datetime_now))








