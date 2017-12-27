# -*- coding: utf-8 -*-
"""
init_analysis()

"""
import pandas as pd
import numpy as np
from collections import defaultdict
import datetime
from sqlalchemy import create_engine 
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import matplotlib.ticker as mtk

engine = create_engine("mssql+pymssql://CENTALINE\zhangyun29:sh.8888@./invest")
#engine = create_engine("mssql+pymssql://sa:Pass0330@./invest")
cnx = engine.connect()

k_Df = pd.DataFrame()
stdD = defaultdict(list)
Lv1D = defaultdict(list)
Lv2D = defaultdict(list)


def init_analysis():
    global stdD, Lv1D, k_Df, Fstd, FLv1
    stdD['Tm'] = [k_Df.Tm[0]]
    stdD['H'] = [k_Df.H[0]]
    stdD['L'] = [k_Df.L[0]]
    stdD['O'] = [k_Df.O[0]]
    stdD['C'] = [k_Df.C[0]]
    stdD['drt'] = [0]
   
    Lv1D['Tm'] = [k_Df.Tm[0]]
    Lv1D['V'] = [k_Df.O[0]]
    Lv1D['drt'] = [0] 
    Lv1D['cnt_dn'] = [2]
    Lv1D['cnt_up'] = [2]
    
    
    # =====init Flag==============
    Fstd = 0
    FLv1 = 0
      
    return True
    
def get_k(stock_ID, cycle, tmStart = None, tmEnd = None ):
    str_sql = 'select * from ' + cycle + '_' +stock_ID
    global k_Df
    k_Df = pd.read_sql(str_sql, cnx)
    #dtCnt = len(df)
    k_Df.columns = ['Tm','O','H','L','C','V','A']
    return True
 #  ======Big k ===============================================
def gen_bigk_spec(kDf, prec):
    aL = []
    for i in range(len(k_Df)):
        a = abs(k_Df.iloc[i,4] - k_Df.iloc[i,1])/ k_Df.iloc[i,1]
        a = a*100
        aL.append(a)
    al = np.array(aL)
    H = al.max()
    L = al.min()
    scaleL = np.arange(L,H,(H-L)/50)
    countL = np.zeros(50)
    for v in al:
        for i,s in enumerate(scaleL[1:]):
            if scaleL[i-1] <= v and v <s:
                countL[i-1] += 1
            
    count = countL.sum()
    count_precL = countL/count*100
    scaleL = np.arange(L,H,(H-L)/50)
    countL = np.zeros(50)
    for v in al:
        for i,s in enumerate(scaleL[1:]):
            if scaleL[i-1] <= v and v <s:
                countL[i-1] += 1
            
    count = countL.sum()
    count_precL = countL/count*100
    bigk = 0.0
    sumc = 0.0
    for i,v in enumerate(count_precL):
        sumc += v
        if sumc >= prec:
            bigk = scaleL[i+1]
            break
    return bigk  

def get_kA(ii,k_Df):
    a = abs(k_Df.iloc[i,4] - k_Df.iloc[i,1])/ k_Df.iloc[i,1]
    a = a*100
    return a    
 #  ==============STD==Begin===================================    
