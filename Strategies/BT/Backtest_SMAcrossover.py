import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import time

#################################
# DONT CHANGE: IT WORKS
# Date: 23.4.2017
#################################

class myBacktest_SMA_crossOver(object):

    def __init__(self, time_series, investment=1000, transaction_fee=0.0):
        ''' maker or taker fee is to set'''

        self.__time_series = time_series
        self.__shares = np.zeros(len(self.__time_series))

        self.__trades = np.zeros(len(self.__time_series))    # set up the trading vector, simply [-1 , 1]
        self.__portfolio= np.zeros(len(self.__time_series))  # set up the portfolio vector

        self.__investment = investment
        self.__transaction_fee = transaction_fee
        self.__gain = np.zeros(len(self.__time_series))
        self.__window = []
        self.__winMin = []
        self.__winMax = []
        self.__interval = []
        self.__window_long = []
        self.__window_short = []
        self.__long_mean =[]
        self.__short_mean = []
        self.__current_fee =[]
        self.__position = False

    def __getRollingMean(self,__window):
        __rolling_mean = self.__time_series.rolling(__window).mean()
        return __rolling_mean

    def returnRollingStd(self):
        __rol_std = self.__time_series.rolling(self.__window).std()
        return pd.DataFrame(__rol_std, columns=['Rolling Std'])

    def returnRollingMean(self, window):
        print(window)
        __rolling_mean = self.__getRollingMean(window)
        __rolling_df = pd.DataFrame(__rolling_mean)
        return __rolling_df

    def __enterMarket(self,pos):
        self.__current_fee = self.__investment * self.__transaction_fee
        self.__shares[pos] = (self.__investment - self.__current_fee) / self.__time_series[pos]
        self.__portfolio[pos] = (self.__shares[pos] * self.__time_series[pos]) + self.__gain[pos-1]
        self.__trades[pos] = 1
        self.__gain[pos] = self.__gain[pos-1]
        self.__position = True
        #print('buy at: $%.2f' % self.__time_series[pos])

    def __exitMarket(self, pos):
        self.__current_fee = (self.__shares[pos-1] * self.__time_series[pos]) * self.__transaction_fee
        self.__portfolio[pos] = (self.__shares[pos-1] * self.__time_series[pos]) + self.__gain[pos-1] - self.__current_fee
        self.__gain[pos] = self.__portfolio[pos] - self.__investment
        self.__shares[pos] = 0
        self.__position = False      # we are out of the game
        self.__trades[pos] = -1  # indicates a short position in the trading history

    def __updatePortfolio(self,pos):
        self.__shares[pos] = self.__shares[pos - 1]
        self.__portfolio[pos] = self.__shares[pos] * self.__time_series[pos] + self.__gain[pos-1]
        self.__gain[pos] = self.__gain[pos - 1]
        self.__position = True # we are out of the game

    def __downPortfolio(self, pos):
        self.__portfolio[pos] = self.__portfolio[pos - 1]
        self.__shares[pos] = 0
        self.__gain[pos] = self.__gain[pos-1]
        self.__position = False  # we are out of the game


    def SMA_crossOver(self):
        # computes the portfolio according to simple moving average, uses only ShortMean()

        self.__portfolio = np.zeros(len(self.__time_series))
        self.__long_mean = self.__getRollingMean(self.__window_long)
        self.__short_mean = self.__getRollingMean(self.__window_short)

        for i in range((self.__window_long+1), len(self.__time_series)):        ## hier muss noch was rein, um von beliebigem index zu starten
           # print(i, self.__trades[i])
            if self.__short_mean[i] > self.__long_mean[i-1]:
                if self.__position == False:
                    # our position is short and we want to buy
                    self.__enterMarket(i)
                elif self.__position == True:
                    # we hold a position and don't want to sell: portfolio is increasing
                    self.__updatePortfolio(i)

            elif self.__short_mean[i] <= self.__long_mean[i-1]:
                if self.__position == True:
                    # we should get out of the market and sell:
                    self.__exitMarket(i)
                elif self.__position == False:
                    # do nothing for now
                    self.__downPortfolio(i)

            if self.__portfolio[i] < 0.0:
                print('Skip loop, negative portfolio')
                break

        print("nach SMA: ", self.__portfolio[-1])

    def returnSMA_crossOver(self, window_long, window_short = 1):
        ''' if short = 1 --> cross over with time series!'''
        '''returns: portfolio, gain, shares, trades in DataFrame format'''
        self.__window_long = window_long
        self.__window_short = window_short

        #print("Window: ",  self.__window )
        self.SMA_crossOver()

        return pd.DataFrame(self.__portfolio, columns=['portfolio']), pd.DataFrame(self.__gain, columns=['gain']), \
               pd.DataFrame(self.__shares, columns=['shares']), pd.DataFrame(self.__trades, columns=['trades'])

## update from here!
    def optimize_SMAcrossover(self, window_long_min, window_long_max, long_interval, window_short_min=1,
                              window_short_max=1, short_interval=1):
        '''should optimize the window for the best SMA'''

        __window_long_min = window_long_min
        __window_long_max = window_long_max
        __long_interval = long_interval
        __window_short_min = window_short_min
        __window_short_max = window_short_max
        __short_interval = short_interval

        __bestWindow_long = 0
        __bestWindow_short = 0

        ## Initialize
        __tmp_portfolio_old = np.array([0, 0])
        __best_portfolio = np.array([0, 0])
        __best_trades = []
        __best_gain = []
        __best_shares = []


        # iterate over the two window lengths
        for i in range(__window_long_min, __window_long_max, __long_interval):
            # assign long window
            self.__window_long = i

            for j in range(__window_short_min, __window_short_max, __short_interval):
                # assign short window
                self.__window_short = j

                print("window short: ", j)
                print("window long: ", i)

                ## ******************
                self.SMA_crossOver()
                ## ******************
                __new_portfolio = copy.deepcopy(self.__portfolio)

                print("new_portfolio last: ", __new_portfolio[-1])

                if __tmp_portfolio_old[-1] < __new_portfolio[-1]:
                    __best_trades = copy.deepcopy(self.__trades)
                    __best_portfolio = copy.deepcopy(__new_portfolio)
                    __bestWindow_long = i
                    __bestWindow_short = j
                    __best_gain = copy.deepcopy(self.__gain)
                    __best_shares = copy.deepcopy(self.__shares)
                    __tmp_portfolio_old = copy.deepcopy(__best_portfolio)
                    filename = ('best_portfolio_'+str(i)+'_'+str(j)+'.csv')
                    pd.DataFrame.to_csv(pd.DataFrame(__best_portfolio), filename)
                print("tmp_old:", __tmp_portfolio_old[-1])
                print("best portfolio:", __best_portfolio[-1])
                print(" ")


        __output = pd.DataFrame(__best_portfolio, columns=['best_portfolio'])
        __output['bes_shares'] = pd.DataFrame(__best_shares)
        __output['best_trades'] = pd.DataFrame(__best_trades)
        __output['best_gain'] = pd.DataFrame(__best_gain)

        return  __output,  __bestWindow_long, __bestWindow_short