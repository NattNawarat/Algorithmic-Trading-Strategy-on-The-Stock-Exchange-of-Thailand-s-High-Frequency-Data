import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
import pickle
import copy
import multiprocessing as mp
from config import stocks_list
def save(data , fn):
    with open(fn, 'wb') as f:
        pickle.dump(data, f)
def load(fn): 
    with open(fn, 'rb') as f:
        data = pickle.load(f)
        f.close()
    return data

def get_BestBid(BID):
    BestBid = np.zeros(len(BID))
    for i in range(0,len(BID)):
        for col in BID.columns:
            if BID[col].iloc[i] > 0:
                BestBid[i] = col
    return BestBid

def get_BidVolume(BID,BestBidVal):
        BidVolume = np.zeros((len(BID),5))
        BID_arr = np.array(BID)
        for i in range(len(BID)):
            BestBid = BestBidVal.iloc[i]
            BestBidColumn = list(BID.columns).index(BestBid)
            if BestBidColumn >= 4:
                BidVolume[i] = np.array(BID_arr[i,BestBidColumn-4:BestBidColumn+1]).reshape(1,-1)
            else:
                BidVolume[i,5-BestBidColumn -1:] = np.array(BID_arr[i,:BestBidColumn+1]).reshape(1,-1)
        BidVolume = pd.DataFrame(BidVolume,index = BID.index)
        return BidVolume
    
def get_OfferVolume(OFFER):
        BestOfferColumn = 0     
        OfferVolume = np.zeros((len(OFFER),5))
        OFFER_arr = np.array(OFFER)
        for i in range(len(OFFER)):
            #get BestOfferColumn
            for BestOfferColumn in range(len(OFFER.columns)):
                if OFFER_arr[i,BestOfferColumn] > 0:
                    break

            if BestOfferColumn + 4 < len(OFFER.columns):
                OfferVolume[i] = np.array(OFFER_arr[i,BestOfferColumn:BestOfferColumn+5]).reshape(1,-1)
            else:
                OfferVolume[i,:len(OFFER.columns)  - BestOfferColumn ] = np.array(OFFER_arr[i,BestOfferColumn:]).reshape(1,-1)
        OfferVolume = pd.DataFrame(OfferVolume,index = OFFER.index)
        return OfferVolume
        
def get_data_dict(arg):
        quote = arg[0]
        resample_str = arg[1]
        df = pd.DataFrame()
        Data = load( f'RAW DATA PATH' )
        OHLC_BID = {}
        BID_VOLUME = {}
        OFFER_VOLUME = {}
        for date in list(Data.keys()):
            print(quote + date)
            BID = {}
            BID = Data[date][0].between_time("10:05","16:25")
            OFFER = Data[date][1].between_time("10:05","16:25")

            BestBidVal = Data[date][2].between_time("10:05","16:25")['BestBid']
            BestBid = pd.DataFrame()
            BestBid['open'] = BestBidVal.resample(resample_str).first()
            BestBid['high'] = BestBidVal.resample(resample_str).max()
            BestBid['low'] = BestBidVal.resample(resample_str).min()
            BestBid['close'] = BestBidVal.resample(resample_str).last()
            BestBid = BestBid.shift(1).dropna()

            BidVolume = get_BidVolume(BID,BestBidVal)
            OfferVolume = get_OfferVolume(OFFER)

            BidVolume = BidVolume.resample(resample_str).last().shift(1).dropna()
            OfferVolume = OfferVolume.resample(resample_str).last().shift(1).dropna()
            OHLC_BID[date] = BestBid
            BID_VOLUME[date] = BidVolume
            OFFER_VOLUME[date] = OfferVolume
        data_dict = {"OHLC":OHLC_BID,
                     "BID":BID_VOLUME,
                     "OFFER":OFFER_VOLUME
                    }
        save(data_dict,f"./OHLC_5m/{quote}_{resample_str}.pkl")
  
if __name__ == "__main__":
    
    for stock in stocks_list["CONSUMP"] + stocks_list["AGRO"] + stocks_list["FINCIAL"] + stocks_list["RESOURC"] + stocks_list["INDUS"] + stocks_list["SERVICE"] + stocks_list["TECH"] + stocks_list["SET50"]:
        try:        
            print(stock)
            get_data_dict((stock,"5T"))

        except :
            continue