def std(i):
    global  k_Df,stdD, Lv1D, Fstd
    j = len(stdD['Tm']) - 1 
    drt = stdD['drt'][j]
    ncd = ( stdD['H'][j]< k_Df.H[i] and stdD['L'][j] < k_Df.L[i]) or (stdD['H'][j] > k_Df.H[i] and stdD['L'][j] > k_Df.L[i])
    
    tmpK = k_Df.ix[i,:] # ix is hard copy
    Fstd = 0
    if ncd:
        if stdD['H'][j] < k_Df.H[i]:
            drt = 1
        else:
            drt = -1
        sprd(tmpK)
        stdD['Tm'].append(tmpK[0]) 
        stdD['H'].append(tmpK[2])
        stdD['L'].append(tmpK[3])
        stdD['O'].append(tmpK[1])
        stdD['C'].append(tmpK[4])
        stdD['drt'].append(drt)
        Fstd = 1

    else:
        if drt == 1:
            if stdD['L'][j] == k_Df.L[i] and stdD['H'][j] < k_Df.H[i]:
                sprd(tmpK)
                stdD['Tm'].append(tmpK[0]) 
                stdD['H'].append(tmpK[2])
                stdD['L'].append(tmpK[3])
                stdD['O'].append(tmpK[1])
                stdD['C'].append(tmpK[4])
                stdD['drt'].append(drt)
                Fstd = 1

            elif stdD['L'][j] > k_Df.L[i] and stdD['H'][j] < k_Df.H[i]: 
                stdCut(drt,tmpK,stdD['H'][j],stdD['L'][j])                
                sprd(tmpK)
                stdD['Tm'].append(tmpK[0]) 
                stdD['H'].append(tmpK[2])
                stdD['L'].append(tmpK[3])
                stdD['O'].append(tmpK[1])
                stdD['C'].append(tmpK[4])
                stdD['drt'].append(drt)
                Fstd = 1

            else:
                stdCut(drt,tmpK,stdD['H'][j],stdD['L'][j]) 
                sprd(tmpK)
                stdD['H'][j] = tmpK[2]
                stdD['L'][j] = tmpK[3]
                stdD['O'][j] = tmpK[1]
                stdD['C'][j] = tmpK[4]
                

        elif drt == -1:
            if stdD['H'][j] == k_Df.H[i] and stdD['L'][j] > k_Df.L[i]:
                sprd(tmpK)
                stdD['Tm'].append(tmpK[0]) 
                stdD['H'].append(tmpK[2])
                stdD['L'].append(tmpK[3])
                stdD['O'].append(tmpK[1])
                stdD['C'].append(tmpK[4])
                stdD['drt'].append(drt)
                Fstd = 1


            elif stdD['H'][j] < k_Df.H[i] and stdD['L'][j] > k_Df.L[i]:
                stdCut(drt,tmpK,stdD['H'][j],stdD['L'][j])                
                sprd(tmpK)
                stdD['Tm'].append(tmpK[0]) 
                stdD['H'].append(tmpK[2])
                stdD['L'].append(tmpK[3])
                stdD['O'].append(tmpK[1])
                stdD['C'].append(tmpK[4])
                stdD['drt'].append(drt)
                Fstd = 1
                
            else:
                stdCut(drt,tmpK,stdD['H'][j],stdD['L'][j])                
                sprd(tmpK)
                stdD['H'][j] = tmpK[2]
                stdD['L'][j] = tmpK[3]
                stdD['O'][j] = tmpK[1]
                stdD['C'][j] = tmpK[4]
                

        elif drt == 0:
            stdCut(drt,tmpK,stdD['H'][j],stdD['L'][j])                
            sprd(tmpK)
            stdD['H'][j] = tmpK[2]
            stdD['L'][j] = tmpK[3]
            stdD['O'][j] = tmpK[1]
            stdD['C'][j] = tmpK[4]
            
    return True
    
def stdCut(drt,tmpK,stdH,stdL):
    if drt == 0:
        tmpK[2] = min(stdH,tmpK[2])
        tmpK[3] = max(stdL,tmpK[3])

    elif drt == 1:
        tmpK[2] = max(stdH,tmpK[2])
        tmpK[3] = max(stdL,tmpK[3])
    elif drt == -1:
        tmpK[2] = min(stdH,tmpK[2])
        tmpK[3] = min(stdL,tmpK[3])


def sprd(tmpK):
    if tmpK[1] <= tmpK[4]:
        tmpK[1] = tmpK[3]
        tmpK[4] = tmpK[2]
    else:            
        tmpK[1] = tmpK[2]
        tmpK[4] = tmpK[3]

