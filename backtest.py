import pandas as pd
import signal_creator 
import matplotlib.pyplot as plt
import backtrader as bt
import copy
import config 

class GenericCSV_Extend(bt.feeds.GenericCSVData):
    lines = ('pct','signal')
    params = (('pct', 5),('signal', 6)) 


class PairTrading_long_only(bt.Strategy):
    params = {('oneplot', True)}
    def __init__(self):
        '''
        Create an dictionary of indicators so that we can dynamically add the
        indicators to the strategy using a loop. This mean the strategy will
        work with any numner of data feeds. 
        '''
        
        self.signal = dict()
        self.close = dict()
        for i, d in enumerate(self.datas):
            #print(d.signal[0])
            self.signal[d] = d.signal
            self.close[d] = d.close
            self.pct = d.pct
            if i > 0: #Check we are not on the first loop of data feed:
                if self.p.oneplot == True:
                    d.plotinfo.plotmaster = self.datas[0]

    def notify_order(self, order):
        #return
        global trade_log,trade_dict
        global port_val_log,port_val_dict
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            dt = str(self.data.datetime.date())+" "+str(self.data.datetime.time())
            if order.isbuy():
                print(f'BUY EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm {order.executed.comm}')
                print(f'PORT VALUE: {self.broker.getvalue()}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                trade_dict['EnterTS'] = copy.deepcopy(dt)
                trade_dict['EnterSize'] = copy.deepcopy(order.executed.size)
                trade_dict['EnterPrice'] = copy.deepcopy(order.executed.price)
                trade_dict['EnterComm'] = copy.deepcopy(order.executed.comm)
                trade_dict['EnterValue'] = copy.deepcopy(order.executed.value)
                trade_dict['EnterPortValue'] = copy.deepcopy(self.broker.getvalue())
            else:  # Sell
                print(f'SELL EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm {order.executed.comm}')
                print(f'PORT VALUE: {self.broker.getvalue()}')
                trade_dict['ExitTS'] = copy.deepcopy(dt)
                trade_dict['ExitSize'] = copy.deepcopy(order.executed.size)
                trade_dict['ExitPrice'] = copy.deepcopy(order.executed.price)
                trade_dict['ExitComm'] = copy.deepcopy(order.executed.comm)
                trade_dict['ExitValue'] = copy.deepcopy(order.executed.value)
                trade_dict['ExitPortValue'] = copy.deepcopy(self.broker.getvalue())
                
                trade_log.append(copy.deepcopy(trade_dict))
            self.bar_executed = len(self)

        else:
            return
            if order.status in [order.Canceled]:
                print('Order Canceled')
            if order.status in [order.Rejected]:
                print('Order Rejected')
            if order.status in [order.Margin]:
                print('Order Margin')
        # Write down: no pending order
        self.order = None
                
                    
    def next(self):
        for i, d in enumerate(self.datas):
            
            pos = self.getposition(d).size
            #print(self.datas[0].datetime.time())
            #print(self.getposition(d).size)
            if pos == 0:  # no market / no orders
                if self.signal[d][0] == 1:
                    size = int((self.broker.get_cash()/(1+config.comission)) / self.close[d][0])
                    print(f"buy {size}")
                    self.buy(data=d, size = size)
                    #self.buy_bracket(data = d,stopprice=13.00,size = size,stop_loss)
            else:
                
                if self.signal[d][0] != 1:
                    size = self.getposition(d).size
                    self.sell(data=d, size = size)
        
        dt = str(self.data.datetime.date())+" "+str(self.data.datetime.time())
        port_val_dict['TS'] = copy.deepcopy(dt)
        port_val_dict['Position'] = copy.deepcopy(self.getposition(d).size)
        port_val_dict['PortValue'] = copy.deepcopy(self.broker.getvalue())
        port_val_log.append(copy.deepcopy(port_val_dict))



def run_backtest(stocks,start_date,end_date,start_cash):
    global trade_log,trade_dict,port_val_dict,port_val_log
    print(stocks)
    print(start_date)
    print(end_date)
    print(start_cash)
    trade_log = []
    trade_dict = {"EnterTS":  None,
            "EnterSize" : 0,
            "EnterPrice" : 0,
            "EnterComm" : 0,
            "EnterValue" : 0,
            "EnterPortValue" : 0,
            "ExitTS":  None,
            "ExitSize" : 0,
            "ExitPrice" : 0,
            "ExitComm" : 0,
            "ExitValue" : 0,
            "ExitPortValue" : 0
            }
    port_val_log = []
    port_val_dict = {"TS":None,
                    "PortValue": 0,
                    "Position": 0,
                    }
    BacktestDataPreprator = signal_creator.BacktestDataPreprator(stocks,start_date,end_date)
    BacktestDataPreprator.load_data()
    BacktestDataPreprator.create_signal()



    PnL = []
    result = []
    result_dict = {}


    #Create an instance of cerebro
    cerebro = bt.Cerebro()

    #Add our strategy
    cerebro.addstrategy(PairTrading_long_only, oneplot=False)
    #cerebro.addstrategy(maCross, oneplot=False)

    # Create a Data Feed
    data = GenericCSV_Extend(dataname=f"{config.data_feed_path}/coint_stock_1_all.csv",dtformat=('%Y-%m-%d %H:%M:%S'),timeframe=bt.TimeFrame.Minutes)
    # Add the Data Feed to Cerebro
    cerebro.adddata(data,name = "stock_1")
    data = GenericCSV_Extend(dataname=f"{config.data_feed_path}/coint_stock_2_all.csv",dtformat=('%Y-%m-%d %H:%M:%S'),timeframe=bt.TimeFrame.Minutes)
    # Add the Data Feed to Cerebro
    cerebro.adddata(data,name = "stock_2")

    cerebro.broker.setcommission(commission=config.comission)

    # Set our desired cash start
    cerebro.broker.setcash(start_cash)

    # Add analyzer for performance
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name="anl_ret")
        
    # Run over everything
    strategies = cerebro.run()

    #Get final portfolio Value
        
    portvalue = cerebro.broker.getvalue()
    pnl = portvalue/start_cash
    
    #Print out the final result
    print(f'Final Portfolio Value: ${portvalue}')
    print(f'P/L: {pnl}')
    
    #trade_log = pd.DataFrame(trade_log)   
    port_val_log = pd.DataFrame(port_val_log)
    result = pd.DataFrame(result)

    #trade_log['EnterTS'] = pd.to_datetime(trade_log['EnterTS'])
    #trade_log['ExitTS'] = pd.to_datetime(trade_log['ExitTS'])
    port_val_log['TS'] = pd.to_datetime(port_val_log['TS'])
    port_val_log.set_index('TS',inplace = True)
    #print(trade_log.head())
    #print(trade_log.tail())
    #print(port_val_log.head())
    #print(port_val_log.tail())
    #trade_log.to_csv(f"{config.result_feed_path}/trade_log.csv")
    port_val_log.to_csv(f"{config.result_feed_path}/port_val_log.csv")
    return_dict = {}
    return_dict["numbers_of_week"] = BacktestDataPreprator.number_of_timeframes
    return_dict["analysis"] = strategies[0].analyzers
    return_dict["start_cash"] = start_cash
    return_dict["end_cash"] = portvalue
    return_dict["port_val_log"] = port_val_log
    return return_dict

if __name__ == "__main__":
    start_date = "2018-01-01"
    end_date = "2020-01-01"
    stocks = config.BANK
    run_backtest(stocks,start_date,end_date,1000000)