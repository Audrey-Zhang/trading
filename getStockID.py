# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 14:46:48 2017

@author: zhangyun29

get stockID list, update by month
"""

import pandas as pd
import numpy as np
import tushare as ts
import pymssql
from sqlalchemy import create_engine 

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

df = ts.get_stock_basics()
#engine = create_engine("mssql+pymssql://CENTALINE\zhangyun29:sh.8888@./invest")
engine = create_engine("mssql+pymssql://sa:Pass0330@./invest")
cnx = engine.connect()

Stock_ID_df = df.loc[:,['name','industry']]
for i in range(len(df)):
    Stock_ID_df['name'][i] = Stock_ID_df['name'][i].decode('utf8')
    Stock_ID_df['industry'][i] = Stock_ID_df['industry'][i].decode('utf8')
    
Stock_ID_df['Stock_ID']=Stock_ID_df.index


Stock_ID_df.to_sql('dt_status',cnx,if_exists = 'append',index = False,chunksize = 500)