#  ==============STD==End======================================== 
#  ==============Lv1==Start========================================         
def Lv1(): 
    global stdD, Lv1D, FLv1
    i = len(stdD['Tm']) - 1
    j = len(Lv1D['Tm']) - 1    
    cnt_up = Lv1D['cnt_up'][j] + 1
    cnt_dn = Lv1D['cnt_dn'][j] + 1
    FLv1 = 0    
    zig = 0    
    if i > 3:    
        zig = fPeak(i,stdD)

    if zig == 0:
        FLv1 = 0
        Lv1D['cnt_up'][j] = cnt_up
        Lv1D['cnt_dn'][j] = cnt_dn
    elif zig == -1:
        tmpP = [stdD['Tm'][i-2],stdD['H'][i-2],zig]
        if (cnt_up >= 5) & (zig != Lv1D['drt'][j]):
            Lv1D['Tm'].append(tmpP[0])
            Lv1D['V'].append(tmpP[1])
            Lv1D['drt'].append(tmpP[2])
            Lv1D['cnt_up'].append(cnt_up)
            Lv1D['cnt_dn'].append(2)
            FLv1 = 1
        elif (zig == Lv1D['drt'][j]) & (stdD['H'][i-2] >= Lv1D['V'][j]):
                   
            Lv1D['Tm'].pop(j)
            Lv1D['V'].pop(j)
            Lv1D['drt'].pop(j)
            Lv1D['cnt_up'].pop(j)
            Lv1D['cnt_dn'].pop(j)
            Lv1D['Tm'].append(tmpP[0])
            Lv1D['V'].append(tmpP[1])
            Lv1D['drt'].append(tmpP[2])
            Lv1D['cnt_up'].append(cnt_up)
            Lv1D['cnt_dn'].append(2)
            
            FLv1 = -1

    elif zig == 1:
        tmpP = [stdD['Tm'][i-2],stdD['L'][i-2],zig]
        if (cnt_dn >= 5) & (zig != Lv1D['drt'][j]):
            Lv1D['Tm'].append(tmpP[0])
            Lv1D['V'].append(tmpP[1])
            Lv1D['drt'].append(tmpP[2])
            Lv1D['cnt_up'].append(2)
            Lv1D['cnt_dn'].append(cnt_dn)            
            FLv1 = 1
        elif (zig == Lv1D['drt'][j]) & (stdD['L'][i-2] <= Lv1D['V'][j]):

            Lv1D['Tm'].pop(j)
            Lv1D['V'].pop(j)
            Lv1D['drt'].pop(j)
            Lv1D['cnt_up'].pop(j)
            Lv1D['cnt_dn'].pop(j)
            Lv1D['Tm'].append(tmpP[0])
            Lv1D['V'].append(tmpP[1])
            Lv1D['drt'].append(tmpP[2])
            Lv1D['cnt_up'].append(2)
            Lv1D['cnt_dn'].append(cnt_dn)              
            
            FLv1 = -1

    return True
   

def fPeak(i,argD):

    if i<3:
        zig =0
    else:
        if ( argD['H'][i-2] > argD['H'][i-3] ) & ( argD['H'][i-2] > argD['H'][i-1] ):
            zig = -1
        elif ( argD['L'][i-2] < argD['L'][i-3]) & ( argD['L'][i-2] < argD['L'][i-1] ):
            zig = 1
        else:
            zig = 0 
    return zig
