# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 17:17:31 2018

use wap of each level as the target, which make my conception very clearly
"""
import pandas as pd
import numpy as np
from collections import defaultdict
import datetime
import time
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import matplotlib.ticker as mtk
from sqlalchemy import create_engine 

engine = create_engine("mssql+pymssql://CENTALINE\zhangyun29:sh.9999@./invest")
#engine = create_engine("mssql+pymssql://sa:Pass0330@./invest")
cnx = engine.connect()

def get_k(stock_ID, cycle, tmStart = None, tmEnd = None ):
    str_sql = 'select * from ' + cycle + '_' +stock_ID
    df = pd.read_sql(str_sql, cnx)
    Ct = len(df)
    df.columns = ['Tm','O','H','L','C','V','A']
    df.index = df.Tm
    print 'dtCnt=',len(df)
    return df,Ct
    
class Stdk(object):
    def __init__(self,k):
        self.df =pd.DataFrame(k,index = [k.name],columns = k.index)
        self.df.iloc[0] = k
        self.df['drt'] = [0]
        
        self.nflag = 0
        
        
    def update(self,k):
        drt = self.df.drt[-1]
        ncd = ( self.df.H[-1]< k['H'] and self.df.L[-1] < k['L']) or (self.df.H[-1] > k['H'] and self.df.L[-1] > k['L'])
    
        tmpK = k
        self.nflag = 0
        if ncd:
            if self.df.H[-1] < k['H']:
                tmpK['drt'] = 1
            else:
                tmpK['drt'] = -1
            self.sprd(tmpK)
            self.df.loc[tmpK.name] = tmpK
            self.nflag = 1
        else:
            if drt == 1:
                tmpK['drt'] = drt
                if self.df.L[-1] == k['L'] and self.df.H[-1] < k['H']:
                    self.sprd(tmpK)
                    self.df.loc[tmpK.name] = tmpK
                    self.nflag = 1

                elif self.df.L[-1] > k['L'] and self.df.H[-1] < k['H']: 
                    self.stdCut(drt,tmpK,self.df.H[-1],self.df.L[-1])                
                    self.sprd(tmpK)
                    self.df.loc[tmpK.name] = tmpK
                    self.nflag = 1
                else:
                    self.stdCut(drt,tmpK,self.df.H[-1],self.df.L[-1]) 
                    self.sprd(tmpK)
                    tm = self.df.iloc[-1].name
                    self.df.loc[tm] = tmpK
                    
            elif drt == -1:
                tmpK['drt'] = drt
                if self.df.H[-1] == k['H'] and self.df.L[-1] > k['L']:
                    self.sprd(tmpK)
                    self.df.loc[tmpK.name] = tmpK
                    self.nflag = 1


                elif self.df.H[-1] < k['H'] and self.df.L[-1] > k['L']:
                    self.stdCut(drt,tmpK,self.df.H[-1],self.df.L[-1])                
                    self.sprd(tmpK)
                    self.df.loc[tmpK.name] = tmpK
                    self.nflag = 1
                
                else:
                    self.stdCut(drt,tmpK,self.df.H[-1],self.df.L[-1])                
                    self.sprd(tmpK)
                    tm = self.df.iloc[-1].name
                    self.df.loc[tm] = tmpK
                    
            elif drt == 0:
                tmpK['drt'] = drt
                self.stdCut(drt,tmpK,self.df.H[-1],self.df.L[-1])                
                self.sprd(tmpK)
                tm = self.df.iloc[-1].name
                self.df.loc[tm] = tmpK
        return True

    def stdCut(self,direction,k,H,L):
        if direction == 0:
            k.H = min(H,k.H)
            k.L = max(L,k.L)

        elif direction == 1:
            k.H = max(H,k.H)
            k.L = max(L,k.L)
        elif direction == -1:
            k.H = min(H,k.H)
            k.L = min(L,k.L)
        return True
        
    def sprd(self,k):
        if k.O <= k.C:
            k.O = k.L
            k.C = k.H
        else:            
            k.O = k.H
            k.C = k.L
        return True

class Lv0Td(object):
    def __init__(self,k):
        self.df = pd.DataFrame({'Tm_init':[k['Tm']]})
        #self.df.columns = ['Tm_init','V','drt','tdtype','k_ct','A','H80','L80']
        self.df['V'] = [k['O']]
        self.df['drt'] = [0]
        self.df['tdtype'] = [0]
        self.df['k_ct'] = [0]
        self.df['A'] = [0.0]
        self.df['H80'] = [k['H']]
        self.df['L80'] = [k['L']]
        self.df.index = [k['Tm']]
        
        self.cnt_dn = 2
        self.cnt_up = 2        
        self.nflag = 0
        
    def update(self,stdo,k):
        i = len(stdo.df) - 1
        #j = len(Lv1D['Tm']) - 1    
        self.cnt_up = self.cnt_up + 1
        self.cnt_dn = self.cnt_dn + 1
        self.nflag = 0    
        zig = 0    
        if i > 3:    
            zig = self.fPeak(i,stdo.df)

        if zig == 0:
            self.nflag = 0
        elif zig == -1:
            tmpP = pd.Series( {'Tm_init':k.name,'V': stdo.df.ix[i-2,'H'],'drt':zig},name = stdo.df.ix[i-2,'Tm'] )
            if (self.cnt_up >= 5) & (zig != self.df.ix[-1,'drt']):
                self.df.loc[tmpP.name] = tmpP
                self.cnt_dn = 2
                self.nflag = 1
            elif (zig == self.df.ix[-1,'drt']) & (stdo.df.ix[i-2,'H'] >= self.df.ix[-1,'V']):               
                self.df.iloc[-1] = tmpP
                self.df.index.values[-1] = tmpP.name
                self.cnt_dn = 2
                self.nflag = -1

        elif zig == 1:
            tmpP = pd.Series( {'Tm_init':k.name,'V': stdo.df.ix[i-2,'L'],'drt':zig},name = stdo.df.ix[i-2,'Tm'] )            
            if (self.cnt_dn >= 5) & (zig != self.df.ix[-1,'drt']):
                self.df.loc[tmpP.name] = tmpP 
                self.cnt_up = 2
                self.nflag = 1
            elif (zig == self.df.ix[-1,'drt']) & (stdo.df.ix[i-2,'L'] <= self.df.ix[-1,'V']):
                self.df.iloc[-1] = tmpP
                self.df.index.values[-1] = tmpP.name
                self.cnt_up = 2
                self.nflag = -1
        return True

    def fPeak(self,ii,df):
        if ii<3:
            zig =0
        else:
            if ( df.ix[ii-2,'H'] > df.ix[ii-3,'H'] ) & ( df.ix[ii-2,'H'] > df.ix[ii-1,'H'] ):
                zig = -1
            elif ( df.ix[ii-2,'L'] < df.ix[ii-3,'L']) & ( df.ix[ii-2,'L'] < df.ix[ii-1,'L'] ):
                zig = 1
            else:
                zig = 0 
        return zig
            
            
# =====================================================================
k_Df,dtCnt = get_k('600438','M30')
IdxL = k_Df.index.tolist()
firstk = k_Df.iloc[0]

stdk = Stdk(firstk.T)
Lv0 = Lv0Td(firstk.T)

for i in np.arange(1,dtCnt):
    begin = time.time()
    k = k_Df.iloc[i]
    stdk.update(k)
    print i,'k:',time.time() - begin, ' ',   
    
    begin = time.time()    
    if stdk.nflag == 1:
        begin = time.time() 
        Lv0.update(stdk,k)
        stdk.nflag = 0
    print i,'Lv0:',time.time() - begin
    
    
'''
stdrdf = stddf.loc[stddf.drt == 1,['O','H','L','C']]
stdgdf = stddf.loc[stddf.drt == -1,['O','H','L','C']]
drawpd = pd.merge(k_Df,stdrdf,on = 'Tm',how = 'left',suffixes = ['_k','_r'])
drawdf = pd.merge(drawpd,stdgdf, on='Tm',how= 'left')
fig,ax = plt.subplots(figsize = (100,40))
mpf.candlestick2_ochl(ax, k_Df.O,k_Df.H,k_Df.L,k_Df.C, width=0.6, colorup='w', colordown = 'w', alpha=0.15)
IdxS = range(0,dtCnt)
ax.vlines(IdxS,drawdf.L_r,drawdf.H_r,color = 'r',lw = 5)
ax.vlines(IdxS,drawdf.L,drawdf.H,color = 'g',lw = 5)
drlvdf.V_y = drlvdf.V_y.interpolate()
ax.plot(drlvdf.V_y.tolist())
ax.set_xlim(left = 0.0)
plt.savefig('000.png')
'''