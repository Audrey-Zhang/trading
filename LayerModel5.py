# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 14:38:46 2019

@author: ariesyun
"""
import numpy as np
from frame import *

class Node():
    pass

class UnaryOperator(Node):
    def __init__(self,operand):
        self.operand = operand
        
class BinaryOperator(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
class StackOperator(Node):
    def __init__(self, items):
        self.items = items

class Add(BinaryOperator):
    pass

class Sub(BinaryOperator):
    pass

class Mul(BinaryOperator):
    pass

class Div(BinaryOperator):
    pass

class Negate(UnaryOperator):
    pass

class gt(BinaryOperator):
    pass

class lt(BinaryOperator):
    pass

class eq(BinaryOperator):
    pass

class ge(BinaryOperator):
    pass

class le(BinaryOperator):
    pass

class All(StackOperator):
    pass

class Any(StackOperator):
    pass

class choose(BinaryOperator):
    pass

class Number(Node):
    def __init__(self, value):
        self.value = value
        
class NodeVisitor:
    def evaluate(self, node):
        methname = 'visit_' + type(node).__name__
        meth = getattr(self, methname, None)
        if meth is None:
            if type(node) in [int,float,str]:
                return node
            raise RuntimeError('No {} method'.format('visit_' + type(node).__name__))
        return meth(node)
    
    def test(self,print_list):
        #print(print_list)
        pass
    
    def visit_Number(self, node):
        return node.value
    
    def visit_choose(self, node):
        self.test(node.left[node.right])
        return node.left[node.right]
    
    def visit_All(self, node):
        self.test(all([self.evaluate(n) for n in node.items]))
        return all([self.evaluate(n) for n in node.items])
    
    def visit_Any(self, node):
        self.test(any([self.evaluate(n) for n in node.items]))
        return any([self.evaluate(n) for n in node.items])
    
    def visit_Add(self, node):
        self.test(self.evaluate(node.left) + self.evaluate(node.right))
        return self.evaluate(node.left) + self.evaluate(node.right)
    
    def visit_Sub(self, node):
        self.test(self.evaluate(node.left) - self.evaluate(node.right))
        return self.evaluate(node.left) - self.evaluate(node.right)
    
    def visit_Mul(self, node):
        self.test(self.evaluate(node.left) * self.evaluate(node.right))
        return self.evaluate(node.left) * self.evaluate(node.right)
    
    def visit_Div(self, node):
        self.test(self.evaluate(node.left) / self.evaluate(node.right))
        return self.evaluate(node.left) / self.evaluate(node.right)
        
    def visit_Negate(self, node):
        self.test(-self.evaluate(node.operand))
        return -self.evaluate(node.operand)
    
    def visit_gt(self, node):
        self.test(self.evaluate(node.left) > self.evaluate(node.right))
        return self.evaluate(node.left) > self.evaluate(node.right)
        
        
    def visit_lt(self, node):
        self.test(self.evaluate(node.left) < self.evaluate(node.right))
        return self.evaluate(node.left) < self.evaluate(node.right)
        
    def visit_eq(self, node):
        self.test(self.evaluate(node.left) == self.evaluate(node.right))
        return self.evaluate(node.left) == self.evaluate(node.right)
        
    def visit_ne(self, node):
        self.test(self.evaluate(node.left) != self.evaluate(node.right))
        return self.evaluate(node.left) != self.evaluate(node.right)
        
    def visit_ge(self, node):
        self.test(self.evaluate(node.left) >= self.evaluate(node.right))
        return self.evaluate(node.left) >= self.evaluate(node.right)
            
    def visit_le(self, node):
        self.test(self.evaluate(node.left) <= self.evaluate(node.right))
        return self.evaluate(node.left) <= self.evaluate(node.right)

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
                method = 'end'
            else:
                method = 'start'
        elif method == 'L':
            if s.drt == -1:
                method = 'start'
            else:
                method = 'end'

        if method == 'start':
            return s.start
        elif method =='end':
            return s.end
        elif method =='peak':
            return s.peak

    def is_peak(self, drt, ref_point):
        if drt == 1 and self.V > ref_point.V:
            return True
        elif drt == -1 and self.V < ref_point.V:
            return True
        else:
            return False
        
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
    level = 0
    mm = Market()
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
        return 'Stick(drt:{0.drt!r}, lv:{0.level!r}, {0.start!r})'.format(self)

    def __str__(self):
        return '(drt:{0.drt!s}, lv:{0.level!s}, {0.start!s})'.format(self)

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
                flag = self.updateRange(k_bar) # flag = 0/10
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
            
        self.sendEvent(flag) 
                
        return flag
    
    def sendEvent(self, flag):
        event_list = ['', 'LVUPD', 'NEW','','','','','','','','PEAK']
        if event_list[flag] != '':
            Event(level=self.level, obj_name = self.__class__.__name__, event_name=event_list[flag])
        return None

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
            self.peak = Point.getPoint('H', k_bar)
            flag = 10
        elif self.drt == -1 and k_bar[2] <= self.peak.V:
            self.status = 0 
            self.peak_std_bar = self.std_k_bar_stack[-1]
            self.peak = Point.getPoint('L', k_bar)
            flag = 10

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

    def distr(self):
        k_L = [[k[1],k[2]] for k in self.mm.dt if k[4]>= self.start.TmIdx and k[4]<= self.peak.TmIdx]
        bin_cnt = self.mm.bin_cnt
        interval = (self.peak.V - self.start.V)*self.drt/ bin_cnt
        L = min(self.peak.V, self.start.V)
        H = max(self.peak.V, self.start.V)
        scale = [L]
        for i in list(range(1,bin_cnt)):
            scale.append(scale[i-1]+interval)
        scale.append(H)

        distr = np.zeros(bin_cnt)
        for k in k_L:
            distr_k = np.zeros(bin_cnt)
            for i in list(range(bin_cnt)):
                if (min(k) <= scale[i] <= max(k)) or (min(k) <= scale[i+1] <= max(k)):
                    distr_k[i] = 1
            cnt = distr_k.sum()
            if cnt != 0:
                distr_k = distr_k/cnt
            else:
                distr_k = 0


            distr = distr + distr_k
        return [scale, distr]

                
class Trend(object):
    lv_L = []
    level = -1
    ML = []
    m = Market()
    def __init__(self, method, **kwargs):
        self.lv_L.append(self)

        self.mp = kwargs['mp']

        if method == 'init':
            # from P
            self.stick_stack = [self.ML[0]]
            self.start = Point.getPoint('init', kwargs['k_bar'])
            self.end = Point.getPoint('init', kwargs['k_bar'])
            self.peak = Point.getPoint('init', kwargs['k_bar'])
            self.pp = 0
            
            self.ES_stack = []
            self.SS_stack = []
            self.drt = 0            
            self.status = 0 

    def __repr__(self):
        return 'Trend{0.level}({0.drt!r}, {0.status!r}, {0.start!r})'.format(self)
    
    def __str__(self):
        return '({0.drt!s}, {0.start!s})'.format(self)

    def update2(self):
        flag = 0
        treated = self
        print('Lv{}.update2()_begin: flag:{}, treated.status:{},treated.mp:{}'.\
                format(self.level, flag, treated.status, treated.mp))
        
        # Check ML to find new sticks   
        if len(self.ML) - self.mp[-1] > 1:
            new_mp = [i for i in range(self.mp[-1]+1, len(self.ML))]
        # iterate stick_stack to update Trend
        for i in new_mp:
            treated.stick_stack.append(treated.ML[i])
            treated.mp.append(i)
            #treated.updatePp(treated.stick_stack[-1])
            flag, treated = treated.update1Stick()
            print('Lv{}.update2(): flag:{}, treated.status:{},treaded.drt:{},treated.mp:{}'.\
                format(self.level, flag, treated.status, treated.drt, treated.mp))
        self.sendEvent(flag)  #？？don't need to send for each
        return flag

    def update1Stick(self):
        #self.updateEndP() # use signal engine!!!
        #self._updateStickStack()  
        flag = 0  # 0:stain; 1: updated; 2:cloesd;
        new_trend = self           

        if self.drt == 0: # 不需要以stick_stack的末尾进行更新; Trend currently is a Point
            self.drt = self.stick_stack[0].drt
            self.SS_stack = [StdK(**self.stickToStdK(self.stick_stack[0]))]
            self.ES_stack = [StdK(**self.stickToStdK(self.stick_stack[1]))]
            self.peak = self.stick_stack[1].start
            self.pp = 1
            flag = 0

            
        elif self.status == 0: # 不需要以stick_stack的末尾进行更新; Trend currently is / or in 1st N or 1st flag; 
            if len(self.stick_stack) == 3: # stick_stack[-1]未完成，及时确认前2个st是否为pair
                print('Lv{0}.update1st:status={1},mp:{3},{2.start},{2.peak},{2.end},{2.ES_stack}'\
                .format(self.level, self.status, self, len(self.mp)))
                if (self.stick_stack[1].peak.V - self.stick_stack[0].start.V)*self.drt < 0:
                    self.status = 2
                    new_trend = self.produceNewTrend(0)
                    flag = 1
                else:               
                    self.ES_stack = [StdK(**self.stickToStdK(self.stick_stack[1]))]
                    self.updatePeakP(st_idx_in_ss=2)
                    self.status = 1
                    flag = 1
                    
            
        elif self.status == 1:  # 需要以stick_stack的末尾进行更新       
            tmp_stdk = self.stickToStdK(self.stick_stack[-2])

            # 处理eigen_stick:
            if self.drt != tmp_stdk['drt']:
                
                if self.drt == 1: # /...\
                    if tmp_stdk['L'] < self.ES_stack[-1].L:
                        if tmp_stdk['H']> self.ES_stack[-1].H:   # case2: \\外包
                            if tmp_stdk['L'] < self.start.V:
                                self.status = 2
                                new_trend =  self.produceNewTrend(0)
                                flag = 2
                            else:
                                tmp_stdk['L'] = self.ES_stack[-1].L
                                self.ES_stack.append(StdK(**tmp_stdk))
                                flag = 1
                        elif tmp_stdk['H'] <= self.ES_stack[-1].H:  # case1：反向
                            print('Lv{}.upd1st():case1, status:{}, mp:{},pp:{}'.\
                                format(self.level, self.status,self.mp, self.pp))
                            self.status = 2
                            new_trend = self.produceNewTrend(1) 
                            flag = 2
                    elif (tmp_stdk['H'] <= self.ES_stack[-1].H and
                         tmp_stdk['L'] >= self.ES_stack[-1].L):        # case3: trimUpdate
                        self.ES_stack[-1].L = tmp_stdk['L']
                        flag = 0 # peak不更新，不发UPD event!! 需check还有其它类似情况么？
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
                            print('Lv{}.upd1st():case1, status:{}, mp:{},pp:{}'.\
                                format(self.level, self.status,self.mp, self.pp))
                            self.status = 2
                            new_trend = self.produceNewTrend(1)
                            flag = 2
                            
                    elif (tmp_stdk['L'] >= self.ES_stack[-1].L and
                         tmp_stdk['H'] <= self.ES_stack[-1].H):
                        self.ES_stack[-1].H = tmp_stdk['H']
                        # self.ES_stack[-1].merged += 1  # ！！！！
                        flag = 0 
                    elif tmp_stdk['L'] < self.ES_stack[-1].L:
                        self.ES_stack.append(StdK(**tmp_stdk))
                        flag = 1
                        
            
            # 处理syntropy_stick:
            elif self.drt == tmp_stdk['drt']:
                self.updatePeakP(st_idx_in_ss=-1)
                '''
                if self.drt == 1:
                    if tmp_stdk['H'] > self.SS_stack[-1].H:
                        if self.ES_stack[-1].merged > 1 and tmp_stdk['H'] < self.ES_stack[-1].H:
                            self.status = 2
                            new_trend = self.produceNewTrend(21)
                            flag = 3
                            
                        else:
                            self.SS_stack.append(StdK(**tmp_stdk))
                            flag = 1

                    else:
                        self.SS_stack.append(StdK(**tmp_stdk))
                        flag = 0
                        
                        
                elif self.drt == -1:
                    if tmp_stdk['L'] < self.SS_stack[-1].L:
                        if self.ES_stack[-1].merged > 1  and tmp_stdk['L'] > self.ES_stack[-1].L:
                            self.status = 2
                            new_trend = self.produceNewTrend(21)
                            flag = 3
                            
                        else:
                            self.SS_stack.append(StdK(**tmp_stdk))
                            flag = 1
                    else:
                        self.SS_stack.append(StdK(**tmp_stdk))
                        flag = 1
                '''
        return flag, new_trend

    def sendEvent(self, flag):
        event_list = ['', 'LVUPD', 'NEW', 'NEW']
        if event_list[flag] != '':
            Event(level=self.level, obj_name = self.__class__.__name__, event_name=event_list[flag])
        return None

    def updateEndP(self, k_bar):
        if self.drt == 1:
            method = 'H'
        else:
            method = 'L'
        self.end = Point.getPoint(method, k_bar)
        return None
    
    def updatePeakP(self, k_bar=None, st_idx_in_ss=None):
        '''
        update self.peak OR self.pp
        '''
        flag = 0
        if k_bar is not None: # update self.peak  # not used!!
            if self.drt == 1 and k_bar[1] >= self.peak.V:
                self.peak = Point.getPoint('H', k_bar)
                
                flag = 1
            elif self.drt == -1 and k_bar[2] <= self.peak.V:
                self.peak = Point.getPoint('L', k_bar)
                
                flag = 1
        elif st_idx_in_ss is not None: # check and update self.pp
            stick = self.stick_stack[st_idx_in_ss]
            print('{}.updatedPeakP(st_idx_in_ss):last_st_start:{},peak{},drt:{}'.format(self.__class__.__name__,
                stick, self.peak, self.drt))
   
            try:
                self.pp
            except:
                if stick.drt != self.drt: 
                    self.peak = stick.start
                    self.pp = self.stick_stack.index(stick)
                    flag = 1
                else:
                    pass

            else:
                if stick.drt == self.drt:
                    return flag
                elif stick.start.is_peak(self.drt, self.peak):
                    print('{}.updatedPeakP(st_idx_in_ss):FIND PEAK'.format(self.__class__.__name__))
                    self.peak = stick.start
                    self.pp = self.stick_stack.index(stick)
                    flag = 1                

        return flag

    def updatePp(self, st=None, time_index=None, pp=None):   # Unused!!!
        if time_index is not None:
            self.pp = self.findIdxInSS(time_index)
        elif st is not None:
            if st.start == self.peak:
                self.pp = self.stick_stack.index(st)
        else:
            self.pp = pp
        return None

    def _updateStickStack(self):
        '''
        self.mp -> append one
        self.stick_stack  -> append one
        '''
        i  = len(self.ML) - 1
        if (i - self.mp[-1]) > 0:
            self.mp.append(self.mp[-1]+1)
            self.stick_stack = self.ML[self.mp[0]:self.mp[-1]+1]
            return 0
        else:
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
        # mp = None
        if case == 0:
            #stick_stack = [self.stick_stack[-2]]
            mp = self.mp[-2:]
            nt_dict = {'mp': mp,
                        'pp': 1,
                        'status': 0}
            self.newTrend(**nt_dict)


        elif case == 1:
            #peak_point_in_stick_stack = self.findIdxInSS(self.ES_stack[-1].TmIdx)
            mp = self.mp[self.pp:]
            print('Lv{}.produceNewTrend:case1, mp={}'.format(self.level,mp))
            #stick_stack = self.stick_stack[peak_point_in_stick_stack:]
            nt_dict = {'mp': mp,
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
                          'ES_s': self.reduceES(stick_stack1),
                          'SS_s': [StdK(**self.stickToStdK(stick)) for stick in stick_stack1[::2]],
                          'status': 1}
            stick_stack2 = self.stick_stack[self.findIdxInSS(self.ES_stack[-1].TmIdx):self.findIdxInSS(pp_TmIdx)]
            if self.mp is not None:
                mp2 = self.mp[self.findIdxInSS(self.ES_stack[-1].TmIdx):self.findIdxInSS(pp_TmIdx)]
            nt_dict2 = {'stick_stack':stick_stack2,
                          'mp': mp2,
                          'ES_s': self.reduceES(stick_stack2, 0),
                          'SS_s': [StdK(**self.stickToStdK(stick)) for stick in stick_stack2[::2]],
                          'status': 2}
            
            self.newTrend(**nt_dict2)
            self.newTrend(**nt_dict1)
        
        
        new_trend = self.lv_L[-1]
        return new_trend

    def distr(self, st_list=None):
        bin_cnt = self.m.bin_cnt
        if st_list is None:
            if self.status == 2:
                st_list = [self.ML[i] for i in self.mp[:self.pp]]
            else:
                st_list = [self.ML[i] for i in self.mp]
        his_L = [st.distr() for st in st_list]
        # new scale
        H = max([his[0][-1] for his in his_L])
        L = min([his[0][0] for his in his_L])
        
        scale = [L]
        interval = (H-L)/bin_cnt
        for i in list(range(1,bin_cnt)):
            scale.append(scale[i-1] + interval)
        scale.append(H)

        distr = np.zeros(bin_cnt)
        for his in his_L:
            for i in list(range(bin_cnt)):
                s = his[0][i]
                for j in list(range(bin_cnt)):
                    if scale[j] <= s < scale[j+1]:
                        distr[j] += his[1][i]
        self.his = [scale, distr]

        self.core_index = distr.argmax()
        self.core = scale[self.core_index]
        self.ccHL = self.m.ccHL(self.his)
        self.cc = (self.ccHL[1] - self.ccHL[0])/bin_cnt
        return self.his
    
    @classmethod
    def newTrend(cls, **kwargs): 
        new_trend = cls.__new__(cls)
        new_trend.ML = cls.ML

        cls.lv_L.append(new_trend)

        new_trend.mp = kwargs['mp']
        new_trend.stick_stack = [new_trend.ML[i] for i in new_trend.mp]
            
        new_trend.drt = new_trend.stick_stack[0].drt
        new_trend.SS_stack = [StdK(**new_trend.stickToStdK(stick)) for stick in new_trend.stick_stack[::2]]
        
        new_trend.start = Point.getPoint('start', new_trend.stick_stack[0])
        new_trend.end = Point.getPoint('end', new_trend.stick_stack[-1])
        
        
        # from /
        if len(new_trend.stick_stack) == 2:
            if 'pp' in kwargs.keys():
                new_trend.pp = kwargs['pp']
            new_trend.peak = Point.getPoint('end', new_trend.stick_stack[0])  
            new_trend.ES_stack = [StdK(**new_trend.stickToStdK(new_trend.stick_stack[1]))]   
            new_trend.pp = 1       
        #from /\, N
        else:
            if 'pp' in kwargs.keys():
                new_trend.pp = kwargs['pp']
                new_trend.peak = Point.getPoint('start', new_trend.stick_stack[new_trend.pp])
            else:
                new_trend.peak = Point.getPoint('end', new_trend.stick_stack[0])  
                for st_idx in list(range(1,len(new_trend.stick_stack))):
                    new_trend.updatePeakP(st_idx_in_ss=st_idx)
            new_trend.ES_stack = new_trend.reduceES(new_trend.stick_stack)

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
    
    def setPeak(self): #暂时没用
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

    @classmethod 
    def findBigStick(cls, pct_spc): 
        v1, v2 = cls.lv_L[-2].start.V, cls.lv_L[-1].start.V
        pct = (v2 - v1)*cls.lv_L[-2].drt / v1
        print('Trend{}: v1:{:.2f}, v2:{:.2f}, drt:{}, pct:{:.2%}'.format(
            cls.level, v1, v2, cls.lv_L[-2].drt, pct))
        if pct > pct_spc:
            msg = {}
            Singal('BIGST', level=cls.level, msg = msg)
        return None

    # ============================ Evaluation Method =====================================
    def amp(self):

        amp_eq = [(st.peak.V - st.start.V)*st.drt for st in self.stick_stack 
        if (st.drt == self.drt and st.start.TmIdx < self.peak.TmIdx )]
        amp_op = [(st.peak.V - st.start.V)*st.drt for st in self.stick_stack 
        if (st.drt != self.drt and st.start.TmIdx < self.peak.TmIdx )]
        return sum(amp_eq), sum(amp_op)

class CenterStrict(object):
    m = Market()
    def __init__(self, stick_list, m):
        self.level = stick_list[0].level
        self.TmS = stick_list[0].start.TmIdx
        self.group_TmS = self.TmS

        self.initby2Stick(stick_list[:3])

        m.CenterStrict_LD[self.group_TmS] = [self]
        self.group_L = m.CenterStrict_LD[self.group_TmS]

        if len(stick_list) > 3:
            for st in stick_list[3:]:
                if not self.update1Stick(st):
                    idx = stick_list.index(st)
                    self.newAndCopy(stick_list[idx - 2:], self.group_TmS, m)
                    break
    
    def update1Stick(self, stick):
        v = stick.start.V 
        flag = self.isInHL(v)
        updated  = True
        if self.inside and flag:
            self.cnt += 1
        elif not self.inside and flag:
            self.updateHL(v)
            self.inside = flag # True
            self.TmE = stick.start.TmIdx
            self.cnt += 2
        elif self.inside and not flag:
            self.inside = flag  # = False
        elif not self.inside and not flag:
            pre_v = self.point_L[-1].V 
            if self.diffside(pre_v, v):
                self.updateHL(pre_v)
                self.updateHL(v)
                self.TmE = stick.start.TmIdx
                self.inside = True
                self.cnt += 2
            else: # same side
                updated = False
        self.point_L.append(stick.start)
        return updated

    def __str__(self):
        return '({0.TmS!s}, {0.L!s}, {0.H!s})'.format(self)

    @classmethod
    def newAndCopy(cls, stick_list, TmS, m):
        new_center = cls.__new__(cls)
        new_center.level = stick_list[0].level
        new_center.TmS = stick_list[0].start.TmIdx
        new_center.group_TmS = TmS

        new_center.initby2Stick(stick_list[:3])

        new_center.group_L = m.CenterStrict_LD[new_center.group_TmS]
        new_center.group_L.append(new_center)

        if len(stick_list) > 3:
            for st in stick_list[3:]:
                if not new_center.update1Stick(st):
                    idx = stick_list.index(st)
                    new_center.newAndCopy(stick_list[idx - 2:], TmS, m)
                    break
        return None


    def isInHL(self, v):
        if v >= self.L and v <= self.H:
            return True
        else:
            return False

    def updateHL(self, v):
        self.H = max(self.H, v)
        self.L = min(self.L, v)
        return None

    def diffside(self, v1, v2):
        if v1 > self.H and v2 > self.H:
            return False
        elif v1 < self.L and v2 < self.L:
            return False
        return True

    def initby2Stick(self, stick_list):
        self.point_L = [st.start for st in stick_list]
        values = np.array([st.start.V for st in stick_list])        
        self.H = values.max()
        self.L = values.min()
        self.inside = True
        self.TmE = stick_list[-1].start.TmIdx
        self.cnt = 1
        return None


class Pair(object):
    ML = ''
    level = ''
    L = []
    m = Market()

    def __init__(self, st_idx):
        first_st = self.ML[st_idx]
        self.drt, self.S, self.P = first_st.drt, first_st.start.V, first_st.peak.V
        self.TmS = first_st.start.TmIdx
        #self.L = min(first_st.start.V, first_st.peak.V)
        #self.H = max(first_st.start.V, first_st.peak.V)

        self.L.append(self)

        self.index = [st_idx]
        self.chain_layer = -1
        self.status = 0

        self.cc =''
        self.ccHL = np.zeros(4)

    def __repr__(self):
        discription = 'Pair{0.chain_layer}(TmS:{0.TmS!r}, {0.drt!r}, {0.index!r})'.format(self)  
        return  discription

    def output(self):
        description = self.calFeatures()
        description['TmS'] = self.TmS
        description['chain_layer'] = self.chain_layer
        description['index'] = self.index
        return description

    def update(self, st_idx):
        self.index.append(st_idx)
        return None

    def close(self):
        self.status = 1    
        return None  

    def isFollow(self, post_pair):
        if (post_pair.index[-1] + 1) ==  self.index[0]:
            return True
        return False  

    def isContinuous(self, follow_pair):
        if (self.index[-1] + 1) == follow_pair.index[0]:
            return True
        return False
    # ============================ evaluation method ===================================
    def calFeatures(self):
        self.distr()

        feature_name_list = ['drt', 's_v', 'p_v', 's_tm', 'b_tm',
        'b_w', 'cl', 'ch', 'c_drt', 'cc',
        'c_c_level','a','c_a','k','',
        'is_flag','','','','']
        values = np.zeros(20)
      
        values[0] = self.drt
        values[1] = self.S
        values[2] = self.P
        values[3] = self.ML[self.index[0]].peak.TmIdx - self.ML[self.index[0]].start.TmIdx
        values[4] = self.ML[self.index[-1]].peak.TmIdx - self.ML[self.index[0]].peak.TmIdx

        values[5] = len(self.index)
        values[6] = self.ccHL[2]
        values[7] = self.ccHL[3]
        values[8] = self.core_index - 10
        values[9] = self.core

        values[10] = self.cc
        values[11] = abs(self.P - self.S)
        values[12] = self.ccHL[3] - self.ccHL[2]
        values[13] = values[11] / values[3]

        # judge is flag or not
        # c_drt*drt > 3 and c_c_level < 0.6
        values[15] = 0
        if values[8]*values[0] > 3 and values[10] < 0.6:
            values[15] = 1      
        
        


        values = list(values)
        features = {k:v for k,v in zip(feature_name_list, values)}
        return features

    def HL_2nd(self): # calculate block range
        st_2nd = self.ML[self.index[1]]
        H = max(st_2nd.start.V, st_2nd.peak.V )
        L = min(st_2nd.start.V, st_2nd.peak.V )
        return H, L
        

    def distr(self, st_list=None):
        bin_cnt = self.m.bin_cnt
        if st_list is None:
            st_list = [self.ML[i] for i in self.index]
        his_L = [st.distr() for st in st_list]
        # new scale
        H = max([his[0][-1] for his in his_L])
        L = min([his[0][0] for his in his_L])
        
        scale = [L]
        interval = (H-L)/bin_cnt
        for i in list(range(1,bin_cnt)):
            scale.append(scale[i-1] + interval)
        scale.append(H)

        distr = np.zeros(bin_cnt)
        for his in his_L:
            for i in list(range(bin_cnt)):
                s = his[0][i]
                for j in list(range(bin_cnt)):
                    if scale[j] <= s < scale[j+1]:
                        distr[j] += his[1][i]
        self.his = [scale, distr]

        self.core_index = distr.argmax()
        self.core = scale[self.core_index]
        self.ccHL = self.m.ccHL(self.his)
        self.cc = (self.ccHL[1] - self.ccHL[0])/bin_cnt
        return self.his

    # ==================== method only called by object method =========================
    def inside(self, stick):
        if len(self.index) < 3:
            self.updateP()
        if stick.drt == self.drt:
            if self.drt*(stick.peak.V - self.P) <= 0:
                return True
            else:
                return False
        elif stick.drt != self.drt:
            if self.drt*(stick.peak.V - self.S) >= 0:
                return True
            else:
                return False

    def updateP(self):
        # update self.P by self.ML[self.index[0]]
        self.P = self.ML[self.index[0]].peak.V
        return None

    # ============================= classmethod =========================================
    @classmethod
    def newPair(cls, st_idx):
        cls.L[-1].distr()
        new_pair = cls.__new__(cls)
        cls.L.append(new_pair)

        first_st = cls.ML[st_idx]
        new_pair.drt, new_pair.S, new_pair.P = first_st.drt, first_st.start.V, first_st.peak.V
        new_pair.TmS = first_st.start.TmIdx
        new_pair.index = [st_idx]
        
        new_pair.chain_layer = -1
        new_pair.status = 0
        
        return new_pair 

    @classmethod
    def remove(cls, pair_obj):
        cls.L.remove(pair_obj)
        return None   


class PairChain(object):
    m = Market()
    def __init__(self, level, sig_name, st_idx_list=None):
        self.level = level
        self.sig_name = sig_name
        self.ML = self.m.findList('pair', level) 
        L = self.m.findList('pairchain', level) 
        L.append(self)
        self.cL = [[self.ML[0]], [], []]
        

        if st_idx_list is not None:
            self.update2(st_idx_list)
    
    def update2(self, st_idx_list=None):
        if st_idx_list is None:
            if self.cL[0][0].drt == 0:
                new_pair = self.cL[0][0].newPair(0)
                new_pair.chain_layer = 0
                self.cL[0] = [new_pair]
                self.update(1)
                return None
            tm_idx_last = max((l[-1].index[-1] for l in self.cL if len(l)>0))
            st_idx_list = list(range(tm_idx_last + 1, len(self.m.findList('st', self.level)))) 
       
        for st in st_idx_list:
            self.update(st)
        return None

    def update(self, st_idx=None):
        new_pair = self.cL[0][-1].newPair(st_idx)
        new_flag = 0
        L = self.m.findList('st', self.level)
        st = L[st_idx]
        for i in range(len(self.cL)):
            if new_flag == 0:
                if len(self.cL[i]) == 0 or self.cL[i][-1].status == 1:
                   new_pair.chain_layer = i
                   new_flag = 1
                   self.cL[i].append(new_pair)

                elif self.cL[i][-1].status == 0:
                    if self.cL[i][-1].inside(st):
                        self.cL[i][-1].update(st_idx)
            
                    else: 
                        self.cL[i][-1].close()
                        new_pair.chain_layer = i
                        new_flag = 1
                        self.cL[i].append(new_pair)
            elif  new_flag == 1:
                if len(self.cL[i]) == 0 or self.cL[i][-1].status == 1:
                    break
                elif self.cL[i][-1].status == 0:
                    self.cL[i][-1].close()
        if new_flag == 0:
            new_pair.remove(new_pair)
        else:
            self.sendEvent()
        return None

    def updateLastSt(self):
        st = self.cL[0][0].ML[-1]
        last_pair =  self.cL[0][0].L[-1] 
        
        if st.start.TmIdx == last_pair.TmS: # the last Pair must be a one-stick Pair
            aim_layer = last_pair.chain_layer # here should not be a reference!!!!!!
            last_pair.updateP()
            
        else:
            aim_layer = 10

        for i in range(len(self.cL)):
            if i == aim_layer:
                break
            elif i < aim_layer:  # one-stick is in lower layer
                if not self.cL[i][-1].inside(st):
                    self.cL[i][-1].index.pop()
                    self.cL[i][-1].close()   
                    if aim_layer == 10:    
                        last_pair =  self.cL[0][-1].newPair(len(self.cL[0][0].ML) - 1)          
                    last_pair.chain_layer = i
                    aim_layer = last_pair.chain_layer
                    self.cL[i].append(last_pair)
            else:
                if len(self.cL[i][-1].index) == 1:
                    self.cL[i].pop()
                    break
                else:
                    self.cL[i][-1].index.pop()
                    self.cL[i][-1].close()
        return None

    def sendEvent(self):
        Event(level=self.level, obj_name = self.sig_name, event_name='NEW')
        return None

    def regSignal(self):
        kw = {'level_num':self.level, 'obj_name': self.sig_name, 'event_name':'NEW'}
        EventFactory.regSignal(**kw)
        return None

class PatternPair(object):
    # All pattern are based pair obj!!!!!
    m = Market()
    ML = []   #ChainPair.cL
    L = []  # pattern.L 需要注册到m,因为信号系统要用,分类型，不分层 ; 
    level = -1
    window_w = -1

    def __init__(self):   
        self.obj_list = [] 
        self.cursor = []
        self.chain_layer = -1
  
    def __str__(self):
        return '{0.__class__.__name__}({0.obj_list!s})'.format(self)
    
    @classmethod
    def updateAll(cls):
        for pt in cls.L:
            
            flag, cursors = pt.cursors()
            
            if flag:
                pt.obj_list = [pt.ML[c[0]][c[1]] for c in cursors]
                if pt.calChart():
                    pt.open_position()
            
            flag1, n_cursor = pt.nextSCursor()
            if flag1:
                
                flag2,n_cursors = pt.cursors([pt.chain_layer, n_cursor])
                
                if flag2:
                    pt.obj_list = [pt.ML[c[0]][c[1]] for c in n_cursors]
                    pt.cursor[1] = n_cursor
                    if pt.calChart():
                        pt.open_position()            
        return None
                
    def open_position(self):
        kw = {'drt': self.obj_list[0].drt, 'level': self.level, 'TmSig': self.m.dt[-1][4]
             ,'pattern_name':self.__class__.__name__, 'objs':self.obj_list
               , 'open_event':{'level_num':0, 'obj_name': 'Stick', 'event_name':'NEW'}
              , 'open_action': {'method':'open_position', 'param':'m.dt[-1]'}}
        Position(kw)
    
        return None
    
    def cursors(self, start_cursor=None, window_w=None):
        '''
        Front: start_cursor, window_w
        Return: flag, n_cursors
        '''
        if start_cursor is None:
            start_cursor = self.cursor
        
        if window_w is None:
            window_w = self.window_w
        print('test:PP.cursor()__start_cursor:{},layer_chain:{},w:{}'.\
            format(start_cursor,self.chain_layer, window_w))
        cursor_list = [start_cursor]
        flag = False
        while len(cursor_list) < (window_w):
            flag, n_chain_layer, n_cursor = self.nextCCursor(start_cursor[0], start_cursor[1])
            if flag:
                cursor_list.append([n_chain_layer,n_cursor])
            else:
                return flag, cursor_list
        
        return flag, cursor_list
                 
    
    def nextCCursor(self, chain_layer=None, cursor=None):
        '''
        To find next continuous cursor
       Front: self.chain_layer
       Input: cursor, chain_layer=None
        Output: flag, next_chain_layer, next_cursor
        '''
        if chain_layer is None:
            chain_layer = self.chain_layer
            cursor = self.cursor[1]
        
        if len(self.ML[chain_layer]) == 0:
            return False, None, None
        cur_pair = self.ML[chain_layer][cursor]
        
        n_chain_layer = chain_layer
        for pl in self.ML[chain_layer::-1]:
            n_cursor = len(self.ML[n_chain_layer]) -1
            for p in pl[::-1]:
                if p.isFollow(cur_pair):
                    flag = True
                    return flag, n_chain_layer, n_cursor
                n_cursor = n_cursor - 1
            n_chain_layer = n_chain_layer - 1
            
        return False,None, None
    
    def nextSCursor(self):
        '''
       To find next of self.cursor of same chain_layer
       Front: self.cursor
       Output: flag, n_cursor
       '''
        if self.cursor[1] < len(self.ML[self.chain_layer]) - 1:
            return True, self.cursor[1] + 1
        else:
            return False, None
                    
    @classmethod
    def changeL(cls,ll):
        cls.L = ll
        return None
    
    @classmethod
    def changeML(cls,pairchain):
        cls.ML = pairchain[0].cL
        return None
    
    @classmethod
    def changeW(cls, window_w):
        cls.window_w = window_w
    
    @classmethod
    def newPattern(cls, pair):
        new_pattern = cls.__new__(cls)
        cls.L.append(new_pattern)
        new_pattern.status = 0 # 0: no pattern ; 1: pattern formed; 
        
        new_pattern.obj_list = [pair]
        node = new_pattern.step_nodes[0]
        node(pair)
        return None 
    
    def regAction(self):
        obj_str = 'PairChainLv'+ str(self.level)
        
        kw = {'level_num':self.level, 'obj_name': obj_str, 'event_name':'NEW',
              'obj_p':self.__class__.__name__, 'method':'updateAll', 'param':''}
        EventFactory.regAction(**kw)
        return None
    
    def calChart(self):
        pass
    
    # =================== Pair Operator definition ======================
    def is_flag(self, fd):
        f1 = choose(fd, 'drt')
        f2 = choose(fd, 'c_drt')
        t1 = Mul(f1, f2)
        t2 = gt(t1, 3)
        f3 = choose(fd, 'c_c_level')
        t3 = le(f3, 0.5)
        return All([t2, t3])
        
    def real_move(self, fd0, fd1):
        t1 = eq(choose(fd1, 'drt'), Number(1))
        t2 = gt(choose(fd1, 'cl'), choose(fd0, 'ch'))
        move_posi = All([t1, t2])
        t3 = eq(choose(fd1, 'drt'), Number(-1))
        t4 = lt(choose(fd1, 'ch'), choose(fd0, 'cl'))
        move_neg = All([t3, t4])
        return Any([move_posi, move_neg])
    
    def is_enhance(self, fd0, fd1):
        t1 = gt(choose(fd1, 'a'), choose(fd0, 'a'))
        t2 = gt(choose(fd1, 'k'), choose(fd0, 'k'))
        return All([t1, t2])
        

 
#class Signal(object):

class Signal001(object):
    L = []
    m = Market()
    ef = EventFactory()
    type = '001'

    def __init__(self):
        self.L.append(self)
        self.status = 0
        self.L.append(self)

        self.TmS = 0
        self.TmE = None
        self.drt = 0
        self.LLayer = 0
        self.HP = 0
        self.HL_limit = 0
        self.regAction()
    
    def __repr__(self):
        discription = 'SIG001{0.LLayer!r}(TmS:{0.TmS!r}, {0.drt!r}, {0.HP!r}, {0.HL_limit!r})'.format(self)  
        return  discription


    @classmethod
    def is_new(cls):
        flag = 0

        if cls.not_prepared():
            print('Not Prepared!!!!')
            return flag 

        for i in list(range(cls.m.layer))[::-1]:
            if i == 0:
                #return flag
                break
            elif len(cls.m.findList('pairchain', i)[0].cL[0]) < 2:
                continue

            HL_limit = cls.m.findList('pairchain', i)[0].cL[0][-1].ccHL[2:]
            for j in list(range(i-1))[::-1]:
                HL_pair = [cls.m.findList('pairchain', j)[0].cL[0][-2].ccHL[2:]]
                HL_pair.append(cls.m.findList('pairchain', j)[0].cL[0][-1].ccHL[2:])

                #小级别Pair是否破大级别Pair的边界
                drt, con1 = cls.is_puncture(HL_limit, HL_pair)

                # 小级别Pair是否破线方向级进
                con2 = cls.is_step(HL_pair, drt)

                if con1*con2 != 0:
                    flag = 1
                    print('New SIG!!!')
                    new_dict = {'TmS': cls.m.TmIdx,
                    'drt': drt,
                    'LLayer': j,
                    'HP': cls.m.findList('pair', i)[-1]}
                    cls.newSignal(**new_dict)
                    print(HL_limit, HL_pair)
                        

        return flag
    
    @staticmethod
    def is_puncture(HL_limit, HL_pair):  # 穿刺
        flag = 0
        if max(HL_pair[0][0], HL_pair[1][0]) > max(HL_limit):
            drt = 1
            flag = 1
        elif min(HL_pair[0][1], HL_pair[1][1]) < min(HL_limit):
            drt, flag = -1,1
        else:
            drt = 0
        return drt, flag

    @staticmethod
    def is_step(HL_pair, drt):
        flag = 0
        if drt == 1 and HL_pair[0][0] < HL_pair[1][0]:
            flag = 1
        elif drt == -1 and HL_pair[0][1] > HL_pair[1][1]:
            flag = 1
        return flag

    @staticmethod
    def is_overlap(range01, range02):
        flag = 0
        if range01[0] < range02[1] or range01[0] > range02[0]:
            flag = 1
        return flag

    @classmethod
    def not_prepared(cls):
        ll = cls.m.findList('pairchain', cls.m.layer - 2)[0].cL[0]
        if len(ll) < 2:
            return True 
        return False

    @classmethod
    def updateAll(cls):
        cls.is_new()
        return None

    @classmethod
    def newSignal(cls, **kwargs): 
        new_signal = cls.__new__(cls)
        
        new_signal.TmS = kwargs['TmS']
        new_signal.TmE = None
        new_signal.drt = kwargs['drt']
        new_signal.LLayer = kwargs['LLayer']
        new_signal.HP = kwargs['HP']
        new_signal.status = 1
        new_signal.HL_limit = new_signal.HP.ccHL[2:]
        
        cls.L.append(new_signal)
        cls.sendSignal()
        return None

    @classmethod
    def sendSignal(cls):
        pass
        return None

    @classmethod
    def regAction(cls):
        signal_methods = []
        signal_methods.append({
            'level_num': 0,
            'obj_name': 'Stick',
            'event_name': 'NEW',
            'obj_p': 'm.PLv0_L[-1]',
            'method': 'distr',
            'param': ''
        })
        signal_methods.append({
            'level_num': 1,
            'obj_name': 'TrendLv1',
            'event_name': 'NEW',
            'obj_p': 'm.PLv1_L[-1]',
            'method': 'distr',
            'param': ''
        })
        signal_methods.append({
            'level_num': 2,
            'obj_name': 'TrendLv2',
            'event_name': 'NEW',
            'obj_p': 'm.PLv2_L[-1]',
            'method': 'distr',
            'param': ''
        })
        signal_methods.append({
            'level_num': 3,
            'obj_name': 'TrendLv3',
            'event_name': 'NEW',
            'obj_p': 'm.PLv3_L[-1]',
            'method': 'distr',
            'param': ''
        })
        signal_methods.append({
            'level_num': 0,
            'obj_name': 'Stick',
            'event_name': 'NEW',
            'obj_p': 'm.SIG_L[0]',
            'method': 'updateAll',
            'param': ''
        })
        for m in signal_methods:
            cls.ef.regAction(**m)
        return None

       