#  ==============Lv1==End======================================== 
#  ==============Lv2==S======================================== 
class Lv2(object):
    def __init__(self, Lv1LD):
        self.D = defaultdict(list)
        self.LD = defaultdict(list)
        self.F = 0
        self.stdF = 0
        #self.std_btmL = []
        #self.std_tpL = []
        
        self.D['Tm'] = Lv1LD['Tm'][0]
        self.D['V'] = Lv1LD['V'][0]
        self.D['drt'] = 0
        for k in self.D:
            self.LD[k] = [self.D[k]]
        
        if Lv1LD['drt'][2] == 1:        
            self.std_btmL = [[Lv1LD['V'][0],Lv1LD['V'][1],Lv1LD['Tm'][0],0]]
            self.std_tpL =[[Lv1LD['V'][2],Lv1LD['V'][1],Lv1LD['Tm'][1],0]]
        elif Lv1LD['drt'][2] == -1: 
            self.std_tpL =[[Lv1LD['V'][1],Lv1LD['V'][0],Lv1LD['Tm'][0],0]]
            self.std_btmL =[[Lv1LD['V'][1],Lv1LD['V'][2],Lv1LD['Tm'][1],0]] 
        print 'initiated Lv2'

    def gen_Lv2(self,Lv1LD,TmC=None):
        if TmC is None:        
            ii = len(Lv1LD['Tm']) - 1
        else:
            ii = Lv1LD['Tm'].index(TmC)
        drt = Lv1LD['drt'][ii]
        if drt == 1:
            i = len(self.std_btmL) - 1
            stdArr = self.std_btmL
        elif drt == -1:
            i = len(self.std_tpL) - 1
            stdArr = self.std_tpL
        j = len(self.LD['Tm']) - 1
        zig = Lv2.fLvPeak(i,stdArr)
        if zig == 0:
            self.F = 0
        elif zig == -1 and zig == drt:
            self.D['Tm'] = stdArr[i-1][2]
            self.D['V'] = stdArr[i-1][1]
            self.D['drt'] = zig
            if zig != self.LD['drt'][j]:
                self.append_LD()
                self.F = 1
            elif (zig == self.LD['drt'][j]) & (stdArr[i-1][1] >= self.LD['V'][j]):
                self.update_LD()            
                self.F = -1
            
        elif zig == 1 and zig == drt:
            self.D['Tm'] = stdArr[i-1][2]
            self.D['V'] = stdArr[i-1][0]
            self.D['drt'] = zig            
            if zig != self.LD['drt'][j]:
                self.append_LD()
                self.F = 1
            
            elif (zig == self.LD['drt'][j]) & (stdArr[i-1][0] <= self.LD['V'][j]):
                self.update_LD()  
                self.F = -1
        return True   
    
    def gen_std_lvk(self,Lv1LD,TmC=None):
        if TmC is None:        
            i = len(Lv1LD['Tm']) - 1
        else:
            i = Lv1LD['Tm'].index(TmC)
        print 'i:',str(i),
        L = min(Lv1LD['V'][i-2],Lv1LD['V'][i-1])
        H = max(Lv1LD['V'][i-2],Lv1LD['V'][i-1])        
        new_Lv1k = [L,H,Lv1LD['Tm'][i-2],0]
        print ' ',str(L),' ',str(H),' ',str(new_Lv1k[2]),
        if Lv1LD['drt'][i] == 1:
            self.std_btmL = self.stdLv(new_Lv1k,self.std_btmL)
        elif Lv1LD['drt'][i] == -1: 
            self.std_tpL = self.stdLv(new_Lv1k,self.std_tpL)
        return True 
    
    @staticmethod    
    def fLvPeak(i,argkLL):      
        if i<3:
            zig =0
        else:
            if ( argkLL[i-1][3] == 1) & ( argkLL[i][3] == -1):
                zig = -1
            elif ( argkLL[i-1][3] == -1 ) & ( argkLL[i][3] == 1):
                zig = 1
            else:
                zig = 0 
        return zig    
        
    def stdLv(self,crtK,stdArr):
        i = len(stdArr) - 1
        ncd = (stdArr[i][1] < crtK[1] and stdArr[i][0] <= crtK[0]) or (stdArr[i][1] >= crtK[1] and stdArr[i][0] > crtK[0])
        tmpK =crtK
        self.stdF = 0
        if ncd:
            if stdArr[i][1] < crtK[1]:
                tmpK[3] = 1
            else:
                tmpK[3] = -1
            self.stdF = 1
            stdArr.append(tmpK)
        else:
            if stdArr[i][3] == 1:
                if stdArr[i][0] > crtK[0] and stdArr[i][1] < crtK[1]: 
                    tmpK[3] = 1
                    tmpK = Lv2.stdLvCut(stdArr[i][3],stdArr,i,tmpK)                
                    stdArr.append(tmpK)
                    self.stdF = 1
                else:
                    tmpK[3] = 1
                    tmpK = Lv2.stdLvCut(stdArr[i][3],stdArr,i,tmpK)                
                    poptmpK = stdArr.pop(i)
                    tmpK[2] = poptmpK[2]
                    stdArr.append(tmpK)

            elif stdArr[i][3] == -1:    
                if stdArr[i][1] < crtK[1] and stdArr[i][0] > crtK[0]:
                    tmpK[3] = -1
                    tmpK = Lv2.stdLvCut(stdArr[i][3],stdArr,i,tmpK)                
                    stdArr.append(tmpK) 
                    self.stdF = 1
                else:
                    tmpK[3] = -1
                    tmpK = Lv2.stdLvCut(stdArr[i][3],stdArr,i,tmpK)                
                    poptmpK = stdArr.pop(i)
                    tmpK[2] = poptmpK[2]
                    stdArr.append(tmpK)

            elif stdArr[i][3] == 0:
                tmpK[3] = 0
                tmpK = Lv2.stdLvCut(stdArr[i][3],stdArr,i,tmpK)                
                poptmpK = stdArr.pop(i)
                tmpK[2] = poptmpK[2]
                stdArr.append(tmpK)
        return stdArr    
    
    @staticmethod
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
    
    def append_LD(self):
        for k in self.D:
            self.LD[k].append(self.D[k]) 
        return True

    def update_LD(self):
        i = len(self.LD['Tm']) - 1
        for k in self.D:
            self.LD[k][i] = self.D[k]
        return True        


