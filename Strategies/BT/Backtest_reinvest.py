import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy

class myBacktest_SMAreinvest(object):

    '''
        This is a simple Backtesting strategy based on Rolling Mean
        Funtcions to use:
            getRollingMean(): returns panda DF of the short mean
            optimize_SMA(min_window,max_window,interval): returns best_portfolio, best_trades, best_gain, best_shares, best_window
                        needs as input: maximum window, minimum window, interval
        
         Whole margin is reinvested. Zero Risk Aversion and Maximum Gain!
              
        @author: mhansinger
    '''

    def __init__(self, time_series, investment=1000, transaction_fee=0.0):

        self.__time_series = time_series
        self.__shares=np.zeros(len(self.__time_series))
        self.__trades = np.zeros(len(self.__time_series))  # set up the trading vector, simply [-1 , 1]

        self.__investment = investment
        self.__transaction_fee = transaction_fee
        self.__gain = np.zeros(len(self.__time_series))
        self.__window = []
        self.__winMin = []
        self.__winMax = []
        self.__interval = []
        self.__current_fee =[]

        # set up the portfolio vector with the investment
        self.__portfolio = np.ones(len(self.__time_series)) * self.__investment
        self.__position = False

    def getRollingMean(self):
        #self.__window = window
        self.__short_mean = self.__time_series.rolling(self.__window).mean()
        return pd.DataFrame(self.__short_mean)

    def getRollingStd(self):
        #self.__window = window
        __rol_std = self.__time_series.rolling(self.__window).std()
        return pd.DataFrame(__rol_std)

    def __enterMarket(self, pos):
        # portfolio contains here already the investment sum
        self.__current_fee = self.__portfolio[pos-1] * self.__transaction_fee
        self.__shares[pos] = (self.__portfolio[pos-1] - self.__current_fee) / self.__time_series[pos]
        self.__portfolio[pos] = (self.__shares[pos] * self.__time_series[pos])
        self.__trades[pos] = 1
        self.__position = True
        #print('buy at: $%.2f' % self.__time_series[pos])

    def __exitMarket(self, pos):
        self.__current_fee = (self.__shares[pos-1] * self.__time_series[pos]) * self.__transaction_fee
        self.__portfolio[pos] = self.__shares[pos-1] * self.__time_series[pos] - self.__current_fee
        self.__shares[pos] = 0
        self.__trades[pos] = -1  # indicates a short position in the trading history
        self.__position = False      # we are out of the game

    def __updatePortfolio(self, pos):
        self.__shares[pos] = self.__shares[pos - 1]
        self.__portfolio[pos] = self.__shares[pos]* self.__time_series[pos]
        self.__position = True   # wir haben coins

    def __downPortfolio(self, pos):
        self.__portfolio[pos] = self.__portfolio[pos - 1]
        self.__shares[pos] = 0
        self.__position = False  # wir haben keine coins

    def SMA(self):
        # computes the portfolio according to simple moving average, uses only ShortMean()

        self.getRollingMean()

        for i in range((self.__window +1), len(self.__time_series)):        ## hier muss noch was rein, um von beliebigem index zu starten
            if self.__time_series[i] > self.__short_mean[i-1]:
                if self.__position == False:
                    # our position is short and we want to buy
                    self.__enterMarket(i)
                elif self.__position == True:
                    # we hold a position and don't want to sell: portfolio is increasing
                    self.__updatePortfolio(i)

            elif self.__time_series[i] <= self.__short_mean[i-1]:
                if self.__position == True:
                    # we should get out of the market and sell:
                    self.__exitMarket(i)
                elif self.__position == False:
                    # do nothing for now
                    self.__downPortfolio(i)
        print("nach SMA: ", self.__portfolio)


       ## pd.DataFrame.to_csv(pd.DataFrame(self.__portfolio),'Portfolio.csv')

    def returnSMA(self, window):
        self.__window = window
        print("Window: "+ self.__window)
        self.SMA()
        return pd.DataFrame(self.__portfolio), pd.DataFrame(self.__shares), pd.DataFrame(self.__trades)


    def optimize_SMA(self,Min,Max,interval):
        '''should optimize the window for the best SMA'''

        __Min = Min
        __Max = Max
        __interval = interval

        __bestWindow = 0

        __tmp_portfolio_old = np.array([0,0])
        __best_portfolio = np.array([0,0])
        __best_trades = []
        __best_gain = []
        __best_shares = []

        for i in range(__Min,__Max,__interval):

            self.__window = i
            print("window: ", self.__window)
            ## ******************
            self.SMA()
            ## ******************
            __new_portfolio = copy.deepcopy(self.__portfolio)

            print("new_portfolio last: ", self.__portfolio[-1])

            if __tmp_portfolio_old[-1] < __new_portfolio[-1]:
                __best_trades = self.__trades[:]
                __best_portfolio = copy.deepcopy(__new_portfolio)
                __bestWindow = i
                __best_gain = copy.deepcopy(self.__gain)
                __best_shares = copy.deepcopy(self.__shares)
                __tmp_portfolio_old = copy.deepcopy(__best_portfolio)
            print("tmp_old:", __tmp_portfolio_old[-1])
            print("best portfolio:", __best_portfolio[-1])

        return  pd.DataFrame(__best_portfolio), pd.DataFrame(__best_trades), pd.DataFrame(__best_gain), \
                pd.DataFrame(__best_shares), __bestWindow


