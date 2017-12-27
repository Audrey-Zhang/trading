# -*- coding: utf-8 -*-
"""
Created on Wed Mar 01 23:00:04 2017

@author: ariesyun
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import matplotlib.ticker as mtk
from datetime import datetime, timedelta
import numba
import time

def stdCut(drt,tmpK,stdK):
    if drt == 0:
        ##print 'j=',j,stdArr[j][1],'i=',i,crtK[1],min(stdArr[j][1],crtK[1])
        #print tmpK.Tm 
        tmpK[1] = min(stdK[1],tmpK[1])
        tmpK[2] = max(stdK[2],tmpK[2])
        #print tmpK[1]
    elif drt == 1:
        tmpK[1] = max(stdK[1],tmpK[1])
        tmpK[2] = max(stdK[2],tmpK[2])
    elif drt == -1:
        tmpK[1] = min(stdK[1],tmpK[1])
        tmpK[2] = min(stdK[2],tmpK[2])


def sprd(tmpK):
    if tmpK[0] <= tmpK[3]:
        tmpK[0] = tmpK[2]
        tmpK[3] = tmpK[1]
    else:            
        tmpK[0] = tmpK[1]
        tmpK[3] = tmpK[2]

def std(crtK,stdArr,drt):
    j = len(stdArr) - 1   
    ncd = ( stdArr[j][1]< crtK[1] and stdArr[j][2] < crtK[2]) or (stdArr[j][1] > crtK[1] and stdArr[j][2] > crtK[2])
    
    tmpK = crtK
    preTm = stdArr[j][4]
    flag = 0
    if ncd:
        if stdArr[j][1] < crtK[1]:
            drt = 1
        else:
            drt = -1
        sprd(tmpK)
        stdArr.append(tmpK)
        flag = 1
        #print 'ncd=1,j=',j,'i=',i,'drt=',drt

    else:
        if drt == 1:
            if stdArr[j][2] == crtK[2] and stdArr[j][1] < crtK[1]:
                sprd(tmpK)
                stdArr.append(tmpK)
                flag = 1
                #print 'ncd=0,j=',j,'i=',i,'drt=',drt

            elif stdArr[j][2] > crtK[2] and stdArr[j][1] < crtK[1]: 
                stdCut(drt,tmpK,stdArr[j])                
                sprd(tmpK)
                stdArr.append(tmpK)
                flag = 1
                #print 'ncd=0,j=',j,'i=',i,'drt=',drt

            else:
                stdCut(drt,tmpK,stdArr[j]) 
                sprd(tmpK)
                stdArr.pop(j)
                tmpK[4] = preTm
                stdArr.append(tmpK)
                #print 'ncd=0,j=',j,'i=',i,'drt=',drt

        elif drt == -1:
            if stdArr[j][1] == crtK[1] and stdArr[j][2] > crtK[2]:
                sprd(tmpK)
                stdArr.append(tmpK)
                flag = 1
                #print 'ncd=0,j=',j,'i=',i,'drt=',drt

            elif stdArr[j][1] < crtK[1] and stdArr[j][2] > crtK[2]:
                stdCut(drt,tmpK,stdArr[j])                
                sprd(tmpK)
                stdArr.append(tmpK)
                flag = 1
                #print 'ncd=0,j=',j,'i=',i,'drt=',drt
                
            else:
                stdCut(drt,tmpK,stdArr[j])                
                sprd(tmpK)
                stdArr.pop(j)
                tmpK[4] = preTm
                stdArr.append(tmpK)
                #print 'ncd=0,j=',j,'i=',i,'drt=',drt

        elif drt == 0:
            stdCut(drt,tmpK,stdArr[j])                
            sprd(tmpK)
            stdArr.pop(j)
            tmpK[4] = preTm
            stdArr.append(tmpK)
            #print 'ncd=0,j=',j,'i=',i,'drt=',drt
        
    return stdArr,drt,flag

def fPeak(i,argDf):
    #print 'fPeak istd=',i    
    if i<3:
        zig =0
    else:
        if ( argDf[i-2][1] > argDf[i-3][1] ) & ( argDf[i-2][1] > argDf[i-1][1] ):
            zig = -1
        elif ( argDf[i-2][2] < argDf[i-3][2] ) & ( argDf[i-2][2] < argDf[i-1][2] ):
            zig = 1
        else:
            zig = 0 
    return zig

def fLvPeak(i,argDf):
      
    if i<3:
        zig =0
    else:
        if ( argDf[i-1][3] == 1) & ( argDf[i][3] == -1):
            zig = -1
        elif ( argDf[i-1][3] == -1 ) & ( argDf[i][3] == 1):
            zig = 1
        else:
            zig = 0 
    return zig    
#tmp = fPeak(29,stdDf)   
   
def Lv1(stdArr,Lv1Arr,cnt_up,cnt_dn): 
    i = len(stdArr) - 1
    j = len(Lv1Arr) - 1    
    cnt_up = cnt_up + 1
    cnt_dn = cnt_dn + 1
    zig = fPeak(i,stdArr)
    flag = 0
    if zig == 0:
        flag = 0
    elif zig == -1:
        tmpP = [stdArr[i-2][4],stdArr[i-2][1],zig]
        if (cnt_up >= 5) & (zig != Lv1Arr[j][2]):
            Lv1Arr.append(tmpP)
            cnt_dn = 2
            flag = 1
        elif (zig == Lv1Arr[j][2]) & (stdArr[i-2][1] >= Lv1Arr[j][1]):
            #print tmpP            
            Lv1Arr.pop(j)            
            Lv1Arr.append(tmpP)
            #print Lv1Df.loc[j]
            cnt_dn = 2
            flag = -1
            #print 'renewP','j=',j,'c_up=',cnt_up,'C_dn=',cnt_dn,tmpP
    elif zig == 1:
        tmpP = [stdArr[i-2][4],stdArr[i-2][2],zig]
        if (cnt_dn >= 5) & (zig != Lv1Arr[j][2]):
            Lv1Arr.append(tmpP)
            cnt_up = 2
            flag = 1
            #print 'newP','j=',j,'c_up=',cnt_up,'C_dn=',cnt_dn,tmpP
        elif (zig == Lv1Arr[j][2]) & (stdArr[i-2][2] <= Lv1Arr[j][1]):
            #print tmpP
            Lv1Arr.pop(j)            
            Lv1Arr.append(tmpP)
            #print Lv1Df.loc[j]
            cnt_up = 2
            flag = -1
            #print 'renewP','j=',j,'c_up=',cnt_up,'C_dn=',cnt_dn,tmpP
 
    return Lv1Arr,flag,cnt_up,cnt_dn


def stdLvCut(drt,stdArr,i,crtK):
    if drt == 0:
        crtK[1] = min(stdArr[i][1],crtK[1])
        crtK[0] = max(stdArr[i][0],crtK[0])
    elif drt == 1:
        crtK[1] = max(stdArr[i][1],crtK[1])
        crtK[0] = max(stdArr[i][0],crtK[0])
    elif drt == -1:
        crtK[1] = min(stdArr[i][1],crtK[1])
        crtK[0] = min(stdArr[i][0],crtK[0])
    return crtK


def stdLv(crtK,stdArr,i):
    ncd = (stdArr[i][1] < crtK[1] and stdArr[i][0] <= crtK[0]) or (stdArr[i][1] >= crtK[1] and stdArr[i][0] > crtK[0])
    tmpK =crtK
    flag = 0
    if ncd:
        if stdArr[i][1] < crtK[1]:
            tmpK[3] = 1
        else:
            tmpK[3] = -1
        stdArr.append(tmpK)
        flag = 1
    else:
        if stdArr[i][3] == 1:
            if stdArr[i][0] > crtK[0] and stdArr[i][1] < crtK[1]: 
                tmpK[3] = 1
                tmpK = stdLvCut(stdArr[i][3],stdArr,i,tmpK)                
                stdArr.append(tmpK)
                flag = 1
                #print 'ncd=0,j=',j,'i=',i,'drt=',drt

            else:
                tmpK[3] = 1
                tmpK = stdLvCut(stdArr[i][3],stdArr,i,tmpK)                
                poptmpK = stdArr.pop(i)
                tmpK[2] = poptmpK[2]
                stdArr.append(tmpK)
                #print 'ncd=0,j=',j,'i=',i,'drt=',drt

        elif stdArr[i][3] == -1:
            if stdArr[i][1] < crtK[1] and stdArr[i][0] > crtK[0]:
                tmpK[3] = -1
                tmpK = stdLvCut(stdArr[i][3],stdArr,i,tmpK)                
                stdArr.append(tmpK)
                flag = 1
                #print 'ncd=0,j=',j,'i=',i,'drt=',drt
                
            else:
                tmpK[3] = -1
                tmpK = stdLvCut(stdArr[i][3],stdArr,i,tmpK)                
                poptmpK = stdArr.pop(i)
                tmpK[2] = poptmpK[2]
                stdArr.append(tmpK)
                #print 'ncd=0,j=',j,'i=',i,'drt=',drt

        elif stdArr[i][3] == 0:
            tmpK[3] = 0
            tmpK = stdLvCut(stdArr[i][3],stdArr,i,tmpK)                
            poptmpK = stdArr.pop(i)
            tmpK[2] = poptmpK[2]
            stdArr.append(tmpK)
            #print 'ncd=0,j=',j,'i=',i,'drt=',drt
    return stdArr,tmpK[3],flag

def Lv2(argLv,stdArr,drt): 
    i = len(stdArr) - 1 
    j = len(argLv) - 1
    zig = fLvPeak(i,stdArr)
    flag = 0
    if zig == 0:
        flag = 0
    elif zig == -1 and zig == drt:
        tmpP = [stdArr[i-1][2],stdArr[i-1][1],zig]
        if zig != argLv[j][2]:
            argLv.append(tmpP)
            flag = 1
        elif (zig == argLv[j][2]) & (stdArr[i-1][1] >= argLv[j][1]):
            print tmpP            
            argLv.pop(j)
            argLv.append(tmpP)            
            flag = -1
            
    elif zig == 1 and zig == drt:
        tmpP = [stdArr[i-1][2],stdArr[i-1][0],zig]
        if zig != argLv[j][2]:
            argLv.append(tmpP)
            flag = 1
            
        elif (zig == argLv[j][2]) & (stdArr[i-1][0] <= argLv[j][1]):
            print tmpP
            argLv.pop(j)
            argLv.append(tmpP) 
            flag = -1
 
    return argLv,flag

def reLvLCnt(LvHA,LvLA):
    '''
    Drt_LvL = 1, LvH = -1, std_btm;
    Drt_LvL = -1,LvH =  1, std_tp
    '''
    iLvHA = len(LvHA)-1 
    print 'reLvLcnt'     

    TmLvH = datetime.strptime(LvHA[iLvHA][0],'%Y/%m/%d %H:%M:%S')
    arr = range(0,len(LvLA))
    LvLCnt = 0
    for i in reversed(arr):
        TmLvL = datetime.strptime(LvLA[i][0],'%Y/%m/%d %H:%M:%S')
        if TmLvH < TmLvL:
            LvLCnt = LvLCnt + 1
        else:
            print 'break: LvLCnt=', LvLCnt, 'iLvHA=',iLvHA           
            break
    return LvLCnt
            
def get_curLv(LvArr,curK):
    j = len(LvArr) - 1
    if LvArr[j-1][2] == 1:
        if curK[1] >= LvArr[j][1]:
            curLvStk = [LvArr[j-1],LvArr[j]]
        else:
            curLvStk = [LvArr[j],[curK[4],curK[2],1]]
    else:
        if curK[2] <= LvArr[j][1]:
            curLvStk = [LvArr[j-1],LvArr[j]]
        else:
            curLvStk = [LvArr[j],[curK[4],curK[1],-1]]
    return curLvStk
    
def tmDif(strTm1,strTm2,listA = None):
    if listA == None:    
        dif = idxS.index(strTm2) - idxS.index(strTm1)
    else:
        tmp = [x[0] for x in listA]
        dif = tmp.index(strTm2) - tmp.index(strTm1)
    return dif


def get_N(LvArr,curLvStk):
    j = len(LvArr) - 1
    N1 = [LvArr[j-3],LvArr[j-2]]
    N2 = [LvArr[j-2],LvArr[j-1]]
    N3 = curLvStk
        
    
    sf1 = evaLv(N1)
    sf2 = evaLv(N2)
    sf3 = evaLv(N3)
    drt = sf1[3]
    
    Ntype = 0    
    if sf1[0] > 5 and sf3[0] > 5:
        if drt == 1 and LvArr[j-3][1]<= LvArr[j-1][1]:
             Ntype = 1
        elif drt == -1 and LvArr[j-3][1]>= LvArr[j-1][1]:
            Ntype = 1
        
    return Ntype, drt

def get_CT():
    pass

def evaLv(curLvStk):
    LvLen = abs ( curLvStk[0][1] - curLvStk[1][1])
    tmLen = tmDif(curLvStk[0][0],curLvStk[1][0])
    k = LvLen / tmLen
    drt = curLvStk[0][2]
    return LvLen,tmLen,k,drt

def evaN():
    pass

def get_rpArr(LvArr,idx):
    rp1 = []
    rp2 = []    
    for i in range(idx,len(LvArr)-3):
        drt = LvArr[i][2]
        if drt == 1:
            mid = min(LvArr[i+1][1],LvArr[i+3][1]) - max(LvArr[i][1],LvArr[i+2][1])
            rp1.append(mid / abs(LvArr[i+1][1] - LvArr[i][1]))
            rp2.append(mid / abs(LvArr[i+3][1] - LvArr[i+2][1]))
        elif drt == -1:
            mid = min(LvArr[i][1],LvArr[i+2][1]) - max(LvArr[i+1][1],LvArr[i+3][1])
            rp1.append(mid / abs(LvArr[i+1][1] - LvArr[i][1]))
            rp2.append(mid / abs(LvArr[i+3][1] - LvArr[i+2][1]))
        else:
            pass
    return rp1,rp2
            
def get_rp(LvArr,i):
    drt = LvArr[i][2]
    rp1 = []
    rp2 = [] 
    if drt == 1:
        mid = min(LvArr[i+1][1],LvArr[i+3][1]) - max(LvArr[i][1],LvArr[i+2][1])
        rp1 = mid / abs(LvArr[i+1][1] - LvArr[i][1])
        rp2 = mid / abs(LvArr[i+3][1] - LvArr[i+2][1])
    elif drt == -1:
        mid = min(LvArr[i][1],LvArr[i+2][1]) - max(LvArr[i+1][1],LvArr[i+3][1])
        rp1 = mid / abs(LvArr[i+1][1] - LvArr[i][1])
        rp2 = mid / abs(LvArr[i+3][1] - LvArr[i+2][1])
    else:
        pass
    return rp1,rp2      
    
def center(CtArr,LvArr):
    i = len(LvArr) - 1
    j = len(CtArr) - 1    
    tmpCt = CtArr[j]
    #if LvArr[i][]
    
#===========================main initial=====================================  
'''      
df = pd.read_csv(file)
df.columns = ['Date','Tm','O','H','L','C','V'] 
dtCnt = len(df) 
dtCnt = 1500
   
idxS = pd.Series(dtype = str)
idxS = [' ']

for i in range(0,dtCnt):
    if i == 0:
        idxS[0] = df.Date[0] + ' ' + df.Tm[0]
    else:
        idxS.append(df.Date[i] + ' ' + df.Tm[i])

#===========================Loop K initial=====================================
#drt_Lv1 = 0
mark = []
sigA = []

stdA = [[df.O[0],df.H[0],df.L[0],df.C[0],idxS[0]]]
drt_std = 0

Lv1A = [[idxS[0],df.O[0], 0]]
cnt_up_Lv1 = 2
cnt_dn_Lv1 = 2

Lv2A = [[idxS[0],df.O[0], 0]]
#std_tp/btm

for i in range(1,dtCnt):
    #print '============================='    
  
    currentK = [df.O[i],df.H[i],df.L[i],df.C[i],idxS[i]]
    Fstd = 0
    FLv1 = 0
    FLv2 = 0
    stdA,drt_std,Fstd = std(currentK,stdA,drt_std)
    istd = len(stdA) -1

    
    if istd > 3 and Fstd == 1:
        Lv1A,FLv1,cnt_up_Lv1,cnt_dn_Lv1 = Lv1(stdA,Lv1A,cnt_up_Lv1,cnt_dn_Lv1)
    iLv1 = len(Lv1A) - 1
    if (FLv1 == 1 or FLv1 == -1) and iLv1 > 2:
        mark.append([i,Lv1A[iLv1][1],'lv1'])  
        rp1,rp2 = get_rp(Lv1A,iLv1-3)
        txt = '{:.2}'.format(rp1) +','+ '{:.2}'.format(rp2)
        mark.append([i,Lv1A[iLv1][1]+1,txt])
    
    if iLv1 == 3 and FLv1 == 1 and Fstd == 1:
        
        if Lv1A[2][2] == 1: 
            std_btm =[[Lv1A[0][1],Lv1A[1][1],Lv1A[0][0],0]]
            std_tp =[[Lv1A[2][1],Lv1A[1][1],Lv1A[1][0],0]]            
            
        elif Lv1A[2][2] == -1:
            std_tp =[[Lv1A[1][1],Lv1A[0][1],Lv1A[0][0],0]]
            std_btm =[[Lv1A[1][1],Lv1A[2][1],Lv1A[1][0],0]]
        drt_st = 0
        drt_sb = 0            
    

    if iLv1 > 3 and FLv1 == 1 and Fstd == 1:
                
        itp = len(std_tp) - 1
        ibtm = len(std_btm) - 1
        if Lv1A[iLv1][2] == 1:
            tmpK = [Lv1A[iLv1-2][1],Lv1A[iLv1-1][1],Lv1A[iLv1-2][0],0]
            std_btm,drt_sb,stdbAF = stdLv(tmpK,std_btm,ibtm)
                      
            
            if stdbAF == 1 and ibtm > 2:
                Lv2A,FLv2 = Lv2(Lv2A,std_btm,1)
        
        elif Lv1A[iLv1][2] == -1:
            tmpK = [Lv1A[iLv1-1][1],Lv1A[iLv1-2][1],Lv1A[iLv1-2][0],0]
            std_tp,drt_st,stdtAF = stdLv(tmpK,std_tp,itp)
            
            
            if stdtAF == 1 and itp > 2:
                Lv2A,FLv2 = Lv2(Lv2A,std_tp,-1)
    iLv2 = len(Lv2A) - 1
    if FLv2 == 1:
        mark.append([i,Lv2A[iLv2][1],'lv2'])
        
                
    #================================Strategy==================================

    LvH: 1. n > 4； 2. 进行性老化*
    LvL: 1. 过阈值； 2. 大笔*

    if len(Lv1A) > 4 and Fstd == 1:    
        
        n = 0
        if Lv1A[iLv1][2] == Lv2A[iLv2][2] and Lv2A[iLv2][2] != 0:
            thread = Lv1A[iLv1][1]
            print 'thread=i,',thread,'iLv1',iLv1,Lv1A[iLv1][2],'iLv2',iLv2,Lv2A[iLv2][2]
        elif Lv1A[iLv1-1][2] == Lv2A[iLv2][2] and Lv2A[iLv2][2] != 0: 
            thread = Lv1A[iLv1-1][1]
            print 'thread=i-1,',thread,Lv1A[iLv1][2],Lv2A[iLv2][2]
            

        if (Lv1A[iLv1][2] == 1 and Lv2A[iLv2][2] == -1 and df.H[i] > thread ) or (Lv1A[iLv1][2] == -1 and Lv2A[iLv2][2] == 1 and df.L[i] < thread):
            n = reLvLCnt(Lv2A,Lv1A)
        if n > 4:
            sigA.append([i,df.C[i],'sg'])
        
        
####=====================================Draw==================================

start = time.time()
orgDf = df.iloc[0:dtCnt,2:6]

DstdA = []
for i in range(0,len(idxS)):
    DstdA.append([float('nan'),float('nan'),float('nan'),float('nan')])
for i in range(0,len(stdA)):
    DstdA[idxS.index(stdA[i][4])] = [stdA[i][0],stdA[i][1],stdA[i][2],stdA[i][3]]
DstdDf = pd.DataFrame(DstdA)
DstdDf.columns = ['O','H','L','C']


DLv1 = []
for i in range(0,len(idxS)):
    DLv1.append(float('nan'))
for i in range(0,len(Lv1A)):
    DLv1[idxS.index(Lv1A[i][0])] = Lv1A[i][1]
DLv1S = pd.Series(DLv1)
DLv1S = DLv1S.interpolate()

DLv2 = []
for i in range(0,len(idxS)):
    DLv2.append(float('nan'))
for i in range(0,len(Lv2A)):
    DLv2[idxS.index(Lv2A[i][0])] = Lv2A[i][1]
DLv2S = pd.Series(DLv2)
DLv2S = DLv2S.interpolate()

def drawLvStd(ax,stdArr,vlcolor):
    xxx = range(0,dtCnt)
    ymin = []
    ymax = []
    for i in range(0,len(idxS)):
        ymin.append(float('nan'))
        ymax.append(float('nan'))
    for i in range(0,len(stdArr)):
        ymin[idxS.index(stdArr[i][2])] = stdArr[i][0]
        ymax[idxS.index(stdArr[i][2])] = stdArr[i][1]
    ax.vlines(xxx,ymin,ymax,color = vlcolor,lw = 5,alpha=0.75)
    

def x_fmt_func(x,pos=None):
    idx = np.clip(int(x+0.5),0, dtCnt-1)  
    print "x=", x
    return idxS[idx]

def candlestickz(ax,o,h,l,c):
    pass

def dwAxO(ax,os,hs,ls,cs):
    mpf.candlestick2_ochl(ax, os,hs,ls,cs, width=0.6, colorup='w', colordown = 'w', alpha=0.15)
    ax1.set_xlim(left = 0.0)    
    #tmp = ax.get_xlim()[0]
    #print tmp
    
def dwAxStd(ax,os,hs,ls,cs):
    mpf.candlestick2_ochl(ax, os,hs,ls,cs, width=0.6, colorup='r', colordown = 'g', alpha=0.75)
    ax1.set_xlim(left = 0.0)    
    #tmp = ax.get_xlim()[0]

    
fig, ax1 = plt.subplots(figsize=(int(dtCnt/3),40))
ax1.plot(DLv1S)
ax1.plot(DLv2S) 
drawLvStd(ax1,std_btm,'r')
drawLvStd(ax1,std_tp,'g')
for i in mark:
    plt.text(i[0],i[1],i[2],color = 'red', fontsize = 10)    
for i in sigA:
    plt.text(i[0],i[1],i[2],color = 'red', fontsize = 20)
    
#dwAxStd(ax1,DstdDf.O, DstdDf.H, DstdDf.L, DstdDf.C)
dwAxO(ax1,orgDf.O, orgDf.H, orgDf.L, orgDf.C)

ax1.xaxis.set_major_formatter(mtk.FuncFormatter(x_fmt_func))
#plt.show() 
plt.savefig('d:\Users\zhangyun29\Desktop\\1.png')
time_per_test = time.time()-start
'''