#  ==============Lv2==End========================================         

# =============distri =========================================
class Distri(object):
    sd = 20
    def __init__(self,kDf,TmStart):
        self.Tm_start = TmStart
        self.Lv_count = 0
        kL = float(kDf[kDf.Tm == TmStart].O)
        kH = float(kDf[kDf.Tm == TmStart].C)
        if kL < kH:
            self.drt = 1
        else:
            self.drt = -1
        self.LD = defaultdict(list)
        self.LD['TmS'].append(self.Tm_start)
        self.D = {
            'TmU':'',
            'L': 0.0,
            'H':0.0,
            'scale':[],
            'count':[],
            'k_count':0,
            'ap':0.0
        }
        self.F = 0
        
        self._df = pd.DataFrame()
        self._internal = 0.0

    def gen_D(self, TmUpdate, kDf, TmStart=None):
        #begin = datetime.datetime.now()
        
        if TmStart is not None:            
            self.Tm_start = TmStart
        self.D['TmU'] = TmUpdate
        self._df = kDf[(kDf.Tm >= self.Tm_start) & (kDf.Tm <= self.D['TmU'])]
        self.D['L'] = self._df['L'].min()
        self.D['H'] = self._df['H'].max()
        self._internal = (self.D['H'] - self.D['L'])/Distri.sd
        self.D['scale'] = np.arange(self.D['L'],self.D['H'], self._internal)
        self.D['count'] = np.zeros(Distri.sd)
        self.D['k_count'] = len(self._df)
        self.D['ap'] = self._df.C.mean()
        for i,r in self._df.iterrows():
            self.D['count'] = Distri.distri_k_to_scale(r,self.D['scale'],self.D['count'])        
        cc = CenterCore()
        cc.calcul_ccparam(self.D)
        for k in cc.D:
            kk = 'cc'+k
            self.D[kk] = cc.D[k]
        ss = Spec()
        ss.gen_features(cc.D['max_c'])
        ss.calcul_result()
        for k in ss.rD:
            self.D[k] = ss.rD[k]
        cd1 = self.D['r_total'] > 10

        C1 = self._df.iloc[0,1]
        C2 = self._df.iloc[-1,4] 
        if C1 < C2: 
            cd2 = self.D['ccpeak_start_i'][3] > 7
            cd3 = C2 < self.D['ccH'][3]
        else:
            cd2 = self.D['ccpeak_start_i'][3] < 12
            cd3 = C2 > self.D['ccL'][3]
        
        if cd1 and cd2 and cd3 and (self.F < 2) :
            self.F = 2
        if len(self.LD['TmU']) >0:
            self.check_drt()       
        #timer = datetime.datetime.now() - begin
        #print str(timer)
        return True
    
    def check_drt(self):
        if self.drt == 1 and self.LD['L'][0] > self._df.iloc[-1,4]:
            print 'delete !!!!!'
            self.F = 10            
            return False
        elif self.drt == -1 and self.LD['H'][0] < self._df.iloc[-1,4]:
            print 'delete !!!!!'
            self.F = 10            
            return False
        else:
            return True
            
    def update_LD(self):
        for k in self.D:
            self.LD[k].append(self.D[k])
        return True 
    
   
    @staticmethod
    def distri_k_to_scale(kD, scaleL, countL):
        # distribute one k to scale
        count_times = 1.0
        tm_unit_value = 1
        for scale in scaleL:
            if kD['L'] <= scale and scale <= kD['H']:
                count_times += 1
        count_unit = tm_unit_value / count_times

        for j,scale in enumerate(scaleL):
            if kD['L'] <= scale and scale <= kD['H']:
                countL[j] += count_unit
            
        return countL
        
    def get_D(self,i_or_Tm=None):    
        if i_or_Tm is None:
            d = self.D
        elif isinstance(i_or_Tm,int):
            i = i_or_Tm            
            d = {
                'TmU':self.LD['TmE'][i],
                'L':self.LD['L'][i],
                'H':self.LD['H'][i],
                'scale':self.LD['scale'][i],
                'count':self.LD['count'][i],
                'k_count':self.LD['k_count'][i]        
                }
        elif isinstance(i_or_Tm,pd.tslib.Timestamp):
            i = self.LD['TmU'].index(i_or_Tm)
            d = {
                'TmU':self.LD['TmE'][i],
                'L':self.LD['L'][i],
                'H':self.LD['H'][i],
                'scale':self.LD['scale'][i],
                'count':self.LD['count'][i],
                'k_count':self.LD['k_count'][i]        
                }
        return d 
    
    @staticmethod    
    def sendToLDL(DistriLDL,dd):
        DistriLDL.append(dd)
        return True

    @staticmethod
    def del_LD(DistriLDL,dd):
        i = DistriLDL.index(dd)
        DistriLDL.pop(i)
        return True
    
    @staticmethod
    def del_LD_before(DistriLDL,ddorT):
        if isinstance(ddorT, Distri):
            Tm = ddorT.Tm_start
        else:
            Tm = ddorT
        for i,item in DistriLDL:
            if item.Tm_start < Tm:
                DistriLDL.pop(i)
        return True
    
    @staticmethod
    def move_LD(DistriLDL_from,DistriLDL_to,dd):
        Distri.del_LD(DistriLDL_from,dd)
        Distri.sendToLDL(DistriLDL_to,dd)
        return True
        
    @classmethod
    def set_sd(cls,n):
        Distri.sd = n
        return True
            
    def kill_D(self,Tm,DistriLDL):
        if self.Tm_start < Tm:
            i = DistriLDL.index(self)
            DistriLDL.pop(i)
        return True  
        
    def calcul_wap(self):
        self._df.C.mean()
        return self.ap
    
