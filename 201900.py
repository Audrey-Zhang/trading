# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 15:18:24 2019

@author: zhangyun29
"""

import numpy as np
import pandas as pd

from LayerModel2 import Stick, Trend

df = pd.read_csv('SHFE.bu1906.txt')
df['TmIdx'] = df.index
dt = df[['Open', 'High', 'Low', 'Close', 'TmIdx']].values.tolist()
lv0_L = [Stick('init', k_bar=dt[0])]   
lv1_L = [Trend('init', k_bar=dt[0], main_list=lv0_L, mp=[0])]
lv2_L = [Trend('init', k_bar=dt[0], main_list=lv1_L, mp=[0])]    

def appendNewTrend(flag, lv_L, nt_Dict):
    if flag == 2:
        lv_L.append(Trend('trim', **nt_Dict))
    elif flag == 3:
        for nt in nt_Dict:
            lv_L.append(Trend('trim', **nt))
    return None

getTV = lambda lv_L: [(stick.start.TmIdx, stick.start.V) for stick in lv_L]
    

def main():
    global dt, lv0_L, lv1_L, lv2_L
    
    for k in dt[1:]:
        flag_lv0, flag_lv1, flag_lv2 = 0,0,0
        
        # update crt Lv0 and add new lv0
        flag_lv0, new_lv0 = lv0_L[-1].update(k)        
        if flag_lv0 == 2:
            lv0_L.append(Stick('trim', **new_lv0))            
            
        # update crt Lv1 and add new lv1
        lv1_L[-1].updateEndP(k)
        if flag_lv0 == 2:
            flag_lv1, new_lv1 = lv1_L[-1].update2()
            appendNewTrend(flag_lv1, lv1_L, new_lv1)
        elif flag_lv0 == 1:
            flag_lv1 = lv1_L[-1].updatePeakP(k_bar=k)
                            
        # update crt lv2 and add new lv2
        if flag_lv1 == 2 or flag_lv1 == 3:
            while lv2_L[-1].mp[-1] < (len(lv1_L) - 1):
                flag_lv2, new_lv2 = lv2_L[-1].update2()
                appendNewTrend(flag_lv2, lv2_L, new_lv2)
            

    return None

main()
        

