# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 11:18:12 2017
dl_xxx()
gen_xx()
check_existed()
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

def check_existed(Circle,StockID):
    str_sql = 'select Stock_ID from db_status where '+ Circle + '= 1' 
    aldt = pd.read_sql(str_sql,cnx)
    alL = aldt['Stock_ID'].values.tolist()
    if StockID in alL:
        return True
    else:
        return False
   
    
def dl_Tick(dateStart, dateEnd, SymbolList):
    cal_dates = ts.trade_cal()
    date = cal_dates[(cal_dates.calendarDate>=dateStart)&(cal_dates.calendarDate < dateEnd)&(cal_dates.isOpen ==1)]
    date.columns=[u'date',u'isOpen']
    sleep_time = 2    
    
    for symbol in SymbolList:
        if check_existed('Tick',symbol):   #if 这个周期、股票已有数据，需求待导入日期与已存在日期的差集 
            print 'existed',
            str_sql = 'select date,count(1) as a from tick_'+symbol +' group by date'  
            aldt = pd.read_sql(str_sql,cnx)
            dt = pd.merge(date,aldt,how='left',on='date')
            dt = dt[dt.a.isnull()]
            existF = True
        else:
            print 'not existed',
            dt = date 
            existF = False
            
        for i,r in dt.iterrows():
            begin = datetime.datetime.now()   
            str_date=str(r[0])
            str_sql = 'tick_' + symbol
            try:
                d = ts.get_tick_data(symbol, str_date, pause = 0.1)
                d['date'] = r[0]
                print str(len(d)),
            except IOError,msg:
                print str(msg).decode('UTF-8'),
                sleep_time = min(sleep_time*2,128) #每次下载失败后sleep_time翻倍，但是最大128s  
                
            else:
                if len(d) > 9:  ##TuShare即便在停牌期间也会返回tick data，并且只有三行错误的数据，这里利用行数小于10把那些unexpected tickdata数据排除掉              
                    d.to_sql(str_sql,cnx, if_exists = 'append',index = False,chunksize = 500)
                    sleep_time=max(sleep_time/2, 2) #每次成功下载后sleep_time变为一半，但是至少2s 
                    if existF == False: 
                        existF = True
                        str_sql = 'update db_status set Tick = 1 where Stock_ID = ' +symbol
                        cnx.execute(str_sql)
                    print str_date,' ',symbol,' ',
                else:
                    print str_date,u' stock suspending... ',
                timer = datetime.datetime.now() - begin
                print str(timer)
                time.sleep(sleep_time)

                
    return True
    
def dl_M1(SymbolList):
    
    return True

def gen_M1(dateStart, dateEnd, SymbolList):
    
    return True
    
def gen_D(SymbolList):
    for symbol in SymbolList:
        
        if check_existed('Tick',symbol):
            str_sql = 'select * from Tick_' + symbol
            d = pd.read_sql(str_sql,cnx)
            d['time'] = d['date'] +' '+ d['time']
            d['time'] = pd.to_datetime(d['time'])
            d = d.set_index('time')
            price_df = d['price'].resample('D').ohlc()
            vols=d['volume'].resample('D').sum()
            vols=vols.dropna()
            vol_df=pd.DataFrame(vols,columns=['volume'])
            amounts=d['amount'].resample('D').sum()  
            amounts=amounts.dropna()  
            amount_df=pd.DataFrame(amounts,columns=['amount'])  
            df = price_df.merge(vol_df,left_index = True,right_index=True).merge(amount_df,left_index = True, right_index=True)
            
            str_sql = 'D_' + symbol
            df.to_sql(str_sql,cnx, if_exists = 'append',chunksize = 500)
            
            str_sql = 'update db_status set D = 1 where Stock_ID = ' +symbol
            cnx.execute(str_sql) 
            print 'D_'+ str(symbol)+' Done!'
        else:
            print 'Tick data have not ready!'
     
    return True     
     
     
