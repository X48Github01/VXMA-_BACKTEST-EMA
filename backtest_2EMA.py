import math
import time
import warnings
from datetime import datetime as dt

import ccxt
import numpy as np
import pandas as pd
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

pd.set_option("display.max_rows", None)
warnings.filterwarnings("ignore")
# Bot setting
BOT_NAME = "VXMA"
# Change Symbol Here
SYMBOL_NAME = "BTC"
# Change Time Frame Here
TF = "1d"
# API CONNECT
exchange = ccxt.binance()
symboli = SYMBOL_NAME + "/USDT"


print(f"Backtesting {symboli} on timeframe {TF}")
bars = exchange.fetch_ohlcv(symboli, timeframe=TF, since=None, limit=1502)
df = pd.DataFrame(
    bars[:-1], columns=["timestamp", "Open", "High", "Low", "Close", "Volume"]
)
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
df = df.set_index("timestamp")


def Ema_Fast(period):
    global df
    df["EMA_fast"] = ta.ema(df.Close, period)
    return df.EMA_fast


def Ema_Slow(period):
    global df
    df["EMA_slow"] = ta.ema(df.Close, period)
    return df.EMA_slow


def signalbuy():
    m = len(df.index)
    df["buy"] = [False] * m
    for i in range(3, m):
        if (
            df["EMA_fast"][i - 1] > df["EMA_slow"][i - 1]
            and df["EMA_fast"][i - 2] < df["EMA_slow"][i - 2]
        ):
            df["buy"][i] = True
    return df.buy


def signalsell():
    m = len(df.index)
    df["sell"] = [False] * m
    for i in range(3, m):
        if (
            df["EMA_fast"][i - 1] < df["EMA_slow"][i - 1]
            and df["EMA_slow"][i - 2] < df["EMA_fast"][i - 2]
        ):
            df["sell"][i] = True
    return df.sell


class run_bot(Strategy):
    ema_fast = 12
    ema_slow = 26

    def init(self):
        super().init()
        self.A2 = self.I(
            Ema_Fast,
            self.ema_fast,
        )

        self.A1 = self.I(
            Ema_Slow,
            self.ema_slow,
        )
        self.A3 = self.I(signalbuy)

        self.A4 = self.I(signalsell)

    def next(self):
        if self.A3:
            self.position.close()
            self.buy()
        if self.A4:
            self.position.close()
            self.sell()


bt = Backtest(df, run_bot, cash=10000)
stat = bt.run()
# stat = bt.optimize(
# ema_fast = range(1,200,2),
# ema_slow = range(1,200,2),
# maximize = 'Win Rate [%]')
print(stat)
bt.plot()

#Start                     2004-08-19 00:00:00
#End                       2013-03-01 00:00:00
#Duration                   3116 days 00:00:00
#Exposure Time [%]                       94.27
#Equity Final [$]                     68935.12
#Equity Peak [$]                      68991.22
#Return [%]                             589.35
#Buy & Hold Return [%]                  703.46
#Return (Ann.) [%]                       25.42
#Volatility (Ann.) [%]                   38.43
#Sharpe Ratio                             0.66
#Sortino Ratio                            1.30
#Calmar Ratio                             0.77
#Max. Drawdown [%]                      -33.08
#Avg. Drawdown [%]                       -5.58
#Max. Drawdown Duration      688 days 00:00:00
#Avg. Drawdown Duration       41 days 00:00:00
## Trades                                   93
#Win Rate [%]                            53.76
#Best Trade [%]                          57.12
#Worst Trade [%]                        -16.63
#Avg. Trade [%]                           1.96
#Max. Trade Duration         121 days 00:00:00
#Avg. Trade Duration          32 days 00:00:00
#Profit Factor                            2.13
#Expectancy [%]                           6.91
#SQN                                      1.78
#_strategy              SmaCross(n1=10, n2=20)
