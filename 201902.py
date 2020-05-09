# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 15:07:55 2019
把Trend update 写成类函数

@author: zhangyun29
"""

import numpy as np
import pandas as pd

from LayerModel3 import Point,StdK, Stick, Trend

def main():
    global dt
    
    for k in dt[1:]:
        #print(k[4], Stick.lv_L[0].drt)
        flag_lv0, flag_lv1, flag_lv2 = 0,0,0
        
        # update crt Lv0 and add new lv0
        flag_lv0 = Stick.lv_L[-1].update(k)  
        
        # update crt Lv1 and add new Lv1
        TrendLv1.lv_L[-1].updateEndP(k)
        if flag_lv0 == 2:
            flag_lv1 = TrendLv1.lv_L[-1].update2()
        elif flag_lv0 == 1:
            flag_lv1 = TrendLv1.lv_L[-1].updatePeakP(k_bar=k)
            
        # update crt Lv2 and add new Lv2
        TrendLv2.lv_L[-1].updateEndP(k)
        if flag_lv1 == 2 or flag_lv1 == 3:
            flag_lv2 = TrendLv2.lv_L[-1].update2()
        elif flag_lv1 == 1:
            flag_lv2 = TrendLv2.lv_L[-1].updatePeakP(k_bar=k)
        
    return None

df = pd.read_csv('SHFE.bu1906.txt')
df['TmIdx'] = df.index
dt = df[['Open', 'High', 'Low', 'Close', 'TmIdx']].values.tolist()

Stick('init', k_bar=dt[0])
lv0_L = Stick.lv_L

TrendLv1 = type('TrendLv1', (Trend,), {'lv_L':[], 'main_list':Stick.lv_L, 'level':'TrendLv1'}) 
TrendLv1('init', k_bar=dt[0], mp=[0])
lv1_L = TrendLv1.lv_L

TrendLv2 = type('TrendLv2', (Trend,), {'lv_L':[], 'main_list':TrendLv1.lv_L, 'level':'TrendLv2'}) 
TrendLv2('init', k_bar=dt[0], mp=[0])
lv2_L = TrendLv2.lv_L

main()