# =============center core  =================================
class CenterCore(object):
    def __init__(self):
        self.swL = [10,9,8,7,6,5,4,3]
        self.scale_list = []
        self.count_list = []
        self.D = defaultdict(list)
        
        self.D['max_c'] = np.zeros(len(self.swL))
        self.D['peak_start_i'] = np.zeros(len(self.swL))
        self.D['wap'] = np.zeros(len(self.swL))
        self.D['H'] = np.zeros(len(self.swL))
        self.D['L'] = np.zeros(len(self.swL))
        #self.F = False
        return None
        
    def calcul_ccparam(self,distriD,scale_width_list = None):
        if scale_width_list is not None:
            self.swL = scale_width_list
        self.scale_list = distriD['scale']
        self.count_list = distriD['count']
        k_count = distriD['k_count']                
        if k_count > 4:
            for i,sw in enumerate(self.swL):    
                self.D['max_c'][i],idx = self.distri_scan(sw)
                self.D['peak_start_i'][i] = idx
                w = self.count_list[idx:idx+sw]
                p = self.scale_list[idx:idx+sw]
                self.D['wap'][i] = np.average(p,weights = w)
                self.D['H'][i] = p.max()
                self.D['L'][i] = p.min()
            return True
        else:
            return False
        
    def distri_scan(self,scale_width,scale_density= None):
        if scale_density is not None:
            sd = scale_density
        else:
            sd = 20
        sumL = []
        for i in range(sd-scale_width):
            sum = 0.0
            for j in range(scale_width):
                sum += self.count_list[i+j]
            sumL.append(sum)
        sumAll = self.count_list.sum()
        sumL = sumL/sumAll
        max_cctrn = sumL.max()
        l = list(sumL)
        i = l.index(max_cctrn)
        return max_cctrn, i
        
 
        
