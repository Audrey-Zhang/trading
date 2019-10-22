# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 14:38:46 2019

@author: ariesyun
"""
import numpy as np

class Point:
    def __init__(self, time_index, value, drt):
        self.TmIdx, self.V, self.drt = time_index, value, drt
        
    def __repr__(self):
        return 'Point({0.TmIdx!r}, {0.V!r}, {0.drt!r})'.format(self)

    def __str__(self):
        return '({0.TmIdx!s}, {0.V!s}, {0.drt!s})'.format(self)

    @classmethod
    def getPoint(cls, method, s, index=None):
        '''
        method: init/H/L;  /H/L/start/end
        s:      k_bar/ StdK /Stick /Trend/ list
        '''
        if isinstance(s, list): 
            if index is None:
                return cls.getP_k_bar(method, s)
            return cls.getP_type(method, s[index])
        else:
            return cls.getP_type(method, s)

    @classmethod
    def getP_type(cls, method, s):
        if isinstance(s, list):
            return cls.getP_k_bar(method, s)
        elif isinstance(s, StdK):
            return cls.getP_stdk(method, s)
        else:
            return cls.getP_ss(method, s)

    @classmethod
    def getP_k_bar(cls, method, s):
        if method == 'H':
            return Point(s[4], s[1], -1)
        elif method =='L':
            return Point(s[4], s[2], 1)
        elif method == 'init':
            return Point(s[4], s[0], 0)

    @classmethod
    def getP_stdk(cls, method, s):
        # method here is useless
        if s.drt == 1:
            return Point(s.TmIdx, s.H, -1)
        elif s.drt == -1:
            return Point(s.TmIdx, s.L, 1)
        elif method == 'init':
            return Point(s.TmIdx, s.L, 0)

    @classmethod
    def getP_ss(cls, method, s):
        if method == 'H':
            if s.drt == 1:
                mehtod = 'end'
            else:
                method = 'start'
        elif method == 'L':
            if s.drt == -1:
                mehtod = 'start'
            else:
                method = 'end'

        if method == 'start':
            return s.start
        elif method =='end':
            return s.end
        
class StdK:
    def __init__(self, **kwargs):
        self.drt = kwargs['drt']
        if 'k_bar' in kwargs.keys():
            self.H, self.L, self.TmIdx = kwargs['k_bar'][1], kwargs['k_bar'][2], kwargs['k_bar'][4]
        if 'H' in kwargs.keys():
            self.H, self.L, self.TmIdx = kwargs['H'], kwargs['L'], kwargs['TmIdx']
        self.merged = 1
        # self.range = None  # for ES, trend_drt==1 ~ rangeL, trend_drt==-1 ~ rangeH
    
    def __repr__(self):
        return 'StdK({0.TmIdx}, {0.H}, {0.L}, {0.drt})'.format(self)

    def __str__(self):
        return '({0.TmIdx!s}, {0.H!s}, {0.L!s}, {0.drt!s})'.format(self)

    def update(self, k_bar):
        flag = 0 # 0:stain; 1: up new; -1: down new
        if (k_bar[1] > self.H and k_bar[2] > self.L) or (self.drt == 1 and k_bar[1] > self.H):
            flag = 1
            k_bar[2] = max(k_bar[2], self.L)
        elif (k_bar[1] < self.H and k_bar[2] < self.L) or (self.drt == -1 and k_bar[2] < self.L):
            flag = -1
            k_bar[1] = min(k_bar[1], self.H)
        else:
            flag = 0
            if self.drt == -1:
                self.H = min(self.H, k_bar[1])
            elif self.drt == 1:
                self.L = max(self.L, k_bar[2])
        return flag, k_bar 
    
    def trimUpdate(self, new_stdk):
        if self.drt == 1:
            self.L = max(self.L, new_stdk['L'])
        elif self.drt == -1:
            self.H = min(self.H, new_stdk['H'])
        else:
            self.L = max(self.L, new_stdk['L'])
            self.H = min(self.H, new_stdk['H'])
            
class Stick(object):
    lv_L = []
    m = {'1': ['L', 'H', 'H'], '-1':['H', 'L', 'L']}
    def __init__(self, method, **kwargs):
        self.lv_L.append(self)
        if method == 'init':
            self.start = Point(kwargs['k_bar'][4], kwargs['k_bar'][0], drt=0)
            self.end = Point(kwargs['k_bar'][4], kwargs['k_bar'][0], drt=0)
            self.std_k_bar_stack = [StdK(k_bar=kwargs['k_bar'], drt=0)]
            self.peak = Point.getPoint('init', kwargs['k_bar'])            
            self.drt = 0            
            self.reverse_count = 0
            self.status = 0 # 0:open; 1:ripe; 2:close

        elif method == 'trim':
            self.std_k_bar_stack = kwargs['std_k_bar_stack']
            self.drt = -self.std_k_bar_stack[0].drt
            self.peak_std_bar = kwargs['peak_std_bar']

            self.start = Point.getPoint('', self.std_k_bar_stack[0])
            self.end = Point.getPoint('', self.std_k_bar_stack[-1])
            self.peak = Point.getPoint('', self.peak_std_bar)

            self.reverse_count = 1
            self.status = 1 # 0:open, new peak与起点比较; 1:ripe, new peak与self.peak比较; 2:close

    def __repr__(self):
        return 'Stick({0.drt!r}, {0.status!r}, {0.start!r})'.format(self)

    def __str__(self):
        return '({0.drt!s}, {0.status!s}, {0.start!s})'.format(self)

    def update(self, k_bar):
        return self.lv_L[-1].update1Bar(k_bar)

    def update1Bar(self, k_bar):
        '''
        Return: 
        flag:  [0:stain; 1: updated; 2:close]
        '''
        flag = 0 # 0:stain; 1: updated; 2:close
        
        if self.updateStdK(k_bar) != 0: # 更新stdK, stdK_stack，如果有新的stdK，则继续更新Stick
            peak, pp = self.findPeak()
            if peak == 0:
                flag = self.updateRange(k_bar)
                self.reverse_count += 1
                
            elif self.status == 0:  # 找到Peak
                
                if self.drt == 0:
                    self.drt = peak
                elif peak == self.drt:
                    flag = 0
                elif self.reverse_count > 3:
                    self.status = 1
                    self.peak_std_bar = self.std_k_bar_stack[pp]
                    self.peak = Point.getPoint('', self.std_k_bar_stack[pp])
                    
                    self.reverse_count = 1
                    flag = 1      
            # Ripe, new peak 与 peak比较
            elif peak == self.peak.drt: # 
            
                if self.drt == 1 and self.std_k_bar_stack[-2].H >= self.peak.V:
                    self.peak_std_bar = self.std_k_bar_stack[pp]
                    self.peak = Point.getPoint('', self.std_k_bar_stack[pp])
                    self.reverse_count = 1
                    flag = 1                    
                elif self.drt == -1 and self.std_k_bar_stack[-2].L <= self.peak.V:
                    self.peak_std_bar = self.std_k_bar_stack[pp]
                    self.peak = Point.getPoint('', self.std_k_bar_stack[pp])
                    self.reverse_count = 1
                    flag = 1 
                else:
                    self.reverse_count += 1
                    flag = 0
            elif peak != self.peak.drt and self.reverse_count > 3:
                self.status = 2
                self.newStick()
                flag = 2 
                
        return flag
    
    def updateStdK(self, k_bar):
        is_new = 0
        is_new, trimed_k_bar = self.std_k_bar_stack[-1].update(k_bar)
        if is_new != 0:
            
            self.std_k_bar_stack.append(StdK(k_bar=trimed_k_bar, drt=is_new)) 
            self.reverse_count += 1
            
        return is_new
            
    #=================================================================================
    def findPeak(self):
        peak_type = 0
        if self.reverse_count > 2:
            if (self.std_k_bar_stack[-2].H > self.std_k_bar_stack[-1].H and 
               self.std_k_bar_stack[-2].H > self.std_k_bar_stack[-3].H):
                peak_type = -1
            elif (self.std_k_bar_stack[-2].L < self.std_k_bar_stack[-1].L and 
               self.std_k_bar_stack[-2].L < self.std_k_bar_stack[-3].L):
                peak_type = 1
        return peak_type, len(self.std_k_bar_stack) - 2
    
    def updateRange(self, k_bar):
        flag = 0  # 0: stick stain; 1: stick updated
        if self.peak.drt == 0:
            return flag
        if self.drt == 1 and k_bar[1] >= self.peak.V:
            self.status = 0
            self.peak_std_bar = self.std_k_bar_stack[-1]
            flag = 1
        elif self.drt == -1 and k_bar[2] <= self.peak.V:
            self.status = 0 
            self.peak_std_bar = self.std_k_bar_stack[-1]
            flag = 1

        return flag
    
    def newStick(self):

        pp = self.std_k_bar_stack.index(self.peak_std_bar)
        std_k_bar_stack = self.std_k_bar_stack[pp:]
        peak_std_bar = std_k_bar_stack[len(std_k_bar_stack) - 2]

        new_stick = {
            'std_k_bar_stack' : std_k_bar_stack,
            'peak_std_bar' : peak_std_bar
        }
        Stick('trim', **new_stick)
        return None
    
    def beRipe(self):
        self.status == 1
                
class Trend(object):
    lv_L = []
    level = 'Trend'
    main_list = []
    def __init__(self, method, **kwargs):
        self.lv_L.append(self)
        if 'mp' in kwargs.keys():
            self.mp = kwargs['mp']
        else:
            self.mp = None, None

        if method == 'init':
            # from P
            self.stick_stack = [self.main_list[0]]
            self.start = Point.getPoint('init', kwargs['k_bar'])
            self.end = Point.getPoint('init', kwargs['k_bar'])
            self.peak = Point.getPoint('init', kwargs['k_bar'])
            self.peak_position_in_ss = 0
            
            self.ES_stack = []
            self.SS_stack = []
            self.drt = 0            
            self.status = 0 

        elif method == 'trim': 
            if 'mp' in kwargs.keys():
                self.mp = kwargs['mp']
                self.stick_stack = [self.main_list[i] for i in self.mp]
            else:
                self.stick_stack = kwargs['stick_stack']

            self.drt = self.stick_stack[0].drt
            self.start = Point.getPoint('start', self.stick_stack[0])
            self.end = Point.getPoint('end', self.stick_stack[-1])
        
            # from /
            if len(self.stick_stack) == 1:
                self.peak = Point.getPoint('end', self.stick_stack[0])
                self.peak_point_in_ss = 1
                self.ES_stack = []
                self.SS_stack = [StdK(**self.stickToStdK(self.stick_stack[0]))]
                    
            #from /\, N
            else:
                self.setPeak()
                self.ES_stack = kwargs['ES_s']
                self.SS_stack = kwargs['SS_s']

            self.status = kwargs['status']
            
            if len(self.ES_stack) > 1:
                print('!!!Error!!! ES of new trend > 1.')
            if self.drt == 0:
                print('!!!Error!!! drt = 0.')
    

    def update(self, k_bar):
        self.updateRange(k_bar)
        
        flag = 0 # 0:stain; 1: updated; 2:cloesd;
        new_trend = {}
        
        flag_st, new_stick = self.stick_stack[-1].update(k_bar) 
                    

        if self.drt == 0 and flag_st == 2:
            self.stick_stack.append(Stick('trim', **new_stick))
            self.drt = self.stick_stack[0].drt
            self.peak = Point.getPoint('end', self.stick_stack[0])
            self.SS_stack = [StdK(**self.stickToStdK(self.stick_stack[0]))]
            flag = 1

            
        elif self.status == 0 and flag_st == 2:
            self.stick_stack.append(Stick('trim', **new_stick))
            if len(self.stick_stack) == 3:
                if (self.stick_stack[1].peak.V - self.stick_stack[0].start.V)*self.drt < 0:
                    self.status = 2
                    new_trend = self.newTrend(0)
                    flag = 2
                else:               
                    self.ES_stack = [StdK(**self.stickToStdK(self.stick_stack[1]))]
                    self.status = 1
                    flag = 1
                
            
        elif self.status == 1 and flag_st == 2:            
            # Step1: append to stick_stack
            self.stick_stack.append(Stick('trim', **new_stick))
            tmp_stdk = self.stickToStdK(self.stick_stack[-2])
            
            # 处理eigen_stick:
            if self.drt != tmp_stdk['drt']:
                
                if self.drt == 1:
                    if tmp_stdk['L'] < self.ES_stack[-1].L:
                        if tmp_stdk['H']> self.ES_stack[-1].H:   # case2: 外包
                            if tmp_stdk['L'] < self.start.V:
                                self.status = 2
                                new_trend =  self.newTrend(0)
                                flag = 2
                            else:
                                tmp_stdk['L'] = self.ES_stack[-1].L
                                self.ES_stack.append(StdK(**tmp_stdk))
                                flag = 1
                        elif tmp_stdk['H'] <= self.ES_stack[-1].H:  # case1：反向
                            self.status = 2
                            new_trend = self.newTrend(1)
                            flag = 2
                    elif (tmp_stdk['H'] <= self.ES_stack[-1].H and
                         tmp_stdk['L'] >= self.ES_stack[-1].L):        #  case3: trimUpdate
                        self.ES_stack[-1].L = tmp_stdk['L']
                        self.ES_stack[-1].merged += 1
                        flag = 1
                    elif tmp_stdk['H'] > self.ES_stack[-1].H:     #case4: 进行
                        self.ES_stack.append(StdK(**tmp_stdk))
                        flag = 1
                        
                elif self.drt == -1:
                    if tmp_stdk['H'] > self.ES_stack[-1].H:
                        if tmp_stdk['L'] < self.ES_stack[-1].L:
                            if tmp_stdk['H'] > self.start.V:
                                self.status = 2
                                new_trend =  self.newTrend(0)
                                flag = 2
                            else:
                                tmp_stdk['H'] = self.ES_stack[-1].H
                                self.ES_stack.append(StdK(**tmp_stdk))
                                flag = 1
                        elif tmp_stdk['L'] >= self.ES_stack[-1].L:
                            self.status = 2
                            new_trend = self.newTrend(1)
                            flag = 2
                    elif (tmp_stdk['L'] >= self.ES_stack[-1].L and
                         tmp_stdk['H'] <= self.ES_stack[-1].H):
                        self.ES_stack[-1].H = tmp_stdk['H']
                        self.ES_stack[-1].merged += 1
                        flag = 1
                    elif tmp_stdk['L'] < self.ES_stack[-1].L:
                        self.ES_stack.append(StdK(**tmp_stdk))
                        flag = 1
                        
            
            # 处理syntropy_stick:
            elif self.drt == tmp_stdk['drt']:
                
                if self.drt == 1:
                    if tmp_stdk['H'] > self.SS_stack[-1].H:
                        if self.ES_stack[-1].merged > 1 and tmp_stdk['H'] < self.ES_stack[-1].H:
                            self.status = 2
                            new_trend = self.newTrend(21)
                            flag = 3
                        else:
                            self.SS_stack.append(StdK(**tmp_stdk))
                            flag = 1
                            pp = self.findIdxInSS(self.peak.TmIdx)

                    else:
                        self.SS_stack.append(StdK(**tmp_stdk))
                        flag = 1
                        
                elif self.drt == -1:
                    if tmp_stdk['L'] < self.SS_stack[-1].L:
                        if self.ES_stack[-1].merged > 1  and tmp_stdk['L'] > self.ES_stack[-1].L:
                            self.status = 2
                            new_trend = self.newTrend(21)
                            flag = 3
                        else:
                            self.SS_stack.append(StdK(**tmp_stdk))
                            flag = 1
                            pp = self.findIdxInSS(self.peak.TmIdx)

                    else:
                        self.SS_stack.append(StdK(**tmp_stdk))
                        flag = 1

        return flag, new_trend

    def update2(self):
        flag = 0
        treated = self
        
        # Check main_list to find new sticks   
        #new_mp = []  
        if len(self.main_list) - self.mp[-1] > 1:
            new_mp = [i for i in range(self.mp[-1]+1, len(self.main_list))]
        # iterate stick_stack to update Trend
        for i in new_mp:
            if self.status == 2:
                print(treated is self.lv_L[-1])
            treated.stick_stack.append(treated.main_list[i])
            treated.mp.append(i)
            flag, treated = treated.update1Stick()
        return flag

    def update1Stick(self):
        #self._updateStickStack()  
        flag = 0  # 0:stain; 1: updated; 2:cloesd;
        new_trend = self           

        if self.drt == 0: # 不需要以stick_stack的末尾进行更新; Trend currently is a Point
            self.drt = self.stick_stack[0].drt
            self.SS_stack = [StdK(**self.stickToStdK(self.stick_stack[0]))]
            flag = 1

            
        elif self.status == 0: # 不需要以stick_stack的末尾进行更新; Trend currently is / or in 1st N or 1st flag; 
            if len(self.stick_stack) == 3:
                if (self.stick_stack[1].peak.V - self.stick_stack[0].start.V)*self.drt < 0:
                    self.status = 2
                    new_trend = self.produceNewTrend(0)
                    flag = 2
                else:               
                    self.ES_stack = [StdK(**self.stickToStdK(self.stick_stack[1]))]
                    self.status = 1
                    flag = 1
                
            
        elif self.status == 1:  # 需要以stick_stack的末尾进行更新       
            tmp_stdk = self.stickToStdK(self.stick_stack[-2])
            
            # 处理eigen_stick:
            if self.drt != tmp_stdk['drt']:
                
                if self.drt == 1:
                    if tmp_stdk['L'] < self.ES_stack[-1].L:
                        if tmp_stdk['H']> self.ES_stack[-1].H:   # case2: 外包
                            if tmp_stdk['L'] < self.start.V:
                                self.status = 2
                                new_trend =  self.produceNewTrend(0)
                                flag = 2
                            else:
                                tmp_stdk['L'] = self.ES_stack[-1].L
                                self.ES_stack.append(StdK(**tmp_stdk))
                                flag = 1
                        elif tmp_stdk['H'] <= self.ES_stack[-1].H:  # case1：反向
                            self.status = 2
                            new_trend = self.produceNewTrend(1)
                            flag = 2
                    elif (tmp_stdk['H'] <= self.ES_stack[-1].H and
                         tmp_stdk['L'] >= self.ES_stack[-1].L):        #  case3: trimUpdate
                        self.ES_stack[-1].L = tmp_stdk['L']
                        self.ES_stack[-1].merged += 1
                        flag = 1
                    elif tmp_stdk['H'] > self.ES_stack[-1].H:     #case4: 进行
                        self.ES_stack.append(StdK(**tmp_stdk))
                        flag = 1
                        
                elif self.drt == -1:
                    if tmp_stdk['H'] > self.ES_stack[-1].H:
                        if tmp_stdk['L'] < self.ES_stack[-1].L:
                            if tmp_stdk['H'] > self.start.V:
                                self.status = 2
                                new_trend =  self.produceNewTrend(0)
                                flag = 2
                            else:
                                tmp_stdk['H'] = self.ES_stack[-1].H
                                self.ES_stack.append(StdK(**tmp_stdk))
                                flag = 1
                        elif tmp_stdk['L'] >= self.ES_stack[-1].L:
                            self.status = 2
                            new_trend = self.produceNewTrend(1)
                            flag = 2
                    elif (tmp_stdk['L'] >= self.ES_stack[-1].L and
                         tmp_stdk['H'] <= self.ES_stack[-1].H):
                        self.ES_stack[-1].H = tmp_stdk['H']
                        self.ES_stack[-1].merged += 1
                        flag = 1
                    elif tmp_stdk['L'] < self.ES_stack[-1].L:
                        self.ES_stack.append(StdK(**tmp_stdk))
                        flag = 1
                        
            
            # 处理syntropy_stick:
            elif self.drt == tmp_stdk['drt']:
                
                if self.drt == 1:
                    if tmp_stdk['H'] > self.SS_stack[-1].H:
                        if self.ES_stack[-1].merged > 1 and tmp_stdk['H'] < self.ES_stack[-1].H:
                            self.status = 2
                            new_trend = self.produceNewTrend(21)
                            flag = 3
                        else:
                            self.SS_stack.append(StdK(**tmp_stdk))
                            flag = 1
                            pp = self.findIdxInSS(self.peak.TmIdx)

                    else:
                        self.SS_stack.append(StdK(**tmp_stdk))
                        flag = 1
                        
                elif self.drt == -1:
                    if tmp_stdk['L'] < self.SS_stack[-1].L:
                        if self.ES_stack[-1].merged > 1  and tmp_stdk['L'] > self.ES_stack[-1].L:
                            self.status = 2
                            new_trend = self.produceNewTrend(21)
                            flag = 3
                        else:
                            self.SS_stack.append(StdK(**tmp_stdk))
                            flag = 1
                            pp = self.findIdxInSS(self.peak.TmIdx)

                    else:
                        self.SS_stack.append(StdK(**tmp_stdk))
                        flag = 1

        return flag, new_trend

    def updateEndP(self, k_bar):
        if self.drt == 1:
            method = 'H'
        else:
            method = 'L'
        self.end = Point.getPoint(method, k_bar)
        return None

    def updateX(self):
        '''
        Return:
        大段: SS_percentage, pair_count
        大N：v3 - v1, v4-v2, v2 - v1, v4-v3, k1, k3
        '''
        tm = self.end.TmIdx 
        x0, x1 = self.getSSPct()
        

        return tm, x0, x1

    def _updateStickStack(self):
        '''
        self.mp -> append one
        self.stick_stack  -> append one
        '''
        i  = len(self.main_list) - 1
        if (i - self.mp[-1]) > 0:
            self.mp.append(self.mp[-1]+1)
            self.stick_stack = self.main_list[self.mp[0]:self.mp[-1]+1]
            return 0
        else:
            return None

    def updatePeakP(self, k_bar=None, stick=None):
        '''
        update self.peak and self.pp
        only used in update by stick mode!
        '''
        flag = 0
        if k_bar is not None:
            if self.drt == 1 and k_bar[1] >= self.peak.V:
                self.peak = Point.getPoint('H', k_bar)
                flag = 1
            elif self.drt == -1 and k_bar[2] <= self.peak.V:
                self.peak = Point.getPoint('L', k_bar)
                flag = 1
        elif stick is not None:
            if self.drt == stick.drt and (self.drt * stick.peak.V) >= (self.drt * self.peak.V):
                self.peak = Point.getPoint('end', stick)
                flag = 1
        return flag

    def updatePp(self, time_index=None, pp=None):
        if time_index is not None:
            self.pp = self.findIdxInSS(time_index)
        else:
            self.pp = pp
        return None
    

    ##===========================================================           
    def stickToStdK(self, stick_r):
        if stick_r.drt == 1:
            stdk = {'H':stick_r.peak.V, 'L':stick_r.start.V, 'TmIdx':stick_r.start.TmIdx, 'drt': 1}
        elif stick_r.drt == -1:
            stdk = {'L':stick_r.peak.V, 'H':stick_r.start.V, 'TmIdx':stick_r.start.TmIdx, 'drt': -1}
        elif stick_r.drt == 0:
            stdk = {'L':stick_r.start.V, 'H':stick_r.start.V, 'TmIdx':stick_r.start.TmIdx, 'drt': 0}
        return stdk
    
    def getPoint(self, stack, position_in_stack=0, method=None):
        if method == 'peak':
            if self.drt == 1:
                method = 'H'
            elif self.drt == -1:
                method = 'L'
            else:
                method = 'init'

        if isinstance(stack, str): 
            if stack == 'ss':
                if method == 'start':
                    drt = self.stick_stack[position_in_stack].drt
                    p = Point(self.stick_stack[position_in_stack].start.TmIdx, 
                             self.stick_stack[position_in_stack].start.V,
                             drt)
                elif method == 'end':
                    drt = -self.stick_stack[position_in_stack].drt
                    p = Point(self.stick_stack[position_in_stack].peak.TmIdx, 
                             self.stick_stack[position_in_stack].peak.V,
                             drt)
            elif stack == 'ES':
                if method == 'start':
                    drt = self.ES_stack[position_in_stack].drt
                    p = Point(self.ES_stack[position_in_stack].start.TmIdx, 
                             self.ES_stack[position_in_stack].start.V,
                             drt)
                elif method == 'end':
                    drt = -self.ES_stack[position_in_stack].drt
                    p = Point(self.ES_stack[position_in_stack].peak.TmIdx, 
                             self.ES_stack[position_in_stack].peak.V,
                             drt)
        elif isinstance(stack, list):
            if method == 'H':
                p = Point(stack[4], stack[1], -1)
            elif method =='L':
                p = Point(stack[4], stack[2], 1)
            elif method == 'init':
                p = Point(stack[4], stack[0], 0)
        elif isinstance(stack, StdK):
            if method == 'H':
                p = Point(stack.TmIdx, stack.H, -1)
            elif method == 'L':
                p = Point(stack.TmIdx, stack.L, 1)
        elif isinstance(stack, Stick) or isinstance(stack, Trend):
            if method == 'H' and stack.drt == 1:
                p = Point(stack.peak.TmIdx, stack.peak.V, -1)
            elif method == 'H' and stack.drt == -1:
                p = Point(stack.start.TmIdx, stack.start.V, -1)
            elif method == 'L' and stack.drt == -1:
                p = Point(stack.peak.TmIdx, stack.peak.V, 1)
            elif method == 'L' and stack.drt == 1:
                p = Point(stack.start.TmIdx, stack.start.V, 1)
            elif method == 'start':
                p = Point(stack.start.TmIdx, stack.start.V, stack.drt)
            elif method == 'end':
                p = Point(stack.peak.TmIdx, stack.peak.V, -stack.drt)
        return p
    
    def updateRange(self,k):
        flag = 0
        if self.drt == 1 and k[1] > self.peak.V:
            self.peak = Point.getPoint(k, 0, method='H')
            flag = 1
        elif self.drt == -1 and k[2] < self.peak.V:
            self.peak = Point.getPoint(k, 0, method = 'L')
            flag = 1
        return flag
    
    def setPeak(self):
        # iterate ss to set peak point and pp in ss
        self.peak = Point.getPoint('end', self.stick_stack[0])
        self.peak_point_in_ss = 1
        pp = 0
        if self.drt == 1 and len(self.stick_stack) >= 3:
            for stick in self.stick_stack[2::2]:
                pp += 2
                if stick.peak.V > self.peak.V:
                    self.peak = Point.getPoint('end', self.stick_stack[pp])
                    self.peak_point_in_ss = pp + 1 
        elif self.drt == -1 and len(self.stick_stack) >= 3:
            for stick in self.stick_stack[2::2]:
                pp += 2
                if stick.peak.V < self.peak.V:
                    self.peak = Point.getPoint('end', self.stick_stack[pp])
                    self.peak_point_in_ss = pp + 1
        return None
            
    def findIdxInSS(self, timeIndex):
        i = 0
        pp = None

        for stick in self.stick_stack:
            if timeIndex == stick.start.TmIdx:
                pp = i
                break
            i += 1
        return pp
    
    def produceNewTrend(self, case):
        mp = None
        if case == 0:
            #stick_stack = [self.stick_stack[-2]]
            if self.mp is not None:
                mp = self.mp[-2:]
            nt_dict = {'stick_stack': [],
                        'mp': mp,
                        'main_list': self.main_list,
                        'ES_s': [],
                        'SS_s': [StdK(**self.stickToStdK(self.main_list[mp[0]]))],
                        'status': 0}
            self.newTrend(**nt_dict)


        elif case == 1:
            peak_point_in_stick_stack = self.findIdxInSS(self.ES_stack[-1].TmIdx)
            if self.mp is not None:
                mp = self.mp[peak_point_in_stick_stack:]
            stick_stack = self.stick_stack[peak_point_in_stick_stack:]
            nt_dict = {'stick_stack': stick_stack,
                        'mp': mp,
                        'main_list': self.main_list,
                        'ES_s': self.reduceES(stick_stack),
                        'SS_s': [StdK(**self.stickToStdK(stick)) for stick in stick_stack[::2]],
                        'status': 1}
            self.newTrend(**nt_dict)

        elif case == 21:
            pp_TmIdx = 0
            min_v = min(self.stick_stack[-2].start.V, self.stick_stack[-2].peak.V)
            max_v = max(self.stick_stack[-2].start.V, self.stick_stack[-2].peak.V)
            pp_start = self.findIdxInSS(self.ES_stack[-1].TmIdx)

            for stick in self.stick_stack[-4:pp_start:-2]: 
                stdk = StdK(**self.stickToStdK(stick))
                if self.drt == 1:
                    if stdk.H < max_v and stdk.L <= min_v:
                        min_v = stdk.L
                        pp_TmIdx = stdk.TmIdx
                    elif stdk.H >= max_v:
                        break
                elif self.drt == -1:
                    if stdk.H >= max_v and stdk.L > min_v:
                        max_v = stdk.H
                        pp_TmIdx = stdk.TmIdx
                    elif stdk.L <= min_v:
                        break
            stick_stack1 = self.stick_stack[self.findIdxInSS(pp_TmIdx):]
            if self.mp is not None:
                mp1 = self.mp[self.findIdxInSS(pp_TmIdx):]
            nt_dict1 = {'stick_stack':stick_stack1,
                          'mp': mp1,
                          'main_list': self.main_list,
                          'ES_s': self.reduceES(stick_stack1),
                          'SS_s': [StdK(**self.stickToStdK(stick)) for stick in stick_stack1[::2]],
                          'status': 1}
            stick_stack2 = self.stick_stack[self.findIdxInSS(self.ES_stack[-1].TmIdx):self.findIdxInSS(pp_TmIdx)]
            if self.mp is not None:
                mp2 = self.mp[self.findIdxInSS(self.ES_stack[-1].TmIdx):self.findIdxInSS(pp_TmIdx)]
            nt_dict2 = {'stick_stack':stick_stack2,
                          'mp': mp2,
                          'main_list': self.main_list,
                          'ES_s': self.reduceES(stick_stack2, 0),
                          'SS_s': [StdK(**self.stickToStdK(stick)) for stick in stick_stack2[::2]],
                          'status': 2}
            
            self.newTrend(**nt_dict2)
            self.newTrend(**nt_dict1)
        
        
        new_trend = self.lv_L[-1]
        return new_trend

    @classmethod
    def newTrend(cls, **kwargs): 
        new_trend = cls.__new__(cls)

        cls.lv_L.append(new_trend)

        if 'mp' in kwargs.keys():
            new_trend.mp = kwargs['mp']
            new_trend.stick_stack = [new_trend.main_list[i] for i in new_trend.mp]
        else:
            new_trend.stick_stack = kwargs['stick_stack']
            
        new_trend.drt = new_trend.stick_stack[0].drt
        new_trend.start = Point.getPoint('start', new_trend.stick_stack[0])
        new_trend.end = Point.getPoint('end', new_trend.stick_stack[-1])
        
        # from /
        if len(new_trend.stick_stack) == 2:
            new_trend.peak = Point.getPoint('end', new_trend.stick_stack[0])
            new_trend.peak_point_in_ss = 1
            new_trend.ES_stack = []
            new_trend.SS_stack = [StdK(**new_trend.stickToStdK(new_trend.stick_stack[0]))]
                    
        #from /\, N
        else:
            new_trend.setPeak()
            new_trend.ES_stack = kwargs['ES_s']
            new_trend.SS_stack = kwargs['SS_s']

        new_trend.status = kwargs['status']
            
        return None
   
    def reduceES(self, stick_stack_o, tail=1):
        drt = stick_stack_o[0].drt
        stick_stack = stick_stack_o[:]
        if tail == 1:            
            stick_stack.pop()
        l = len(stick_stack)
        #  if l < 3: stick_stack index (0,1,2) / (0,1) / (0)
        if l == 1:
            ES_stack = []
        else:
            ES_stack = [StdK(**self.stickToStdK(stick_stack[1]))]
        
        if drt == 1 and l >= 3:            
            for stick in stick_stack[3::2]:
                if ES_stack[-1].H < stick.start.V:
                    tmp_stdk = StdK(**self.stickToStdK(stick))
                    if ES_stack[-1].L > stick.peak.V:
                        tmp_stdk.L = ES_stack[-1].L
                    ES_stack.append(tmp_stdk)
                else:
                    ES_stack[-1].trimUpdate(self.stickToStdK(stick))
        elif drt == -1 and l >= 3:
            for stick in stick_stack[3::2]:
                if ES_stack[-1].L > stick.start.V:
                    tmp_stdk = StdK(**self.stickToStdK(stick))
                    if ES_stack[-1].H < stick.peak.V:
                        tmp_stdk.H = ES_stack[-1].H
                    ES_stack.append(tmp_stdk)
                else:
                    ES_stack[-1].trimUpdate(self.stickToStdK(stick))
        return ES_stack
    
    def getSSPct(self):
        ss_a, es_a = 0, 0
        if len(self.stick_stack) == 1:
            ss_a = abs(self.stick_stack[-1].start.V - self.stick_stack[-1].peak.V)
        else:
            for stick1, stick2 in zip(self.stick_stack[::2], self.stick_stack[1::2]):
                ss_a += abs(stick1.start.V - stick1.peak.V)
                es_a += abs(stick2.start.V - stick2.peak.V)

        SS_percentage = ss_a * 100 / (ss_a + es_a) 
        pair_count = len(self.stick_stack) // 2

        return SS_percentage, pair_count

    @classmethod
    def getNproperty(cls, p1, p2, p3, p4):
        '''
        Input: 4个点
        Return: 6个参数：v3-v1, v4-v2, A1, A2, k1, k2
        '''
        amplitude = np.array([p3.V - p1.V, p4.V - p2.V, p2.V - p1.V, p4.V - p3.V])
        if amplitude[2] < 0:
            amplitude *= -1 
        delta_tm = np.array([p2.TmIdx - p1.TmIdx, p4.TmIdx - p3.TmIdx])
        ll =[p1.TmIdx]
        ll += list(amplitude)
        ll += list(amplitude[2:] / delta_tm)
        return ll
     
class Center:
    c_L = []
    def __init__(self, *p_L):
        # len(p_L) >= 4
        self.status = 0
        self.point_stack = p_L[1:-1]
        self.tail = p_L[-1]
        self.drt = 0
        self.setHL()
        self.TmS = p2.TmIdx
        self.setTmE()

    def update1Point(self, point):
        if self.tail is None:
            self.tail = point
            return None

        v1, v2 = self.tail.V, point.V
        if (v1 > v2 and v2 >self.H) or (v1 < v2 and v2 < self.L):
            drt = int((v1 - v2)/abs(v1 - v2))
            self.new_center(drt, self.tail, point)
            self.close()
        else:
            self.point_stack.append(self.tail)
            self.setHL()
            self.setTmE()
            self.tail = point

    def close(self):
        d = self.getDepth()
        if d < 4:
            self.c_L.pop(self)
        self.status = 2
        return None

    def setHL(self):
        value_high = [p.V for p in self.point_stack[:-1] if p.drt == -1]
        value_low = [p.V for p in self.point_stack[:-1] if p.drt == 1]
        self.H = max(value_high)
        self.L = min(value_low)
        return None

    def setTmE(self):
        self.TmE = self.point_stack[-1].TmIdx
        return None

    def getDepth(self):
        return len(self.point_stack) - 1

    @classmethod
    def new_center(cls, drt, *p_L):        
        if len(p_L) < 2:
            print('to creat new center need more points!')
        else:
            nc = cls.__new__(cls)
            nt.status = 0
            nt.drt = drt
            if len(p_L) == 2:
                nt.point_stack = [p for p in p_L]
            else:
                nt.point_stack, nt_tail = p_L[:-1], p_l[-1]
            nt.setHL()
            nt.setTmE()
            cls.c_L.append(nt)
        return None

    @classmethod
    def findOpenC(cls):
        openC = [c for c in cls.c_L if c.statuc == 2]
        return openC

                



    def update(self, stick_stack):
        flag, new_center = 0, {}
        return flag, new_center

    @staticmethod
    def isPair(s1, s2):
        flag = False
        n = [s1.start.V, s1.peak.V, s2.peak.V]
        if (n2 < n0 and n2 > n1) or (n2 > n0 and n2 < n1):
            flag = True
        return flag

class Flag(object):
    def __init__(self, **kwargs):
        self.stick = kwargs['stick_stack'][0]
        self.center = Center(stick_stack = kwargs['stick_stack'][1:])

    def update(self, stick_stack):
        flag, new_flag = 0, {}
        return flag, new_flag

    def update1Stick(self, stick):
        flag = 0

        return flag 

#class TrendList(object):
