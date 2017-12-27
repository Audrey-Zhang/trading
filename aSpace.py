# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 14:58:24 2017

@author: zhangyun29
"""

from collections import defaultdict
from sqlalchemy import create_engine 
import pandas as pd

#engine = create_engine("mssql+pymssql://CENTALINE\zhangyun29:sh.8888@./invest")
engine = create_engine("mssql+pymssql://sa:Pass0330@./invest")
cnx = engine.connect()


class aSpace():
    def __init__(self,symbol,tmCycle):
        self.StockID = symbol
        self.cycle = tmCycle
        self.k_Df = pd.DataFrame()
        self.stdD = defaultdict(list)
        self.Lv1D = defaultdict(list)
        self.Lv2D = defaultdict(list)
        self.distriD = defaultdict(list)
        
        