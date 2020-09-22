import numpy as np
import pandas as pd
import time
import gc

from bat import *

def get_data(fn):
    dt_df = pd.read_csv('e:\Work_python\\trading\\trading\data_csv\\'+fn,index_col=0,parse_dates=True)
    stockID =fn.split('.')[0]
    dt_df['TmIdx'] = list(range(0,dt_df.shape[0]))
    dt_df['tm'] =dt_df.index
    dt = dt_df[['open','high','low','close','TmIdx','tm']].values.tolist()
    del dt_df
    return dt, stockID

stock_fns = ['601012-1m.csv', '0600352.XSHG.csv']
for fn in stock_fns:    
    time_start=time.time()    
    dt, stockID = get_data(fn)
    m = Running(stockID, dt)
    m.play()
    m.reset_market()
    time_end=time.time()
    print('{} totally cost：{:.2f}'.format(stockID,time_end-time_start))

    dd = [obj.split('_')[0] for obj in Event.remark]
    rr = {}
    for kk in set(dd):
        rr[kk] = 0
        for oo in dd:
            if oo == kk:
                rr[kk] += 1
    print(rr)
   