import numpy as np
import pandas as pd
import time
import gc
import matplotlib as mpl
import matplotlib.pyplot as plt
from LayerModel5 import *
from frame import *

class Running(object):
    filepath = 'e:\Work_python\\trading\\trading\event_config.json'
    ef = EventFactory(filepath)

    def __init__(self, stockID, dt):
        self.m = Market(stockID, 4)
        self.dt = dt

        Stick.mm = self.m
        Trend.m = self.m
        Trend.ef = self.ef
        Pair.m = self.m
        PairChain.m = self.m
        PairChain.ef = self.ef
        CenterStrict.m = self.m
        CenterStrict.ef = self.ef
    
        Stick.remark = []


    def play(self):   
        Stick.L = self.m.findList('st', 0)
        Stick('init', k_bar=self.dt[0])
        TrendLv1 = type('TrendLv1', (Trend,), {'L':self.m.findList('st', 1), 'ML':Stick.L, 'level':1}) 
        TrendLv1('init', k_bar=self.dt[0], mp=[0])
        TrendLv2 = type('TrendLv2', (Trend,), {'L':self.m.findList('st', 2), 'ML':TrendLv1.L, 'level':2}) 
        TrendLv2('init', k_bar=self.dt[0], mp=[0])
        TrendLv3 = type('TrendLv3', (Trend,), {'L':self.m.findList('st', 3), 'ML':TrendLv2.L, 'level':3}) 
        TrendLv3('init', k_bar=self.dt[0], mp=[0])
        Center0 = type('Center0', (CenterStrict,), {'ML': self.m.findList('st', 0), 'L': self.m.findList('center', 0), 'openL':[],  'level': 0})
        Center0()
        Center1 = type('Center1', (CenterStrict,), {'ML': self.m.findList('st', 1), 'L': self.m.findList('center', 1), 'openL':[],  'level': 1})
        Center1()
        Center2 = type('Center2', (CenterStrict,), {'ML': self.m.findList('st', 2), 'L': self.m.findList('center', 2), 'openL':[],  'level': 2})
        Center2()
        Center3 = type('Center3', (CenterStrict,), {'ML': self.m.findList('st', 3), 'L': self.m.findList('center', 3), 'openL':[],  'level': 3})
        Center3()
        PairLv0 = type('PairLv0', (Pair,), {'ML': self.m.findList('st', 0), 'L': self.m.findList('pair', 0), 'level': 0})
        PairLv0(0)
        PairLv1 = type('PairLv1', (Pair,), {'ML': self.m.findList('st', 1), 'L': self.m.findList('pair', 1), 'level': 1})
        PairLv1(0)
        PairLv2 = type('PairLv2', (Pair,), {'ML': self.m.findList('st', 2), 'L': self.m.findList('pair', 2), 'level': 2})
        PairLv2(0)
        PairLv3 = type('PairLv3', (Pair,), {'ML': self.m.findList('st', 3), 'L': self.m.findList('pair', 3), 'level': 3})
        PairLv3(0)
        PairChainLv0 = PairChain(0, 'PairChainLv0')
        PairChainLv1 = PairChain(1,'PairChainLv1')
        PairChainLv2 = PairChain(2, 'PairChainLv2')
        PairChainLv3 = PairChain(3, 'PairChainLv3')
        
        SIG_overlap.m, SIG_overlap.ef = self.m, self.ef
        actions = []
        level = 3
        actions.append({ 'level_num': level, 
                    'obj_name': 'TrendLv' +str(int(level)),
                    'event_name': 'NEW',
                    'obj_p': 'SIG_overlap',
                    'method': 'any_opp',
                    'param': str(level)  })
        for ac in actions:
            self.ef.regAction(**ac)
 
        layer = self.m.layer
        m = self.m
        
        Event.L = [[] for i in list(range(layer+1))]
        #filepath = 'event_config.json'
        #ef = EventFactory(filepath)
        
        
        for k in self.dt[1:]:
            self.m.update(k)
            Stick.L[-1].update(k)  
            
            # update crt Lv1 and add new Lv1
            TrendLv1.L[-1].updateEndP(k)
            
            for i in list(range(layer)):
                if len(Event.L[i]) > 0:
                    for event in Event.L[i][:]:
                        actions = self.ef.play(event)
                        for a in actions:
                            self.m.remark.append('{}:{},st0:{}, st1:{}'.format(self.m.TmIdx, a, len(m.findList('st',0)),  len(m.findList('st',1))))
                            if a != '':
                                eval(a)
                                
            
        print([sig.remark for sig in SIG_overlap.L])
        print(len(self.m.findList('st', 3)))
        
       
        return self.m.remark

    def reset_market(self):
        self.dt = []
        SIG_overlap.L = []
        for key in self.m.__dict__:
            if key[-2:] =='_L':
                ll = self.m.__dict__[key]
                for i in range(len(ll))[::-1]:
                    del self.m.__dict__[key][i]
        for i in range(len(StdK.obj_L))[::-1]:
            del StdK.obj_L[i]
        for i in range(len(Point.obj_L))[::-1]:
            del Point.obj_L[i]
        gc.collect()
        return None