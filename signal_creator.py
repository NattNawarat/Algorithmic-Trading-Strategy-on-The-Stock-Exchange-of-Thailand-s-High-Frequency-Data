import pandas as pd
import numpy as np
import data_reader
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import matplotlib.pyplot as plt
from mean_reversion_test import get_hedge_ratio
import config

class SignalCreater():
    """
    This class will create SignalDataFrame base on mean reversion strategy
    init input
    stocks                 DataFrame contains close price of multiple stocks
    seperate_frequency     String represent frequency you want to seperate stocks
    adf_p_maximum          maximum p-value of adf test we will use to reject
    hurst_maximum          maximum hurst exponential value we use to create signal
    """
    def __init__(self,stocks_price,seperate_frequency,adf_p_maximum = 0.05,hurst_maximum = 0.5,must_coint = True):
        self.stocks_price = stocks_price.dropna()
        self.seperate_frequency = seperate_frequency
        self.adf_p_maximum = adf_p_maximum
        self.hurst_maximum = hurst_maximum
        #create list of stocks price by seperate frequency
        self.seperated_stocks = [g for n, g in stocks_price.groupby(pd.Grouper(freq = self.seperate_frequency))]
        self.mean_rev_data = []
        self.must_coint = must_coint
        self.prev_timeframe = 4
        
    def create_mean_rev_data(self,plot):
        """
        Thise function will create mean reversion portfolio z_score and etc.
        to create trade signal
        """
        self.mean_rev_data = []
        for i in range(self.prev_timeframe,len(self.seperated_stocks)):
            print(f"{i}/{len(self.seperated_stocks)}",end = '\r')
            #boolean which tell whether we can create mean reversion port in this week or not
            can_hedge = False
            #find hedge ratio and other statistics test value
            
            prev_df = pd.concat(self.seperated_stocks[i-self.prev_timeframe:i])
            mean_rev_test_result = get_hedge_ratio(prev_df, must_coint = self.must_coint)
            #prepare dictionary to store all necessary data to create trade signal
            mean_rev = {}
            if len(mean_rev_test_result) != 0:   #this mean we got possible mean reversion portfolio base on pass timeframe
                #set default value
                half_life = 100
                minimum_half_life = 0
                stock_1 = ''
                stock_2 = ''
                hedge_vector = []
                adf_p_value = 0
                hurst_expo = 0
                #find mean reversion portfolio which has lowest half-life
                for key in mean_rev_test_result.keys():
                        hedge_result = mean_rev_test_result[key]
                        if (hedge_result['adf_p_value'] < self.adf_p_maximum) and (hedge_result['hurst_expo'] < self.hurst_maximum):
                            #can reject random walk(adf test) and not geometric random walk(hurst exponential)
                            if (int(hedge_result['half_life']) < half_life) and (int(hedge_result['half_life']) > minimum_half_life):
                                can_hedge = True
                                adf_p_value = hedge_result['adf_p_value']
                                hurst_expo = hedge_result['hurst_expo']
                                half_life = int(hedge_result['half_life'])
                                stock_1 = hedge_result['stock_1']
                                stock_2 = hedge_result['stock_2']
                                hedge_vector = hedge_result['hedge_vector']
            if not can_hedge:
                continue
            
            
            #once we get all require parameter we will create z_score for pair trading
            #create dataframe contain price of stocks, mean reversion portfolio, z_score and so on
            #concat pass timeframe and present timeframe(pass timeframe will be use to create rolling std and avg)
            #mean_rev_df = pd.concat([self.seperated_stocks[i-1],self.seperated_stocks[i]]).sort_index()
            mean_rev_df = pd.concat([prev_df,self.seperated_stocks[i]]).sort_index()
            #create z_score
            mean_rev_df = mean_rev_df[[stock_1,stock_2]]
            mean_rev_df['mean_rev_port'] = mean_rev_df[[stock_1,stock_2]].dot(hedge_vector)
            mean_rev_df['rolling_mean'] = mean_rev_df['mean_rev_port'].rolling(int(half_life)).mean()
            mean_rev_df['rolling_std'] = mean_rev_df['mean_rev_port'].rolling(int(half_life)).std()
            mean_rev_df['z_score'] = (mean_rev_df['mean_rev_port'] - mean_rev_df['rolling_mean'])/mean_rev_df['rolling_std']
            #sometimes rolling std is zero which made z_score = inf
            mean_rev_df.replace([np.nan,np.inf, -np.inf], 0, inplace=True)
            #set z_score 0 at last point because we need to liquidate every timeframe
            mean_rev_df['z_score'].iloc[-1] = 0
            mean_rev_df['z_score'].iloc[-2] = 0
            #slice to get present timeframe only
            self.all_df = prev_df.copy()
            mean_rev_df = [g for n, g in mean_rev_df.groupby(pd.Grouper(freq = self.seperate_frequency))][-1]
            self.sliced_df = mean_rev_df.copy()
            #rename stock's name
            mean_rev_df.columns = ['stock_1','stock_2'] + list(mean_rev_df.columns)[2:]
            
            #put all data into dict
            mean_rev['df'] = mean_rev_df
            mean_rev['hedge_vector'] = hedge_vector
            mean_rev['stock_1'] = stock_1
            mean_rev['stock_2'] = stock_2
            mean_rev['half_life'] = half_life
            mean_rev['adf'] = adf_p_value
            mean_rev['hurst_expo'] = hurst_expo
            
            #append dict into list to creat trade signal later
            self.mean_rev_data.append(mean_rev)
            
            if plot == True:
                print(stock_1)
                print(stock_2)
                print(half_life)
                print(hedge_vector)
                plt.plot(np.array(mean_rev_df[stock_1]))
                plt.show()
                plt.plot(np.array(mean_rev_df[stock_2]))
                plt.show()
                plt.figure(figsize=(20,10))
                plt.plot(np.array(mean_rev_df['mean_rev_port']))
                plt.plot(np.array(mean_rev_df['rolling_mean']))
                plt.plot(np.array(mean_rev_df['rolling_mean'] + 2 * mean_rev_df['rolling_std'] ))
                plt.plot(np.array(mean_rev_df['rolling_mean'] - 2 * mean_rev_df['rolling_std'] ))
                plt.show()
                plt.plot(np.array(mean_rev_df['z_score']))
                plt.show()
                
    def create_trade_signal(self,enter_z_score = 2,exit_z_score = 0.5):
        """
        This function will use mean_rev_data to create trade signal
        by using bollinger band to create short long signal
        parameter
        enter_z_score:  absolute of z_score we use to enter position
        exit_z_score:   absolute of z_score we use to exit postion
        """
        if len(self.mean_rev_data) == 0:
            print("mean_rev_data not found")
            print("please run create mean_rev_data before this function")
        for i in range(0,len(self.mean_rev_data)):
            df = self.mean_rev_data[i]['df']
            hedge_vector = self.mean_rev_data[i]['hedge_vector']
            #create value to find percentage of volume we should take position in each stock
            df['stock_1_value'] = df['stock_1'] * hedge_vector[0]
            df['stock_2_value'] = df['stock_2'] * hedge_vector[1]
            df['abs_value'] = abs(df['stock_1_value']) + abs(df['stock_2_value'])
            df['stock_1_pct'] = abs(df['stock_1_value']) / df['abs_value']
            df['stock_2_pct'] = abs(df['stock_2_value']) / df['abs_value']

            position = np.zeros([len(df),1])
            if abs(df['z_score'].iloc[0]) >= enter_z_score:
                position[0] = -np.sign(df['z_score'].iloc[0])


            for j in range(0,len(df.index)):
                curr_position = position[j-1]
                curr_z_score = df['z_score'].iloc[j]
                if curr_position == 0:
                    if abs(curr_z_score) > enter_z_score:
                        curr_position = -np.sign(curr_z_score)
                elif curr_position != 0:
                    if (curr_position == 1) and (curr_z_score >= -exit_z_score):
                        curr_position = 0
                    elif (curr_position == -1) and (curr_z_score < exit_z_score):
                        curr_position = 0
                position[j] = curr_position
             
            df['Signal'] = position


