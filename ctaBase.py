# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 09:39:37 2017

@author: zhangyun29
"""
import pandas as pd
import numpy as np
from collections import defaultdict
from sqlalchemy import create_engine 

#engine = create_engine("mssql+pymssql://CENTALINE\zhangyun29:sh.8888@./invest")
engine = create_engine("mssql+pymssql://sa:Pass0330@./invest")
cnx = engine.connect()

from aSpace import *

symbol = '600438'
cycle = 'D'
aS = aSpace(symbol,cycle)

class hisBarData(object):
    """K线数据"""
    def __init__(self):
        
        self.get_k(aS.StockID,aS.cycle)
        return None
        
    def get_k(self,stock_ID, cycle, tmStart = None, tmEnd = None ):
        str_sql = 'select * from ' + cycle + '_' +stock_ID
        aS.k_Df = pd.read_sql(str_sql, cnx)
        #dtCnt = len(df)
        aS.k_Df.columns = ['Tm','O','H','L','C','V','A']
        return True



class anaDataSpace(object):

    stdD = defaultdict(list)
    Lv1D = defaultdict(list)
    Lv2D = defaultdict(list)
    distriD = defaultdict(list)
    
    def __init__(self, stock_ID, cycle, tmStart = None, tmEnd = None ):
        """Constructor"""
        self.k_Df = pd.DataFrame()        
        self.stock_ID = stock_ID
        self.cycle = cycle
        return None
         
        