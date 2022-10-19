import pandas as pd
import pickle
import matplotlib.pyplot as plt

def save(data , fn):
    with open(fn, 'wb') as f:
        pickle.dump(data, f)


def load(fn): 
    with open(fn, 'rb') as f:
        data = pickle.load(f)
        f.close()
    return data


def slice_market_open(df):
    """
    This function will slice DataFrame to timeframe shic market is open only
    """
    df_morning = df.between_time("10:05","12:31")
    df_evening = df.between_time("14:35","16:31")
    return pd.concat([df_morning,df_evening])

def get_OHLC(quote):
    """
    This function will read OHLC and LOB data and return as DataFrame
    """
    DATA = load(f"/*YOUR SYSTEM PATH*/OHLC_5m/{quote}_5T.pkl")
    BID = pd.DataFrame()
    OFFER = pd.DataFrame()
    OHLC = pd.DataFrame()
    assert(len(DATA['BID'].keys()) == len(DATA['OFFER'].keys()))
    assert(len(DATA['OHLC'].keys()) == len(DATA['BID'].keys()))
    for date in DATA['BID'].keys():
        BID_today = slice_market_open(DATA['BID'][date])
        OFFER_today = slice_market_open(DATA['OFFER'][date])
        OHLC_today = slice_market_open(DATA['OHLC'][date])
        #OHLC_today['return_high'] = (OHLC_today['high'].shift(-1) - OHLC_today['close'])/OHLC_today['close']
        #OHLC_today['return_low'] = (OHLC_today['low'].shift(-1) - OHLC_today['close'])/OHLC_today['close']

        BID = pd.concat([BID,BID_today])
        OFFER = pd.concat([OFFER,OFFER_today])
        OHLC = pd.concat([OHLC,OHLC_today])
        #calculate return before concat (we do not need interday return)

    BID["All"] = BID.sum(axis = 1)
    OFFER["All"] = OFFER.sum(axis = 1)

    #BestBid will always at column 4 in BID
    #BestOdder will always at column 0 in OFFER
    BID = BID.add_prefix('BID_')
    OFFER = OFFER.add_prefix('OFFER_')

    LOB = BID.join(OFFER)
    LOB['OrderImbalance'] = (LOB['BID_All'] - LOB['OFFER_All'])/(LOB['BID_All'] + LOB['OFFER_All'])
    LOB['OrderImbalance (at the touch)'] = (LOB['BID_4'] - LOB['OFFER_0'])/(LOB['BID_4'] + LOB['OFFER_0'])
    OHLC['BestBidVolume'] = LOB['BID_4']
    OHLC['BestOfferVolume'] = LOB['OFFER_0']
    OHLC['OrderImbalance (at the touch)'] = LOB['OrderImbalance (at the touch)']
    OHLC['OrderImbalance'] = LOB['OrderImbalance']
    OHLC = OHLC.sort_index()
    OHLC = OHLC.dropna()
    OHLC['Volume'] = 0
    OHLC['Open Interested'] = 0
    return OHLC[['open','high','low','close','Volume','Open Interested','OrderImbalance (at the touch)','OrderImbalance','BestBidVolume','BestOfferVolume']]