class BacktestDataPreprator():
    def __init__(self,stocks,start_date,end_date):
        """
        self.stocks      LIST    list of stock's name
        self.start_date  STR     date which model start to calculate
        self.end_date    STR     date which model stop calculate
        self.stocks_df   DATAFRAME   close price in 5 minutes interval of each stock in self.stocks  (sliced wit self.start_date and self.end_date)
        self.OHLC        DICT        dict contain self.OHLC price in 5 minutes interval of each stock (did not slice due to hard code of self.OHLC's lengths)
        """
        self.stocks = stocks
        self.start_date = start_date
        self.end_date = end_date
        self.stocks_df = pd.DataFrame()
        self.OHLC = {}
        self.number_of_timeframes = 0

    def load_data(self):
        """
        This function will load data contain price of each stock in self.stocks variable and self.OHLC
        """
        print(self.stocks)
        self.stocks_df = pd.DataFrame()
        self.OHLC = {}
        for symbol in self.stocks:
            try:
                self.OHLC[symbol] = data_reader.get_OHLC(symbol)
                self.OHLC[symbol][self.OHLC[symbol]['close'].pct_change() <= 0.2]
            except:
                continue
            print(symbol)
            print(len(self.OHLC[symbol]))

        
        for symbol in self.OHLC.keys():
            if(len(self.OHLC[symbol])>36000):    #hard code to ensure we get three years data with not so much missing data
                self.stocks_df[symbol] = self.OHLC[symbol]['close'][:]
        self.stocks_df = self.stocks_df.dropna()[self.start_date:self.end_date]


    def create_signal(self):
        """
        This function will create long signal on each stock and save as csv
        """
        stocksignalCreater= SignalCreater(self.stocks_df,'W',must_coint = True)
        stocksignalCreater.create_mean_rev_data(plot = False)
        stocksignalCreater.create_trade_signal()
        self.number_of_timeframes = len(stocksignalCreater.mean_rev_data)



        stocks_1 = []
        stocks_2 = []
        z_score = []
        stock_name = []
        for i in range(0,len(stocksignalCreater.mean_rev_data)):
            df_stock_1 = stocksignalCreater.mean_rev_data[i]['df'][['stock_1','stock_1_pct','Signal']]
            df_stock_1.columns = ['close','pct','signal']
            stock_1 = stocksignalCreater.mean_rev_data[i]['stock_1']
            df_stock_1 = df_stock_1.join(self.OHLC[stock_1][['open','high','low']],how='left')
            df_stock_1 = df_stock_1[['open','high','low','close','pct','signal']]
            #df_stock_1.to_csv(f"{config.data_feed_path}/coint_stock_1_week{i}.csv")
            stocks_1.append(df_stock_1)

            df_stock_2 = stocksignalCreater.mean_rev_data[i]['df'][['stock_2','stock_2_pct','Signal']]
            df_stock_2.columns = ['close','pct','signal']
            stock_2 = stocksignalCreater.mean_rev_data[i]['stock_2']
            df_stock_2 = df_stock_2.join(self.OHLC[stock_2][['open','high','low']],how='left')
            df_stock_2 = df_stock_2[['open','high','low','close','pct','signal']]
            df_stock_2['signal'] = df_stock_2['signal'] * -1
            #df_stock_2.to_csv(f"{config.data_feed_path}/coint_stock_2_week{i}.csv")
            stocks_2.append(df_stock_2)

            df_z_score = stocksignalCreater.mean_rev_data[i]['df'][['z_score','Signal']]
            z_score.append(df_z_score)
            stock_name.append(stock_1)
            stock_name.append(stock_2)
            
        pd.DataFrame(stock_name).to_csv(f"{config.data_feed_path}/stock_name.csv")
        pd.concat(stocks_1).to_csv(f"{config.data_feed_path}/coint_stock_1_all.csv")
        pd.concat(stocks_2).to_csv(f"{config.data_feed_path}/coint_stock_2_all.csv")
        pd.concat(z_score).to_csv(f"{config.data_feed_path}/z_score.csv")