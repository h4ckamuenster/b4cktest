import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy

class myBacktest_RSI(object):

    '''
        This is a simple Backtesting strategy based on RSI
        Funtcions to use:
            getRollingMean(): returns panda DF of the short mean
            optimize_SMA(min_window,max_window,interval): returns best_portfolio, best_trades, best_gain, best_shares, best_window
                        needs as input: maximum window, minimum window, interval
        
         Whole margin is re-invested. Zero Risk Aversion and Maximum Gain!
              
        @author: mhansinger
    '''

    def __init__(self, time_series, investment=1000.0, transaction_fee=0.0016):

        self.__time_series = time_series
        self.__shares = np.zeros(len(self.__time_series))

        self.__trades = np.zeros(len(self.__time_series))    # set up the trading vector, simply [-1 , 1]
        self.__portfolio = []                                 # set up the portfolio vector
        self.__costs = np.zeros(len(self.__time_series))

        self.__investment = investment
        self.__transaction_fee = transaction_fee
        self.__gain = np.zeros(len(self.__time_series))
        self.__window = []
        self.__winMin = []
        self.__winMax = []
        self.__interval = []
        self.__window_long = []
        self.__window_short = []
        self.__long_mean = []
        self.__short_mean = []
        self.__current_fee = []
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

    def __enterMarket(self, pos):
        # portfolio contains here already the investment sum
        self.__shares[pos] = (self.__portfolio[pos-1] ) / self.__time_series[pos]
        self.__portfolio[pos] = (self.__shares[pos] * self.__time_series[pos]) * (1.0 - self.__transaction_fee)
        self.__costs[pos] = self.__costs[pos-1] + (self.__shares[pos] * self.__time_series[pos]) * self.__transaction_fee
        self.__trades[pos] = 1
        self.__position = True

    def __exitMarket(self, pos):
        self.__portfolio[pos] = self.__shares[pos-1] * self.__time_series[pos] * (1.0 - self.__transaction_fee)
        self.__shares[pos] = 0
        self.__costs[pos] = self.__costs[pos-1] + (self.__shares[pos] * self.__time_series[pos]) * self.__transaction_fee
        self.__trades[pos] = -1  # indicates a short position in the trading history
        self.__position = False      # we are out of the game

    def __updatePortfolio(self, pos):
        self.__shares[pos] = self.__shares[pos - 1]
        self.__portfolio[pos] = self.__shares[pos]* self.__time_series[pos]
        self.__position = True   # wir haben coins
        self.__costs[pos] = self.__costs[pos - 1]

    def __downPortfolio(self, pos):
        self.__portfolio[pos] = self.__portfolio[pos - 1]
        self.__shares[pos] = 0
        self.__position = False  # wir haben keine coins
        self.__costs[pos] = self.__costs[pos - 1]

    def RSI(self):
        # computes the portfolio according to simple moving average, uses only ShortMean()

        #self.__long_mean = self.__getRollingMean(self.__window_long)
        #self.__short_mean = self.__getRollingMean(self.__window_short)

        self.__position = False

        self.__portfolio = []
        self.__portfolio = np.ones(len(self.__time_series))*self.__investment
        self.__costs = np.zeros(len(self.__time_series))
        self.__shares = np.zeros(len(self.__time_series))

        # initialize RSI vector
        __RSI_vec = np.array(self.__time_series[0:len(self.__window_short)] )         #np.zeros(len(self.__window_short))


        for i in range(len(self.__window_short),len(self.__time_series)):        ## hier muss noch was rein, um von beliebigem index zu starten
            __RSI_vec = self.__time_series[i-len(self.__window_short):i]

            # Compute down and up sum
            __sum_up = __RSI_vec[__RSI_vec > 0].sum()
            __sum_down = __RSI_vec[__RSI_vec < 0].sum()




        print("nach SMA: ", self.__portfolio[-1])


    def returnRSI(self, window_short = 1):
        '''returns: portfolio, gain, shares, trades in DataFrame format'''
        self.__window_short = window_short

        #print("Window: ",  self.__window )
        self.RSI_crossOver()

        return pd.DataFrame(self.__portfolio, columns=['portfolio']),  \
               pd.DataFrame(self.__shares, columns=['shares']), pd.DataFrame(self.__trades, columns=['trades'])


    def optimize_RSI(self, window_short_min=1, window_short_max=1, short_interval=1):
        '''should optimize the window for the best SMA'''

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
                self.RSI_crossOver()
                ## ******************
                __new_portfolio = copy.deepcopy(self.__portfolio)

                print("new_portfolio last: ", __new_portfolio[-1])

                if __tmp_portfolio_old[-1] < __new_portfolio[-1]:
                    __best_trades = copy.deepcopy(self.__trades)
                    __best_portfolio = copy.deepcopy(__new_portfolio)
                    __bestWindow_long = i
                    __bestWindow_short = j
                    __best_shares = copy.deepcopy(self.__shares)
                    __best_cost = copy.deepcopy(self.__costs)
                    __tmp_portfolio_old = copy.deepcopy(__best_portfolio)
                    filename=('best_portfolio_'+str(i)+'_'+str(j)+'.csv')
                    pd.DataFrame.to_csv(pd.DataFrame(__best_portfolio),filename)
                print("tmp_old:", __tmp_portfolio_old[-1])
                print("best portfolio:", __best_portfolio[-1])
                print(" ")

        __output = pd.DataFrame(__best_portfolio, columns=['best_portfolio'])
        __output['bes_shares'] = pd.DataFrame(__best_shares)
        __output['best_trades'] = pd.DataFrame(__best_trades)
        __output['best_costs'] = pd.DataFrame(__best_cost)

        return  __output,  __bestWindow_long, __bestWindow_short


