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

#engine = create_engine("mssql+pymssql://CENTALINE\zhangyun29:sh.9999@./invest")
engine = create_engine("mssql+pymssql://sa:Pass0330@./invest")
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
            
class PC(object):
    def __init__(self,p1,p2):
        self.sTmS = p1[0]
        self.sTmE = p2[0]
        self.sVS = p1[1]
        self.sVE = p2[1]
        self.drt = p1[2]

        self.bH = 0.0
        self.bL = 0.0
        self.bLv_ct = 0
        self.bTmL = []
        self.bHL = []
        self.bLL = []

    def printpc(self):
        print self.sTmS,' ',self.drt,' ',self.bLv_ct,
    
    def updateB(self,p):
        if self.bLv_ct == 0:
            self.bTmL = [p[0]]
            self.bHL = self.bH = [max(self.sVE,p[1])]
            self.bLL = self.bL = [min(self.sVE,p[1])]
        else:
            self.bTmL.append(p[0])
            if p[2] == -1:
                self.bHL.append(min(self.bHL[-1],p[1]))
                self.bLL.append(self.bLL[-1])
            elif p[2] == 1:
                self.bLL.append(max(self.bHL[-1],p[1]))
                self.bHL.append(self.bLL[-1])
            else:
                print 'What!' 
        self.bLv_ct += 1
        print 'updateB',
        self.printpc()
        return True 
        
    def reset(self,p):
        f = 0
        point1 = 0
        if self.bLv_ct > 0:
            self.bLv_ct -= 1
            self.bTmL.pop()
            self.bHL.pop()
            self.bLL.pop()
            f,point1 = self.check(p)
            if f == 1:
                print 'reset PC',
                self.printpc()                 
                return f,point1
            print 'reset b',
            self.printpc()    
            self.updateB(p)
        else:
            self.sTmE = p[0]
            self.sVE = p[1]
            print 'reset s',
            self.printpc()    
        return f,point1

    def check(self,p):
        flag = 0
        point1 = [0.0,0,0]
        if self.bLv_ct > 0:
            if (p[2] == -1) and (p[1] > self.bHL[-1]):
                flag = 1
                point1 = [self.bTmL[-1],self.bLL[-1],1]
            elif (p[2] == 1) and (p[1] < self.bLL[-1]):
                flag = 1
                point1 = [self.bTmL[-1],self.bHL[-1],-1]
        else:
            if (p[2] == -1) and (p[1] > self.sVS):
                flag = -1
                point1 = [self.sTmE,self.sVE,1]
            elif (p[2] == 1) and (p[1] < self.sVS):
                flag = -1
                point1 = [self.sTmE,self.sVE,-1]
            
        return flag, point1
        
    def addB(self,p):
        self.bLv_ct =+ 1
        self.bTmL.append(p[0])
        self.bHL.append(self.bHL[-1])
        self.bLL.append(self.bLL[-1])
        return True

# =================Print Func==========================================
def pPCstick(pclist,kdf):
    IdxL = kdf.index    
    stickpl = []
    for i in pclist:
        tmp = [i.sTmS,i.sVS]
        stickpl.append(tmp)
        tmp = [i.sTmE,i.sVE]
        stickpl.append(tmp)
    df = pd.DataFrame(np.zeros(len(IdxL)),index = IdxL)
    pcsdf = pd.DataFrame(stickpl,columns = ['Tm','V'])
    pcsdf.index = pcsdf.Tm
    df = df.merge(pcsdf,how = 'left',left_index = True,right_index = True) 
    print df.index
    tmrl = []
    for i in pclist:
        tmp = [i.sTmS,i.sTmE]
        tmrl.append(tmp)
    dff = pd.DataFrame()
    for i in range(len(tmrl)):
        tmp = df.ix[tmrl[i][0]:tmrl[i][1],'V'].interpolate()
        if len(dff)==0:
            dff = tmp
        else:    
            dff = dff.append(tmp)
    dff = pd.DataFrame(dff,index = dff.index)
    df = df.merge(dff,how = 'left',left_index = True,right_index = True)
    printdf = df.pop('V_y')
    return printdf
    
def pPCblock(pclist,kdf):
    
    return True
    
def pLv0(lv_obj,kdf):
    IdxL = kdf.index
    l =lv_obj.df[['V','drt']]
    df = pd.DataFrame(np.zeros(len(IdxL)),index = IdxL)
    df = df.merge(l,how = 'left',left_index = True,right_index = True)
    lvS = df.V.interpolate()       
    
    return lvS
    
# =====================================================================
k_Df,dtCnt = get_k('600438','M30')
#dtCnt = 500
IdxL = k_Df.index.tolist()
firstk = k_Df.iloc[0]

stdk = Stdk(firstk.T)
Lv0 = Lv0Td(firstk.T)
PCL =[]

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
    
    if (Lv0.nflag == 1) & (len(Lv0.df) ==2 ):
        p1 = [Lv0.df.index[0],Lv0.df.V[0],Lv0.df.drt[0]]        
        p2 = [Lv0.df.index[1],Lv0.df.V[1],Lv0.df.drt[1]]
        tmpPC = PC(p1,p2)
        PCL=[tmpPC]
    if (Lv0.nflag == 1) & (len(PCL) > 0):
        p = [Lv0.df.index[-1],Lv0.df.V[-1],Lv0.df.drt[-1]]           
        f,p1 = PCL[-1].check(p)
        if f == 1:
            tmpPC = PC(p1,p)
            PCL.append(tmpPC)
        else:
            PCL[-1].updateB(p)
     
    elif (Lv0.nflag == -1) & (len(PCL) > 0):
        p = [Lv0.df.index[-1],Lv0.df.V[-1],Lv0.df.drt[-1]] 
        f,p1 =PCL[-1].reset(p)
        if f == 1:
            PCL.pop()
            PCL[-1].addB(p1)
            tmpPC = PC(p1,p)
            PCL.append(tmpPC)      
        
        
    Lv0.nflag = 0
    
    
'''
dtCnt = 500
kk = k_Df[0:dtCnt]
lv0s = pLv0(Lv0,kk)
pcss = pPCstick(PCL,kk)
stdrdf = stddf.loc[stddf.drt == 1,['O','H','L','C']]
stdgdf = stddf.loc[stddf.drt == -1,['O','H','L','C']]
drawpd = pd.merge(k_Df,stdrdf,on = 'Tm',how = 'left',suffixes = ['_k','_r'])
drawdf = pd.merge(drawpd,stdgdf, on='Tm',how= 'left')
fig,ax = plt.subplots(figsize = (100,40))
mpf.candlestick2_ochl(ax, kk.O,kk.H,kk.L,kk.C, width=0.6, colorup='w', colordown = 'w', alpha=0.15)
IdxS = range(0,dtCnt)
ax.vlines(IdxS,drawdf.L_r,drawdf.H_r,color = 'r',lw = 5)
ax.vlines(IdxS,drawdf.L,drawdf.H,color = 'g',lw = 5)
ax.plot(pcss.tolist())
ax.plot(lv0s.tolist())
ax.set_xlim(left = 0.0)
plt.savefig('000.png')
'''