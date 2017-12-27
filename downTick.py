# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 15:11:47 2017

@author: zhangyun29
"""

import numpy as np  
import pandas as pd  
import tushare as ts  
import datetime  
import time  
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#import pymssql
from sqlalchemy import create_engine 
engine = create_engine("mssql+pymssql://CENTALINE\zhangyun29:sh.8888@./invest")
cnx = engine.connect()

cal_dates = ts.trade_cal() #返回交易所日历，类型为DataFrame, calendarDate  isOpen  
  
#本地实现判断市场开市函数   
#date: str类型日期 eg.'2017-11-23'  
def is_open_day(date):  
    if date in cal_dates['calendarDate'].values:  
        return cal_dates[cal_dates['calendarDate']==date].iat[0,1]==1  
    return False  


#从TuShare获取tick data数据
#@symbol: str类型股票代码 eg.600030  
#@date: date类型日期  
def get_save_tick_data(symbol, date):  
    global sleep_time  
    res=True  
    str_date=str(date)
    form_name = 'tick_' + symbol
    if is_open_day(str_date):  
        try:   
            d=ts.get_tick_data(symbol,str_date,pause=0.1)   
        except IOError, msg:  
            print str(msg).decode('UTF-8')  
            sleep_time=min(sleep_time*2, 128)#每次下载失败后sleep_time翻倍，但是最大128s  
            print 'Get tick data error: symbol: '+ symbol + ', date: '+str_date+', sleep time is: '+str(sleep_time)  
            return res  
        else: 
            date_col = []
            for i in range(len(d)):
                date_col.append(date)
            d['date'] = date_col
            u_type = []
            for item in d['type']:
                u_item = item.decode('utf-8')
                u_type.append(u_item)
            d['type'] = u_type
            d.to_sql(form_name,cnx, if_exists = 'append',index = False,chunksize = 500)
            sleep_time=max(sleep_time/2, 2) #每次成功下载后sleep_time变为一半，但是至少2s  
            print 'Successfully download !, sleep time: '+str(sleep_time) + ' ' +str_date + ' ' +str(len(d))
            return res  

            
            
            
#获取从起始日期到截止日期中间的的所有日期，前后都是封闭区间          
def get_date_list(begin_date, end_date):          
    date_list = []  
    while begin_date <= end_date:  
        #date_str = str(begin_date)  
        date_list.append(begin_date)  
        begin_date += datetime.timedelta(days=1)  
    return date_list  
    
sleep_time = 2    
stock = '600438'    
dates=get_date_list(datetime.date(2017,10,1), datetime.date(2017,11,4))      
for date in dates:  
    if get_save_tick_data(stock, date):   
        time.sleep(sleep_time)  