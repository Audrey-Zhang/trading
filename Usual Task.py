# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 21:19:36 2017

@author: zhangyun29
"""

import pandas as pd
import tushare as ts  
import datetime  
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from sqlalchemy import create_engine 
#engine = create_engine("mssql+pymssql://CENTALINE\zhangyun29:sh.8888@./invest")
engine = create_engine("mssql+pymssql://sa:Pass0330@./invest")
cnx = engine.connect()

# ============my lib===============
import dtDownload as dtd

dts = '2018-01-01'
dte = '2018-03-07'
sbL = ['300231','300290','002279','603138','603881','300608',
       '300609','300166','300541','300245','000717','603322',
       '000004','002288','002225','002886','002310','600516',
       '000735','002320','600555','000886','600717','002177']
#sbL = ['002177']

dtd.dl_Tick(dts,dte,sbL)
#dtd.gen_D(sbL)
'''
import dtDownload as dtd
sbL = ['600438']
dtd.gen_D(sbL)
dtd.gen_1Min(sbL)
dtd.gen_30Min(sbL)
'''