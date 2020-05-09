# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 14:38:46 2019

@author: ariesyun
"""

class Point:
    def __init__(self, time_index, value, drt):
        self.TmIdx, self.V, self.drt = time_index, value, drt
        
    def __repr__(self):
        return 'Point({0.TmIdx!r}, {0.V!r}, {0.drt!r})'.format(self)

    def __str__(self):
        return '({0.TmIdx!s}, {0.V!s}, {0.drt!s})'.format(self)
        
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
    def __init__(self, method, **kwargs):
        if method == 'init':
            #self.TmIdx_start, self.TmIdx_end = kwargs['k_bar'][4], kwargs['k_bar'][4]
            #self.O, self.C = kwargs['k_bar'][0], kwargs['k_bar'][3]
            self.start = Point(kwargs['k_bar'][4], kwargs['k_bar'][0], drt=0)
            self.end = Point(kwargs['k_bar'][4], kwargs['k_bar'][0], drt=0)
            self.range_value = kwargs['k_bar'][3]
            self.std_k_bar_stack = [StdK(k_bar=kwargs['k_bar'], drt=0)]
            self.peak = self.getPoint(0, 'init')
            self.peak_position = 0
            self.drt = 0
            
            self.reverse_count = 0
            self.status = 0 # 0:open; 1:ripe; 2:close

        elif method == 'trim':
            self.std_k_bar_stack = kwargs['std_k_bar_stack']
            self.drt = -self.std_k_bar_stack[0].drt
            self.peak_position = kwargs['peak_position']
            if self.drt == 1:
                self.O, self.C = self.std_k_bar_stack[0].L, self.std_k_bar_stack[-1].H
                self.start = self.getPoint(0, 'L')
                self.end = self.getPoint(-1, 'L')
                self.peak = self.getPoint(self.peak_position, 'H')
            elif self.drt == -1:
                self.O, self.C = self.std_k_bar_stack[0].H, self.std_k_bar_stack[-1].L
                self.start = self.getPoint(0, 'H')
                self.end = self.getPoint(-1, 'H')
                self.peak = self.getPoint(self.peak_position, 'L')
            self.range_value = self.peak.V
            self.reverse_count = 1
            self.status = 1 # 0:open, new peak与起点比较; 1:ripe, new peak与self.peak比较; 2:close

    def __repr__(self):
        return 'Stick({0.drt!r}, {0.status!r}, {0.start!r})'.format(self)

    def __str__(self):
        return '({0.drt!s}, {0.status!s}, {0.start!s})'.format(self)

    def update(self, k_bar):
        '''
        Return: 
        flag:  [0:stain; 1: updated; 2:close]
        new_stick:  dict
        '''
        self.TmIdx_end, self.C = k_bar[4], k_bar[3]
        flag = 0 # 0:stain; 1: updated; 2:close
        new_stick = ''
        if self.updateStdK(k_bar) != 0: # 更新stdK, stdK_stack，如果有新的stdK，则继续更新Stick
            peak, pp = self.findPeak()
            if peak == 0:
                flag = self.updateRange(k_bar)
                self.reverse_count += 1
                
            elif self.status == 0:
                
                if self.drt == 0:
                    self.drt = peak
                elif peak == self.drt:
                    flag = 0
                elif self.reverse_count > 3:
                    self.status = 1
                    self.peak_position = pp
                    self.peak = self.getPoint(pp)
                    self.reverse_count = 1
                    flag = 1      
            # Ripe, new peak 与 peak比较
            elif peak == self.peak.drt: # 
            
                if self.drt == 1 and self.std_k_bar_stack[-2].H >= self.peak.V:
                    self.peak_position = pp
                    self.peak = self.getPoint(pp)
                    self.reverse_count = 1
                    flag = 1                    
                elif self.drt == -1 and self.std_k_bar_stack[-2].L <= self.peak.V:
                    self.peak_position = pp
                    self.peak = self.getPoint(pp)
                    self.reverse_count = 1
                    flag = 1 
                else:
                    self.reverse_count += 1
                    flag = 0
            elif peak != self.peak.drt and self.reverse_count > 3:
                self.closeStick()
                new_stick = self.newStick(self.peak_position)
                flag = 2 
                
        return flag, new_stick
    
    def updateStdK(self, k_bar):
        is_new = 0
        is_new, trimed_k_bar = self.std_k_bar_stack[-1].update(k_bar)
        if is_new != 0:
            
            self.std_k_bar_stack.append(StdK(k_bar=trimed_k_bar, drt=is_new)) 
            self.reverse_count += 1
            
        return is_new
            
    def save(self):
        return None
    
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
            self.range_value = k_bar[1]
            self.status = 0
            flag = 1
        elif self.drt == -1 and k_bar[2] <= self.peak.V:
            self.range_value = k_bar[2]
            self.status = 0 
            flag = 1

        return flag
    
    def closeStick(self):
        self.status = 2
        return None
    
    def newStick(self, peak_position_in_std_stack):
        std_k_bar_stack = self.std_k_bar_stack[peak_position_in_std_stack:]
        peak_position = len(std_k_bar_stack) - 2

        new_stick = {
            'std_k_bar_stack' : std_k_bar_stack,
            'peak_position' : peak_position
        }
        return new_stick
    
    def getPoint(self, position_in_std_stack, method=None):
        if method is None:
            drt = self.std_k_bar_stack[position_in_std_stack].drt
            if drt == 1:
                p = Point(self.std_k_bar_stack[position_in_std_stack].TmIdx,
                     self.std_k_bar_stack[position_in_std_stack].H,
                     -1)
            elif drt == -1:
                p = Point(self.std_k_bar_stack[position_in_std_stack].TmIdx,
                     self.std_k_bar_stack[position_in_std_stack].L,
                     1)
        elif method == 'H':
            p = Point(self.std_k_bar_stack[position_in_std_stack].TmIdx,
                     self.std_k_bar_stack[position_in_std_stack].H,
                     -1)
        elif method == 'L':
            p = Point(self.std_k_bar_stack[position_in_std_stack].TmIdx,
                     self.std_k_bar_stack[position_in_std_stack].L,
                     1)
        elif method == 'init':
            p = Point(self.std_k_bar_stack[position_in_std_stack].TmIdx,
                     self.std_k_bar_stack[position_in_std_stack].L,
                     0)
        return p
    
    def beRipe(self):
        self.status == 1
                
class Trend:
    def __init__(self, method, **kwargs):
        if 'main_list' in kwargs.keys():
            self.main_list = kwargs['main_list']
            self.mp = kwargs['mp']
        else:
            self.main_list, self.mp = None, None

        if method == 'init':
            # from P
            self.stick_stack = [Stick('init', k_bar=kwargs['k_bar'])]
            self.start = self.getPoint(kwargs['k_bar'], method = 'init')
            self.end = self.getPoint(kwargs['k_bar'], 0, 'init')
            self.peak = self.getPoint(kwargs['k_bar'], 0, 'init')
            self.peak_position_in_ss = 0
            
            self.ES_stack = []
            self.SS_stack = []
            self.drt = 0            
            self.status = 0 

        elif method == 'trim': 
            if 'main_list' in kwargs.keys():
                self.stick_stack = [self.main_list[i] for i in self.mp]
            else:
                self.stick_stack = kwargs['stick_stack']

            self.drt = self.stick_stack[0].drt
            self.start = self.getPoint('ss', 0, 'start')
            self.end = self.getPoint('ss', -1, 'end')
        
            # from /
            if len(self.stick_stack) == 1:
                self.peak = self.getPoint('ss', 0, 'end')
                self.peak_point_in_ss = 1
                self.ES_stack = []
                self.SS_stack = [StdK(**self.stickToStdK(self.stick_stack[0]))]
                    
            #from /\, N
            else:
                self.setPeak()
                self.ES_stack = kwargs['ES_s']
                self.SS_stack = kwargs['SS_s']

            self.status = kwargs['status']
            print('new Trend:', end='')
            self.print_()
            
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
            self.peak = self.getPoint('ss', 0, 'end')
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
        self._updateStickStack()  
        flag = 0  # 0:stain; 1: updated; 2:cloesd;
        new_trend = {}           

        if self.drt == 0: # 不需要以stick_stack的末尾进行更新
            self.drt = self.stick_stack[0].drt
            self.SS_stack = [StdK(**self.stickToStdK(self.stick_stack[0]))]
            flag = 1

            
        elif self.status == 0: # 不需要以stick_stack的末尾进行更新
            if len(self.stick_stack) == 3:
                if (self.stick_stack[1].peak.V - self.stick_stack[0].start.V)*self.drt < 0:
                    self.status = 2
                    new_trend = self.newTrend(0)
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

    def updateEndP(self, k_bar):
        self.end = self.getPoint(k_bar, method = 'peak')
        return None

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
                self.peak = self.getPoint(k_bar, method='H')
                flag = 1
            elif self.drt == -1 and k_bar[2] <= self.peak.V:
                self.peak = self.getPoint(k_bar, method='L')
                flag = 1
        elif stick is not None:
            if self.drt == stick.drt and (self.drt * stick.peak.V) >= (self.drt * self.peak.V):
                self.peak = self.getPoint(stick, 'end')
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
            self.peak = self.getPoint(k, 0, method='H')
            flag = 1
        elif self.drt == -1 and k[2] < self.peak.V:
            self.peak = self.getPoint(k, 0, method = 'L')
            flag = 1
        return flag
    
    def setPeak(self):
        # iterate ss to set peak point and pp in ss
        self.peak = self.getPoint('ss', 0, 'end')
        self.peak_point_in_ss = 1
        pp = 0
        if self.drt == 1 and len(self.stick_stack) >= 3:
            for stick in self.stick_stack[2::2]:
                pp += 2
                if stick.peak.V > self.peak.V:
                    self.peak = self.getPoint('ss', pp, 'end')
                    self.peak_point_in_ss = pp + 1 
        elif self.drt == -1 and len(self.stick_stack) >= 3:
            for stick in self.stick_stack[2::2]:
                pp += 2
                if stick.peak.V < self.peak.V:
                    self.peak = self.getPoint('ss', pp, 'end')
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
    
    def newTrend(self, case):
        mp = None
        if case == 0:
            stick_stack = [self.stick_stack[-2]]
            if self.mp is not None:
                mp = self.mp[-2:]
            new_trend = {'stick_stack': stick_stack,
                        'mp': mp,
                        'main_list': self.main_list,
                        'ES_s': [],
                        'SS_s': [StdK(**self.stickToStdK(stick_stack[0]))],
                        'status': 0}
        elif case == 1:
            peak_point_in_stick_stack = self.findIdxInSS(self.ES_stack[-1].TmIdx)
            if self.mp is not None:
                mp = self.mp[peak_point_in_stick_stack:]
            stick_stack = self.stick_stack[peak_point_in_stick_stack:]
            new_trend = {'stick_stack': stick_stack,
                        'mp': mp,
                        'main_list': self.main_list,
                        'ES_s': self.reduceES(stick_stack),
                        'SS_s': [StdK(**self.stickToStdK(stick)) for stick in stick_stack[::2]],
                        'status': 1}

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
            new_trend1 = {'stick_stack':stick_stack1,
                          'mp': mp1,
                          'main_list': self.main_list,
                          'ES_s': self.reduceES(stick_stack1),
                          'SS_s': [StdK(**self.stickToStdK(stick)) for stick in stick_stack1[::2]],
                          'status': 1}
            stick_stack2 = self.stick_stack[self.findIdxInSS(self.ES_stack[-1].TmIdx):self.findIdxInSS(pp_TmIdx)]
            if self.mp is not None:
                mp2 = self.mp[self.findIdxInSS(self.ES_stack[-1].TmIdx):self.findIdxInSS(pp_TmIdx)]
            new_trend2 = {'stick_stack':stick_stack2,
                          'mp': mp2,
                          'main_list': self.main_list,
                          'ES_s': self.reduceES(stick_stack2, 0),
                          'SS_s': [StdK(**self.stickToStdK(stick)) for stick in stick_stack2[::2]],
                          'status': 2}
            
            new_trend = [new_trend2, new_trend1]
        
        return new_trend
    
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
    
    # evaluation function:    
    def eva(self):
        self.tm_diff = self.peak.TmIdx - self.start.TmIdx
        self.v_diff = self.peak.V - self.start.TmIdx
        self.k = self.v_diff - self.tm_diff
        self.ss_valid = self.stick_stack[:self.findIdxInSS(self.peak.TmIdx) + 1]
        self.center_stack = self.getCenterStack(self.ss_valid)
        return None

    def getCenterStack():
        return center_stack
     
    def print_(self):
        print('drt:{:>2},status:{},start[{},{:>6},{:>2}],peak[{},{:>6},{:>2},ss:{}]'.format(
        self.drt, self.status, self.start.TmIdx, self.start.V, self.start.drt
        ,self.peak.TmIdx, self.peak.V, self.peak.drt, len(self.stick_stack)),end='')
        if len(self.ES_stack) > 0:
            print(',ES:{}[{},{:>6},{:>6},{:>2}]'.format(
                len(self.ES_stack)
                , self.ES_stack[-1].TmIdx, self.ES_stack[-1].H, self.ES_stack[-1].L, self.ES_stack[-1].drt
                ))
        else:
            print(',ES:', len(self.ES_stack), end='')
        if len(self.SS_stack) > 0:
            print(',SS:{}[{},{:>6},{:>6},{:>2}]'.format(
                len(self.SS_stack)
                , self.SS_stack[-1].TmIdx, self.SS_stack[-1].H, self.SS_stack[-1].L, self.SS_stack[-1].drt
                ))
        else:
            print(',SS:', len(self.SS_stack), end='')

class Center:
    def __inti__(self, pair):
        self.start = 0


    def update(self, s):
        # input: Stick or Trend, only start/peak/drt be used.
        flag, new_center = 0, {}
        return flag, new_center

    @staticmethod
    def isPair(s1, s2):
        flag = False
        n = [s1.start.V, s1.peak.V, s2.peak.V]
        if (n2 < n0 and n2 > n1) or (n2 > n0 and n2 < n1):
            flag = True
        return flag
