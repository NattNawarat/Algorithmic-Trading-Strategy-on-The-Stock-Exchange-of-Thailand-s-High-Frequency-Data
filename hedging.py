
import numpy as np
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import matplotlib.pyplot as plt
import mean_reversion_test as mean_reversion_test
import statsmodels.tsa.stattools as ts

    
def get_hedge_ratio(df,must_coint = True):
    """
    This function take DataFrame contain price of each stock
    to perform johansen test and use eigenvector as hedge ratio
    
    This function will return Dictionary contain test result as follow
    hedge_vector: a vector pf hedge ratio of each stock (use df.dot(hedge_vector) to create portfolio)
    adf_p_value: p value use to reject if portfolio is randomwalk
    hurrst_expo: value use to deetermine if portfolio is mean reverting(less than 0.5) geometric random walk(0.5) or has trend(more than 0.5)
    half_life: half life of mean reverting use to create rolling mean and std
    
    """
    result = {}
    stock_list = list(df.columns)
    m = len(stock_list)
    coint_trace_pass = np.zeros((m,m)) #store whether coint johansen test trace statistic pass 95% critical value
    result = {}
    for i in range(0,m):
        for j in range(i+1,m):
            stock_1 = stock_list[i]
            stock_2 = stock_list[j]
            interested_df = df[[stock_1,stock_2]]
            #perform johansen cointegration test to get hedge ratio
            johan_result = coint_johansen(np.array(interested_df),0,1)
            #print(johan_result.trace_stat[0] > johan_result.trace_stat_crit_vals[0][1])
            if(johan_result.trace_stat[0] > johan_result.trace_stat_crit_vals[0][1]) or not must_coint:
                # if 2 time series is cointegrate
                coint_trace_pass[i][j] = 1
                
                #get hedge ratio from eigenvector
                result[f"{stock_1}_{stock_2}"] = {'stock_1':stock_1,'stock_2':stock_2}
                result[f"{stock_1}_{stock_2}"]['hedge_vector'] = johan_result.evec.T[0]
                
                #create mean reversion port to perform adf test
                mean_rev_port = np.array(interested_df.dot(result[f"{stock_1}_{stock_2}"]['hedge_vector']))
                adf_p_value = ts.adfuller(mean_rev_port,maxlag = 1)[1] #p-value of adf test
                
                result[f"{stock_1}_{stock_2}"]['adf_p_value'] = adf_p_value
                
                #find hurst exponential
                hurst_expo = mean_reversion_test.hurst(np.array(mean_rev_port))
                
                result[f"{stock_1}_{stock_2}"]['hurst_expo'] = hurst_expo
                
                #Find mean reversion half-life (use to calculate sma)
                half_life = mean_reversion_test.half_life_mean_reversion(mean_rev_port)
                
                result[f"{stock_1}_{stock_2}"]['half_life'] = half_life
                
                #plt.plot(mean_rev_port)
                #plt.plot(mean_rev_port.rolling(int()))
                #plt.show()
                #print(result[f"{stock_1}_{stock_2}"])
            else:
                pass
    return result