# =============center spec =================================    
class Spec(object):
    specL = [80,70,60,50]    
    center_threadA = [
        [1,0,0,0],
        [2,1,0,0],
        [2,1,0,0],
        [3,2,1,0],
        [3,2,1,0],
        [4,3,2,1],
        [4,3,3,2],
        [5,4,3,3]
    ]
    
    def __init__(self):
        self.featureA = []
        self.resultA = []
        self.rD = defaultdict(list)
        
        self.rD['r_ccL'] = []
        self.rD['r_tcL'] = []
        self.rD['r_total'] = 0        
        
        
    def gen_features(self,max_c_L):
        for v in max_c_L:
            f = []            
            for i in Spec.specL:
                if v*100 > i:
                    f.append(1)
                else:
                    f.append(0)
            self.featureA.append(f)
        return self.featureA
 
    def calcul_result(self):
        self.resultA = np.multiply(self.featureA,Spec.center_threadA)
        self.rD['r_ccL'] = self.resultA.sum(axis = 0)
        self.rD['r_tcL'] = self.resultA.sum(axis = 1)
        self.rD['r_total'] = self.resultA.sum()
        
    def gen_results(self):
        pass
        return True

# =============signal ====================================== 

# ==========================================================
def dt_to_csv(data,filenm):
   df = pd.DataFrame()    
   for k in data:
       df[k] = data[k]
   df.to_csv(filenm)  	
   
def to_dd(ddd,outdd):
    outdd['TmS'].append(ddd.Tm_start)    
    for k in ddd.D:
        outdd[k].append(ddd.D[k])

def dwAxO(ax,os,hs,ls,cs):
    mpf.candlestick2_ochl(ax, os,hs,ls,cs, width=0.6, colorup='w', colordown = 'w', alpha=0.15)
    ax.set_xlim(left = 0.0)

def get_ki(tm):     
    t = pd.Timestamp(tm)
    tml = list(k_Df.Tm)
    i = tml.index(t)
    return i
    
def lineDt(TmL,v,kDf):
    # base kDf draw point
    yyy = []
    for i in range(0,len(kDf)):
        yyy.append(float('nan'))
    for i,vv in enumerate(v):
        ii = get_ki(TmL[i])
        yyy[ii] = vv
    DS = pd.Series(yyy)
    DS = DS.interpolate()
    return DS
    

    
# ==========run sectionn=====================================

get_k('600438','D')
init_analysis()
bigk = gen_bigk_spec(k_Df,80)

signal = defaultdict(list)

ddL = []
c_ddL = []
outs =defaultdict(list)

