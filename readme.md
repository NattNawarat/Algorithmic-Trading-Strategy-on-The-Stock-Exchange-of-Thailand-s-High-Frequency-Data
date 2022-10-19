# Algorithmic Trading Strategy on The Stock Exchange of Thailand’s High Frequency Data

This research project is about designing stock price prediction and algorithmic trading strategy on 
high-frequency data by constructing mean-reversion time series based on historical prices of all stock in a defined sector and statistical tests, 
including Johanson cointegration, Augmented Dickey-Fuller test, and Hurst Exponent
and applying Half-Life of Mean-Reversion to detect and predict prices movement to design a trading strategy

## Prerequisite
### Warning: This project was made to be compatible with author's data. Replicate this project could be very challenging and maybe impossible.
This project require user to provide Sector's price and Stocks's price in OHLC format (daily for Sector's price and 5 minutes interval for stocks' price in .csv format) by themself.
Please store Sector's price in "SectorPrice" directory and name file with this format "{Sector's name}.csv"
Please store Stock's price in "OHLC_5m" directory and name file with this format "{Stock's name}_5T.csv or .pkl"

data_cleaner.py and data_reader.py was design to handle with author's data which cannot be shown in the public. Hence,may not work with your data you have to find the way for data_reader.py to return dataframe of OHLC price in 5 minute interval according to your data. (you can ignore data_cleaner.py.) 

## Requirement
Software requirement and version when this project was made.
- Python 3.8.5
- NumPy 1.19.2
- Pandas 1.3.4
- Dash 2.0.0
- Matplotlib 3.2.2
- Backtrader 1.9.76.123
- Statsmodels 0.12.0


## How to run
 1. Make sure you have Sectors' s price and Stocks' s price in "SectorPrice" and "OHLC_5m" directory.
 2. run dashboard.py
