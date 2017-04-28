#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy

from BT.Backtest_SMA import myBacktest_SMA
from BT.Backtest_reinvest import myBacktest_SMAreinvest
from BT.Backtest_SMAcrossover import myBacktest_SMA_crossOver

# get the raw data

filename = 'BTC_example.csv' #'krakenEUR.csv'

raw = pd.read_csv(filename,index_col=0)
Btc_series = pd.Series(raw)

## Define some parameters!
Investment = 1000
window = 3000


Test_SMA = myBacktest_SMA(Btc_series, Investment)
Test_Re = myBacktest_SMAreinvest(Btc_series, Investment)
Test_crossOVer = myBacktest_SMA_crossOver(Btc_series, 1000)


print('SMA')
portf_SMA, gain_SMA, shares_SMA, trades_SMA = Test_SMA.returnSMA(window)
print('reinvest = max gain')
portf_Re, shares_Re, trades_Re = Test_SMA.returnSMA(window)





def plot_all():

    plt.figure(1)
    plt.plot(Btc_series)
    plt.plot(rolling)

    plt.figure(3)
    plt.plot(trades_SMA)
   # plt.plot(trades_Re)
    plt.figure(4)
    plt.plot(portf_SMA)
    #plt.plot(portf_Re)

    plt.show()

mean = new_BTC.rolling(500000).mean();


def plot_all():

    plt.figure(1)
    new_BTC.plot()
    mean_long.plot()
    mean_short.plot()

    plt.figure(2)
    portfolio.plot()
   # plt.plot(trades_Re)
    plt.figure(3)
    trades.plot()
    #plt.plot(portf_Re)

    plt.show()

def delete_all():
    del portfolio
    del shares
    del trades
    del gain