no_more_dd = 0
for i in range(len(k_Df)):
    print '===================================================='
    tm = k_Df['Tm'][i]
    # ======init Distri =======================================
    
    if len(ddL) > 0:
        delL = []        
        for dd2 in ddL:
            if dd2.F == 10:
                delL.append(dd2)
        for dd3 in delL:
            print '__delete dd:',str(dd3.Tm_start)
            c_ddL.append(dd3)
            ddL.remove(dd3)
    if len(ddL) > 0:
        print '__update dd loop begin. len(ddL):',len(ddL)            
        for dd1 in ddL: 
            print '_______ddL:',str(dd1.Tm_start)
            dd1.gen_D(tm,k_Df)
            dd1.update_LD()
            if dd1.F == 2:
                signal['TmSignal'].append(tm)
                signal['TmCtS'].append(dd1.Tm_start)                 
                print '_______append Signal:tm:',str(dd1.Tm_start),'-',str(tm)
                to_dd(dd1,outs)
                dd1.F = 3    
    
    kA = get_kA(i,k_Df)
    if kA >= bigk and no_more_dd == 0:
        dd = Distri(k_Df,tm)
        dd.gen_D(tm,k_Df)
        dd.update_LD()
        ddL.append(dd)
        no_more_dd = 1
    else:
        no_more_dd = 0
    std(i)
    if Fstd == 1:
        Lv1()
        if FLv1 == 1:
            for dd in ddL:
                dd.Lv_count +=1
            FLv1 = 0
        Fstd = 0
 
# draw func============================================== 
    
Lv1ds = lineDt(Lv1D['Tm'],Lv1D['V'],k_Df)
sigV = []
sigTmIdx = []
for tm in signal['TmCtS']:
    v = float(k_Df[k_Df.Tm == tm].L)
    sigTmIdx.append(get_ki(tm))
    sigV.append(v)
    
dtCnt = len(k_Df)    
fig, ax1 = plt.subplots(figsize=(int(dtCnt/3),40))                
dwAxO(ax1,k_Df.O, k_Df.H, k_Df.L, k_Df.C)
for tm in signal['TmSignal']:
    i = get_ki(tm)
    ax1.vlines(i,4.5,13,color = 'red',lw = 1,alpha=0.75)

ax1.plot(Lv1ds)
ax1.plot(sigTmIdx,sigV, 'o',mfc = 'red')
plt.savefig('000.png') 
#plt.savefig('d:\Users\zhangyun29\Desktop\\1.png')   
'''   
# ========================================================
get_k('600438','D')
init_analysis()

signal = defaultdict(list)
TmC_thread = Lv1D['Tm'][0]
ddL = []
c_ddL = []
outs =defaultdict(list)

for i in range(len(k_Df)):
    print '===================================================='
    tm = k_Df['Tm'][i]   
    std(i)
    if Fstd == 1:
        Lv1()
    if len(Lv1D['Tm']) > 1:
        if len(ddL) > 0:
            
        if FLv1 == 1:
            i = len(Lv1D['Tm']) - 1        
 
            FLv1 = 0        



# ======================out====================================
tml = []
for i in range(len(ddL)):
    tml.append(ddL[i].Tm_start)

ddf = pd.DataFrame()
dd = ddL[4]
ddf['TmU'] = dd.LD['TmU']
ddf['k_count'] = dd.LD['k_count']
ddf['L'] = dd.LD['L']
ddf['H'] = dd.LD['H']
ddf['ap'] = dd.LD['ap']
ddf['r_total'] = dd.LD['r_total']
l = []
ll = []
ill = []
ii = len(dd.LD['ccwap'])
for i in range(ii):
    l.append(dd.LD['ccwap'][i][3])
    ll.append(dd.LD['ccH'][i][3])
    ill.append(dd.LD['ccpeak_start_i'][i][3])
    
ddf['ccwap'] = l
ddf['ccH'] = ll
ddf['cci'] = ill    
ddf.to_csv('ddL.LD.csv')     
'''