import numpy as np
import pandas as pd
import backtest
import config


def cal_price_and_pct_return(df):
    for col in df.columns:
        df[f'{col}Ret'] = df[col].diff()
        df[f'{col}PctRet'] = df[col].pct_change()
    return df

def clean_sector_price_date_time(date):
    date_element = str(date).replace(" ","").split("/")
    if len(date_element[0]) == 1:
        date_element[0] = "0" + date_element[0]
    if len(date_element[1]) == 1:
        date_element[1] = "0" + date_element[1]
    if len(date_element[2]) == 2:
        date_element[2] = "20" + date_element[2]
    return f"{date_element[2]}-{date_element[1]}-{date_element[0]}"

def cal_CAGR(Array):
    number_of_days = len(Array)
    number_of_years = number_of_days/253
    EV_BV = Array[-1]/Array[0]
    CAGR = (np.power(EV_BV,1/number_of_years) - 1) *100
    return CAGR

def cal_profit(Array):
    print(Array[-1],Array[0])
    EV_BV = (Array[-1]/Array[0] - 1) * 100
    print(EV_BV)
    return EV_BV

def cal_drawdown(Array):
    max_price = Array[0]
    draw_down = np.zeros((len(Array),1))
    for i in range(len(Array)):
        curr_price = Array[i]
        if curr_price > max_price:
            max_price = curr_price
        draw_down[i] = (curr_price-max_price)/max_price*100
    return draw_down

def main(sector,start_date,end_date,start_cash):
    
    return_dict = backtest.run_backtest(stocks = config.stocks_list[sector],start_date = start_date,end_date = end_date,start_cash=start_cash)
    trade_analyzer = return_dict['analysis'].ta.rets


    port_val_log = return_dict['port_val_log']
    port_val_log['DD'] = cal_drawdown(np.array(port_val_log['PortValue']))
    port_val_log_daily = port_val_log.resample('D').first().ffill()

    sector_price = pd.read_csv(f"{config.sector_price_path}/{sector}.csv",dtype = {'Timestamp': str},thousands=',')
    sector_price['Timestamp'] = sector_price['Timestamp'].apply(clean_sector_price_date_time)
    sector_price['Timestamp'] = pd.to_datetime(sector_price['Timestamp'])
    sector_price.columns = ['TS','open','high','low','close','vol']
    sector_price.set_index('TS',inplace = True)

    sector_price['PortValue'] = port_val_log_daily['PortValue']

    benchmark_price = sector_price[['open','PortValue']]
    benchmark_price.columns = ['SectorPrice','BacktestPort']
    benchmark_price = benchmark_price.dropna()
    benchmark_price['SectorPort'] = benchmark_price['SectorPrice'] * (benchmark_price['BacktestPort'].iloc[0] / benchmark_price['SectorPrice'].iloc[0])
    benchmark_price = cal_price_and_pct_return(benchmark_price)
    benchmark_price['BackTestPortDD'] = cal_drawdown(np.array(benchmark_price['BacktestPort']))
    benchmark_price['SectorPriceDD'] = cal_drawdown(np.array(benchmark_price['SectorPrice']))

    trade_stats = {}
    ##backtest only value
    trade_stats["Won"] = int(trade_analyzer.won.total)
    trade_stats["Won Average"] = "{0:.2f}".format(trade_analyzer.won.pnl.average) + " THB"
    trade_stats["Lost"] = int(trade_analyzer.lost.total)
    trade_stats["Lost Average"] = "{0:.2f}".format(trade_analyzer.lost.pnl.average) + " THB"
    trade_stats["Trade Average"] = "{0:.2f}".format(trade_analyzer.pnl.net.average) + " THB"
    trade_stats["Number of Trade"] = int(trade_analyzer.total.total)
    trade_stats["SQN"] = "{0:.2f}".format(return_dict['analysis'].sqn.rets.sqn)

    backtest_stats = {}
    sector_stats = {}
    #benchmark and backtest value
    #Profit 
    backtest_stats["Profit"] = "{0:.2f}".format(cal_profit(np.array(benchmark_price['BacktestPort']))) + "%"
    sector_stats["Profit"] = "{0:.2f}".format(cal_profit(np.array(benchmark_price['SectorPrice']))) + "%"
    #CAGR
    backtest_stats["CAGR"] = "{0:.2f}".format(cal_CAGR(np.array(benchmark_price['BacktestPort']))) + "%"
    sector_stats["CAGR"] = "{0:.2f}".format(cal_CAGR(np.array(benchmark_price['SectorPrice']))) + "%"
    #Drawdown
    backtest_stats["max_dd"] = "{0:.2f}".format(benchmark_price['BackTestPortDD'].min()) + "%"
    sector_stats["max_dd"] = "{0:.2f}".format(benchmark_price['SectorPriceDD'].min()) + "%"
    #VAR
    backtest_stats["VAR"] = "{0:.2f}".format(benchmark_price['BacktestPortPctRet'].quantile(0.05)*100) + "%"
    sector_stats["VAR"] = "{0:.2f}".format(benchmark_price['SectorPricePctRet'].quantile(0.05)*100) + "%"
    #Sharpe Ratio
    backtest_stats["Sharpe Ratio"] = "{0:.4f}".format(benchmark_price['BacktestPortRet'].mean()/benchmark_price['BacktestPortRet'].std())
    sector_stats["Sharpe Ratio"] = "{0:.4f}".format(benchmark_price['SectorPriceRet'].mean()/benchmark_price['SectorPriceRet'].std())

    backtest_stats = pd.DataFrame.from_dict(backtest_stats,orient="index",columns = ["Backtest"])
    sector_stats = pd.DataFrame.from_dict(sector_stats,orient="index",columns = ["Sector"])

    benchmark_stats = backtest_stats.join(sector_stats).reset_index()
    benchmark_stats.columns = ['Values','Backtest','Sector']

    trade_stats = pd.DataFrame.from_dict(trade_stats,orient='index').reset_index()
    trade_stats.columns = ['Trade Statistc','Value']


    z_score = pd.read_csv(f"{config.data_feed_path}/z_score.csv")
    return trade_stats,benchmark_stats,port_val_log,benchmark_price,z_score

if __name__ == "__main__":
    main(sector = "BANK",start_date = "2019-01-01",end_date = "2020-01-01",start_cash =1000000)
