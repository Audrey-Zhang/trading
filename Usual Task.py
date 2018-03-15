# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 21:19:36 2017

@author: zhangyun29
"""

import pandas as pd
import tushare as ts  
import datetime  
import time 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from sqlalchemy import create_engine 
#engine = create_engine("mssql+pymssql://CENTALINE\zhangyun29:sh.8888@./invest")
engine = create_engine("mssql+pymssql://sa:Pass0330@./invest")
cnx = engine.connect()

# ============my lib===============
import dtDownload as dtd

def update_retrun_list():
    '''
    return current Stock_ID list  --ll
    insert new Stock_ID to db_status
    '''
    df_l = ts.get_stock_basics()  # generally use 2s
    time.sleep(5)
    ll = df_l.index.tolist()
    sql_str = 'SELECT Stock_ID from db_status'
    df_exist = pd.read_sql(sql_str,cnx)
    s1 = set(df_l.index);
    s2 = set(df_exist['Stock_ID'])
    new = s1 - s2
    print(len(new))
    df_new = df_l.loc[new,['name','industry']]
    df_new['Stock_ID'] = df_new.index
    df_new.to_sql('db_status', cnx, if_exists='append', index=False)
    return ll

sl = update_retrun_list()

dts = '2018-01-03'
dte = '2018-01-13'
sbL = ['300231','300290','002279','603138','603881','300608',
       '300609','300166','300541','300245','000717','603322',
       '000004','002288','002225','002886','002310','600516',
       '000735','002320','600555','000886','600717','002177']
#sbL = ['002177']

dtd.dl_Tick(dts,dte,sl)
#dtd.gen_D(sbL)
'''
import dtDownload as dtd
sbL = ['600438']
dtd.gen_D(sbL)
dtd.gen_1Min(sbL)
dtd.gen_30Min(sbL)
'''