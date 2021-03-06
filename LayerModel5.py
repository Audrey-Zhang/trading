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
    L = []
    def __init__(self, time_index, value, drt):
        self.TmIdx, self.V, self.drt = time_index, value, drt
        self.L.append(self)
        
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
    obj_L = []
    def __init__(self, **kwargs):
        self.drt = kwargs['drt']
        if 'k_bar' in kwargs.keys():
            self.H, self.L, self.TmIdx = kwargs['k_bar'][1], kwargs['k_bar'][2], kwargs['k_bar'][4]
        if 'H' in kwargs.keys():
            self.H, self.L, self.TmIdx = kwargs['H'], kwargs['L'], kwargs['TmIdx']
        self.merged = 1
        # self.range = None  # for ES, trend_drt==1 ~ rangeL, trend_drt==-1 ~ rangeH
        self.obj_L.append(self)
    
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
    L = []
    m = {'1': ['L', 'H', 'H'], '-1':['H', 'L', 'L']}
    level = 0
    mm = Market()
    remark = []
    def __init__(self, method, **kwargs):
        self.L.append(self)
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
        return self.L[-1].update1Bar(k_bar)

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
    L = []
    level = -1
    ML = []
    m = Market()
    ef = EventFactory()
    def __init__(self, method, **kwargs):
        self.L.append(self)

        self.mp = kwargs['mp']
        self.remark = []

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
            self.regAction()

    def __repr__(self):
        return 'Trend{0.level}({0.drt!r}, {0.status!r}, {0.start!r})'.format(self)
    
    def __str__(self):
        return '({0.drt!s}, {0.start!s})'.format(self)

    def update2(self):
        flag = 0
        treated = self
                
        # Check ML to find new sticks   
        if len(self.ML) - self.mp[-1] > 1:
            new_mp = [i for i in range(self.mp[-1]+1, len(self.ML))]
        # iterate stick_stack to update Trend
        for i in new_mp:
            treated.stick_stack.append(treated.ML[i])
            treated.mp.append(i)
            #treated.updatePp(treated.stick_stack[-1])
            flag, treated = treated.update1Stick()
            
        self.sendEvent(flag)  
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
                #self.remark.append('Lv{0}.update1st:status={1},mp:{3},{2.start},{2.peak},{2.end},{2.ES_stack}'\
                #.format(self.level, self.status, self, len(self.mp)))
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
                            #.append('Lv{}.upd1st():case1, status:{}, mp:{},pp:{}'.\
                            #    format(self.level, self.status,self.mp, self.pp))
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
                            self.remark.append('Lv{}.upd1st():case1, status:{}, mp:{},pp:{}'.\
                                format(self.level, self.status,self.mp, self.pp))
                            self.status = 2
                            new_trend = self.produceNewTrend(1)
                            flag = 2
                            
                    elif (tmp_stdk['L'] >= self.ES_stack[-1].L and
                         tmp_stdk['H'] <= self.ES_stack[-1].H):
                        self.ES_stack[-1].H = tmp_stdk['H']
                        ## self.ES_stack[-1].merged += 1  # ！！！！
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

    @classmethod
    def regAction(cls): #初始化第1个对象时调用
        signal_methods = []
        signal_methods.append({
            'level_num': cls.level,
            'obj_name': cls.__name__,
            'event_name': 'NEW',
            'obj_p': 'm.CLv'+str(int(cls.level)-1)+'_L[0]',
            'method': 'newCenter',
            'param': 'obj="st", level=' + str(int(cls.level)) + ', i=-1'
        })
        for m in signal_methods:
            cls.ef.regAction(**m)
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
                    self.peak = stick.start
                    self.pp = self.stick_stack.index(stick)
                    flag = 1                

        return flag
    '''
    def updatePp(self, st=None, time_index=None, pp=None):   # Unused!!!
        if time_index is not None:
            self.pp = self.findIdxInSS(time_index)
        elif st is not None:
            if st.start == self.peak:
                self.pp = self.stick_stack.index(st)
        else:
            self.pp = pp
        return None
        '''

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
            #self.remark.append('Lv{}.produceNewTrend:case1, mp={}'.format(self.level,mp))
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
        
        
        new_trend = self.L[-1]
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

        cls.L.append(new_trend)
        new_trend.remark =[]

        new_trend.mp = kwargs['mp']
        new_trend.stick_stack = [new_trend.ML[i] for i in new_trend.mp]
            
        new_trend.drt = new_trend.stick_stack[0].drt
        new_trend.SS_stack = [StdK(**new_trend.stickToStdK(stick)) for stick in new_trend.stick_stack[::2]]
        
        new_trend.start = Point.getPoint('start', new_trend.stick_stack[0])
        new_trend.end = Point.getPoint('end', new_trend.stick_stack[-1])
        
        
        # from /
        if len(new_trend.stick_stack) == 2:
            new_trend.peak = new_trend.stick_stack[0].peak  
            new_trend.ES_stack = [StdK(**new_trend.stickToStdK(new_trend.stick_stack[1]))]   
            new_trend.pp = 1       
            
        #from /\, N
        else:
            if 'pp' in kwargs.keys():
                new_trend.pp = kwargs['pp']
                new_trend.peak = Point.getPoint('start', new_trend.stick_stack[new_trend.pp])
            else:
                new_trend.peak = new_trend.stick_stack[0].peak  
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

    '''
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
        '''
            
    
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
    '''
    @classmethod 
    def findBigStick(cls, pct_spc): 
        v1, v2 = cls.L[-2].start.V, cls.L[-1].start.V
        pct = (v2 - v1)*cls.L[-2].drt / v1
        self.remark.append('Trend{}: v1:{:.2f}, v2:{:.2f}, drt:{}, pct:{:.2%}'.format(
            cls.level, v1, v2, cls.L[-2].drt, pct))
        if pct > pct_spc:
            msg = {}
            Singal('BIGST', level=cls.level, msg = msg)
        return None
        '''

    # ============================ Evaluation Method =====================================
    def amp(self):

        amp_eq = [(st.peak.V - st.start.V)*st.drt for st in self.stick_stack 
        if (st.drt == self.drt and st.start.TmIdx < self.peak.TmIdx )]
        amp_op = [(st.peak.V - st.start.V)*st.drt for st in self.stick_stack 
        if (st.drt != self.drt and st.start.TmIdx < self.peak.TmIdx )]
        return sum(amp_eq), sum(amp_op)

class CenterStrict(object):
    m = Market()
    L = []
    ML = []
    level = -1
    openL =[]
    ef = EventFactory()
    def __init__(self, level=0, stS_idx=None):
        if stS_idx is None:  # 起点对象
            self.L.append(self)
            self.openL.append(self)
            self.is_main = 0
            self.st_idxL = [0]
            self.TmS, self.TmE = 0,0            
            self.L, self.H = 0,0
            self.remark = ['init-{}'.format(self.TmS)]

            self.regEvent()
            
        #else: 
        #    self.L.append(self)
        #    self.openL.append(self)
        #    # level 不修改， ML不修改

        #    self.is_main = 0
        #    self.st_idxL = list(range(stS_idx+1, len(self.ML)-1))
        #    st0 = self.ML[stS_idx+1]
        #    self.TmS = st0.start.TmIdx
        #    self.TmE = st0.peak.TmIdx
        #    self.L = min(st0.start.V, st0.peak.V)
        #    self.H = max(st0.start.V, st0.peak.V)
        #    self.remark = ['init_by_L-{}'.format(self.TmS)]

        #    self.update(self.st_idxL[1:])

    def __repr__(self):
        description ='Center{0.level}({0.TmS!r}, {1!r}, {0.H!r}, {0.L!r})'.format(self, len(self.st_idxL))
        return description

    @classmethod
    def updateAll(cls):
        for cc in cls.openL:
            flag = cc.update()
            if flag == 2:
                cls.openL.clear()
                cls.openL.append(cls.L[-1])
                break
        return None
    
    def update(self, new_st_idx_list=None): #链式更新
        flag = 0
        # 分析初始化初期，不更新center
        if self.too_early():
            return None
        
        # 待更新Stick List:
        if new_st_idx_list is None: # 把ML[-2]更新进去
            if len(self.st_idxL) == 1 and self.st_idxL[0] < len(self.ML) - 2:
                new_st_idx_list = list(range(self.st_idxL[0]+1, len(self.ML)-1))
            elif self.st_idxL[-1] < len(self.ML) - 2:
                new_st_idx_list = list(range(self.st_idxL[-1]+1, len(self.ML)-1))
            else:
                return None

        # 不检证kwards里的st_idxL的合理性了

        for st_idx in new_st_idx_list:
            flag = self.update1Stick(st_idx)
            if flag == 2:
                self.is_main += 10
                i = new_st_idx_list.index(st_idx)
                if i == 0:
                    st_L = [st_idx - 1] + new_st_idx_list
                else:
                    st_L = new_st_idx_list[i-1:]
                
                new_center ={'st_idxL': st_L, 'flag':flag}
                self.newCenter(**new_center)
                self.sendEvent(flag)
                break                   
        return flag

    def update1Stick(self, st_idx): # Return: flag  2:NEW10 0:else 
        flag = 0
        st = self.ML[st_idx]
        
        if self.out_st(st):
            self.st_idxL.pop()
            flag = 2
        else:
            self.st_idxL.append(st_idx)
            
            if len(self.st_idxL) == 2:
                self.L = min(st.start.V, st.peak.V)
                self.H = max(st.start.V, st.peak.V)
                self.TmS = st.start.TmIdx
                self.TmE = st.peak.TmIdx
            elif len(self.st_idxL) > 3:
                self.updHL(self.st_idxL[-2])
                self.TmE = self.ML[self.st_idxL[-1]].start.TmIdx
        return flag

    @classmethod
    def newCenter(cls, **kwargs): # RETURN：status =  1 或 链式更新close
        new_center = cls.__new__(cls)
        cls.L.append(new_center)              
        
        new_center.is_main = 0
        new_center.remark = []

        flag = 0  
        if 'obj' in kwargs:  
            # 高级别对象生成时NEW，指定视角,更新到ML[-2]
            # 高级别对象生成时NEW，加入到待更新
            cls.openL.append(new_center)

            obj_L = cls.m.findList(kwargs['obj'], kwargs['level'])
            obj = obj_L[kwargs['i']]
            if kwargs['obj'] == 'st':
                # obj is from Trend
                st_idxL = list(range(obj.mp[0], len(cls.ML)-1))
                flag = 2
            elif kwargs['obj'] == 'pair':
                # obj is from Pair_llv
                st_idxL = list(range(obj.index[0], len(cls.ML)-1))
                if len(st_idxL) == 0: #因为pair更新比较快，先用ML[-1]新建Center, upd()会等有新的ML[-2]时再更新center.
                    st_idxL = [obj.index[0]]
                flag = 3
        elif 'st_idxL' in kwargs:
            st_idxL = kwargs['st_idxL']
            new_center.is_main = 5
            flag = 1

        # 更新newCenter:
        if len(st_idxL) == 0:
            # sth strange!!!
            pass            
        elif len(st_idxL) == 1:
            new_center.st_idxL = st_idxL
            new_center.TmS, new_center.TmE = 0,0
            new_center.L, new_center.H = 0,0
        elif len(st_idxL) >= 2:
            new_center.st_idxL = st_idxL[:2]
            st1 = cls.ML[new_center.st_idxL[1]]
            new_center.TmS = st1.start.TmIdx
            new_center.TmE = st1.peak.TmIdx
            new_center.L = min(st1.start.V, st1.peak.V)
            new_center.H = max(st1.start.V, st1.peak.V)
            new_center.update(st_idxL[2:])  #从第3个st开始迭代更新
      
        
        return None

    def too_early(self):
        flag = False
        if len(self.ML) < 3:
            flag = True
        return flag

    def out_st(self, st):
        if len(self.st_idxL) < 2: # 即=1
            return False
        if st.start.V > self.H and st.peak.V > self.H:
            return True
        elif st.start.V < self.L and st.peak.V < self.L:
            return True
        else:
            return False

    def updHL(self, st_idx):
        st = self.ML[st_idx]
        self.H = max(self.H, st.start.V, st.peak.V)
        self.L = min(self.L, st.start.V, st.peak.V)
        return None

    def sendEvent(self, flag):
        event_list = ['','', 'NEW10', 'NEW']
        if event_list[flag] != '':
            Event(level=self.level, obj_name = self.__class__.__name__, event_name=event_list[flag])
        return None

    def regEvent(self):
        for f in ['NEW10']:
            dd = {'level_num': self.level,'obj_name': self.__class__.__name__, 'event_name': f }
            self.ef.regEvent(**dd)
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
        self.chain_layer = 0
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
    ef = EventFactory()
    def __init__(self, level, sig_name, st_idx_list=None):
        self.level = level
        self.sig_name = sig_name
        self.ML = self.m.findList('pair', level) 
        L = self.m.findList('pairchain', level) 
        L.append(self)
        self.cL = [[self.ML[0]], [], []]
        self.regEvent()
        self.regAction()
        

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
                   new_flag = 1 + i
                   self.cL[i].append(new_pair)

                elif self.cL[i][-1].status == 0:
                    if self.cL[i][-1].inside(st):
                        self.cL[i][-1].update(st_idx)
            
                    else: 
                        self.cL[i][-1].close()
                        new_pair.chain_layer = i
                        new_flag = 1 + i
                        self.cL[i].append(new_pair)
            elif  new_flag >= 1:
                if len(self.cL[i]) == 0 or self.cL[i][-1].status == 1:
                    break
                elif self.cL[i][-1].status == 0:
                    self.cL[i][-1].close()
        if new_flag == 0:
            new_pair.remove(new_pair)
        else:
            if new_flag > 2:
                new_flag = 2
            self.sendEvent(new_flag)
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

    def sendEvent(self, flag):
        event_list = ['', 'NEW', 'NEW_llv']
        if event_list[flag] != '':
            Event(level=self.level, obj_name = self.sig_name, event_name=event_list[flag])
        return None

    def regEvent(self):
        for f in ['NEW', 'NEW_llv']:
            dd = {'level_num': self.level,'obj_name': self.sig_name, 'event_name': f }
            self.ef.regEvent(**dd)
        return None

    def regAction(self): #初始化第1个对象时调用
        signal_methods = []
        signal_methods.append({
            'level_num': self.level,
            'obj_name': self.sig_name,
            'event_name': 'NEW_llv',
            'obj_p': 'm.CLv'+str(int(self.level))+'_L[0]',
            'method': 'newCenter',
            'param': 'obj="pair", level=' + str(int(self.level)) + ', i=-1'  
        })
        for m in signal_methods:
            self.ef.regAction(**m)
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
        #print('test:PP.cursor()__start_cursor:{},layer_chain:{},w:{}'.\
        #    format(start_cursor,self.chain_layer, window_w))
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
        #node = new_pattern.step_nodes[0]
        #node(pair)
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
    sig_name = '001'

    def __init__(self):
        self.L.append(self)
        self.status = 0
        self.L.append(self)

        self.TmS = 0
        self.TmE = None
        self.drt = 0
        self.HLayer = 0
        self.LLayer = 0
        self.HTmS = 0
        self.LTmS = 0
        self.regAction()
    
    def __repr__(self):
        if self.status == 0:
            discription = 'SIG001{0.HLayer!r}-{0.LLayer!r}(TmS:{0.TmS!r}, {0.drt!r}, {0.HTmS!r}, {0.LTmS!r})'.format(self)  
        else:
            discription = 'SIG001{0.HLayer!r}-{0.LLayer!r}(TmS:{0.TmS!r}, {0.drt!r}, {0.HTmS!r}, {0.LTmS!r}, {0.HL_limit})'.format(self) 
        return  discription


    def is_new(self):
        flag = 0

        if self.not_prepared():
            #print('Not Prepared!!!!')
            return flag 

        for i in list(range(self.m.layer))[::-1]:
            if i == 0:
                #return flag
                break
            elif len(self.m.findList('pairchain', i)[0].cL[0]) < 2:
                continue

            HL_limit = self.m.findList('pairchain', i)[0].cL[0][-1].ccHL[2:]
            # 是否在盘整
            HP = self.m.findList('pairchain', i)[0].cL[0][-1]
            LP_L = [p for p in self.m.findList('pairchain', i-1)[0].cL[0] if p.TmS >= HP.TmS]
            con0 = self.is_breather(HP, LP_L)
            if con0 != 1:
                continue
            else:
                self.L.append([self.m.TmIdx, HL_limit,HP])

            for j in list(range(i-1))[::-1]:
                HL_pair = [self.m.findList('pairchain', j)[0].cL[0][-2].ccHL[2:]]
                HL_pair.append(self.m.findList('pairchain', j)[0].cL[0][-1].ccHL[2:])

                LP_L = [p for p in self.m.findList('pairchain', j)[0].cL[0] if p.TmS >= HP.TmS]

                #小级别Pair是否破大级别Pair的边界
                drt, con1 = self.is_puncture(HL_limit, LP_L)

                # 小级别Pair是否破线方向级进
                con2 = self.is_step(HL_pair, drt)

                new_dict = {'TmS': self.m.TmIdx,
                    'drt': drt,
                    'HLayer': i,
                    'LLayer': j,
                    'HTmS': self.m.findList('pairchain', i)[0].cL[0][-1].TmS,
                    'LTmS': self.m.findList('pairchain', j)[0].cL[0][-1].TmS,
                    'HP': self.m.findList('pairchain', i)[0].cL[0][-1]}
                # sig pattern是否已存在
                con3 = self.not_exist(**new_dict)

                if con1*con2 != 0 and con3:
                    flag = 1
                    #print('New SIG!!!')                    
                    self.newSignal(**new_dict)
                    #print(con3)

                    

        return flag
    
    def is_breather(self, HP, LP_L): # 盘整
        HP_r = [HP.ccHL[3], HP.ccHL[2]]
        cons = 1
        flag = 0
        if len(LP_L)<3:
            return flag
        for p in LP_L:
            p_r = [p.ccHL[3], p.ccHL[2]]
            cons = cons*self.is_overlap(HP_r, p_r)

        if cons == 1:
            flag = 1

        return flag
    
    @staticmethod
    def is_puncture(HL_limit, LP_L):  # 穿刺
        flag = 0
        peak = LP_L[-1].P
        #print('是否穿刺：p:{0},HL:{1}'.format(peak,HL_limit))
        if peak > max(HL_limit):
            drt = 1
            flag = 1
        elif peak < min(HL_limit):
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
    def is_overlap(range01, range02, ratio = 0.34): # LH是否重叠 
        flag = 0
        if (range02[1] - range01[0])*(range01[1] - range02[0]) > 0:
            r = (range01[1] - range02[0]) / (range02[1] - range01[0])
            if r >= ratio:
                flag = 1
        return flag

    def not_exist(self, **kwargs):  #Signal pattern 去重
        con1 = self.HLayer == kwargs['HLayer']
        con2 = self.LLayer == kwargs['LLayer']
        con3 = self.HTmS == kwargs['HTmS']
        con4 = self.LTmS == kwargs['LTmS']
        if con1 and con2 and con3 and con4:
            return False
        return True

    @classmethod
    def not_prepared(cls):
        ll = cls.m.findList('pairchain', cls.m.layer - 2)[0].cL[0]
        if len(ll) < 2:
            return True 
        return False

    @classmethod
    def updateAll(cls):
        cls.L[0].is_new()
        return None

    @classmethod
    def newSignal(cls, **kwargs): 
        new_signal = cls.__new__(cls)
        
        new_signal.TmS = kwargs['TmS']
        new_signal.TmE = None
        new_signal.drt = kwargs['drt']
        new_signal.HLayer = kwargs['HLayer']
        new_signal.LLayer = kwargs['LLayer']
        new_signal.HTmS = kwargs['HTmS']
        new_signal.LTmS = kwargs['LTmS']
        new_signal.HP = kwargs['HP']
        new_signal.status = 1
        new_signal.HL_limit = new_signal.HP.ccHL[2:]
        new_signal.HP_cc = new_signal.HP.cc
        new_signal.HP_st_len = len(new_signal.HP.index)
        
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


class SIG_overlapMv(object):
    m = Market()
    ef = EventFactory()
    sig_name = 'overlap_mv'
    L =[]
    Fremark =[]
    
    def __init__(self):
        self.resetL()
        return None

    @classmethod
    def any_opp(cls, level): # Search Lv[level]'s tail
        stL = cls.m.findList('st', level)
        if stL[-3].pp > 1:
            pass
        elif stL[-3].start.TmIdx not in [s.lv_TmS for s in cls.L[-3:]]: #Trend[-3]还没有信号
            cls.any_opp2(stL[-3], level)
            #if not cls.almost_wiped(stL[-3]):
            #    cls.any_opp2(stL[-3], level)
        cls.any_opp2(stL[-2], level)
        #if not cls.almost_wiped(stL[-2]):
        #   cls.any_opp2(stL[-2], level)
        return None



    @classmethod
    def any_opp2(cls, st, level):
        new_signal = {'level': level-1, 'TmIdx': cls.m.TmIdx, 'drt': st.drt, 'sigV':cls.m.dt[-1][3], 'lv_TmS':st.start.TmIdx, 'st_idx': st.mp[0]}

        # is_overlap
        flag = 0
        
        if st.pp == 1:
            flag = 1
        elif st.pp in [3,5]:
            cnt_big = 0
            cnt_small = 0
            for st0 in st.stick_stack[:st.pp:2]:
                if (st0.start.V - st0.peak.V)/(st.start.V - st.peak.V) > 0.85:
                    cnt_big += 1
                elif  (st0.start.V - st0.peak.V)/(st.start.V - st.peak.V) < 0.2:
                    cnt_small += 1
            for st0 in st.stick_stack[1:st.pp:2]:
                if  (st0.peak.V - st0.start.V)/(st.start.V - st.peak.V) < 0.2:
                    cnt_small += 1
            if cnt_big == 1 and (cnt_big + cnt_small) == st.pp:
                flag = 2

        # is cross center
        if flag < 1:
            return False
        ll = cls.m.findList('center', level-1)
        centerL = []
        for cc in ll[::-1]:
            if cc.TmS < st.start.TmIdx <= cc.TmE:
                centerL.append(cc)

        if len(centerL) > 0:
            compare_center = centerL[-1]
        else:
            #.append('len(centerL)=0:st{}'.format(st.start.TmIdx))
            return False
    
        if len(compare_center.st_idxL) < 1 or st.mp[0] - compare_center.st_idxL[1] < 3:
            #cls.Fremark.append('cmp_center too young:st{}'.format(st.start.TmIdx))
            return False
        H, L = compare_center.H, compare_center.L
        h, l = max(st.start.V, st.peak.V), min(st.start.V, st.peak.V)
        if l > H or L > h:
            #cls.Fremark.append('Lv1 与center分离:st{}'.format(st.start.TmIdx))
            return False
        total = max(H, h) - min(L, l)
        not_overlap = abs(H - h) + abs(L - l)
        if not_overlap / total < 0.25:
            new_signal['flag'] = flag
            new_signal['remark'] = '{}Lv1{},{},{},{},{},{} '.format(st.drt, st.start.TmIdx, not_overlap, total, not_overlap / total,[H,L,h,l],compare_center.TmS)
            cls.newSig(**new_signal)
            return True
        #cls.Fremark.append('Lv1 not cross center:st{0},H:{1},L:{2},h:{3},l:{4},total:{5},not_overlap:{6}'.format(st.start.TmIdx,H,L,h,l,total,not_overlap))


        return False

    @classmethod
    def almost_wiped(cls, st):
        # if any coming ST0[:-1] wiped the st1
        st_half = (st.start.V + st.peak.V)/2
        threshold = st_half

        if (cls.m.dt[-1][3] - threshold) * st.drt < 0: 
            #cls.Fremark.append('st[{}] wiped: crt_k wipe st1 half'.format(st.start.TmIdx))
            return True

        st0_L = cls.m.findList('st', st.level - 1)[st.mp[st.pp]:]
        
        for st0 in st0_L:
            if (st0.start.V - threshold) * st.drt < 0  or (st0.peak.V - threshold) * st.drt < 0:
                #cls.Fremark.append('st[{}] wiped:st0{} wipe st1 half'.format(st.start.TmIdx, st0.start.TmIdx))
                return True

        #cls.Fremark.append('st[{},half{}] not wiped:st0L_start{}'.format(st.start.TmIdx, threshold, st0_L[0].start.TmIdx))
        return False
    
    @classmethod
    def newSig(cls, **kwargs):
        new_signal = cls.__new__(cls)
        cls.L.append(new_signal)

        new_signal.stockID = cls.m.stockID
        new_signal.level = kwargs['level']
        new_signal.TmInit = kwargs['TmIdx']
        new_signal.drt = kwargs['drt']
        new_signal.sigV = kwargs['sigV']
        new_signal.score = kwargs['flag']
        new_signal.remark = kwargs['remark']
        new_signal.lv_TmS = kwargs['lv_TmS']
        new_signal.st_idx = kwargs['st_idx']
       
    @classmethod
    def resetL(cls):
        cls.L = []


class SIG_overlap(object):
    m = Market()
    ef = EventFactory()
    sig_name = 'overlap'
    L =[]
    Fremark =[]
    
    def __init__(self):
        self.resetL()
        return None

    @classmethod
    def any_opp(cls, level): # Search Lv[level]'s tail
        stL = cls.m.findList('st', level)
        if len(stL) < 5:
            return None

        if stL[-3].pp > 1:
            pass
        elif stL[-3].start.TmIdx not in [s.lv_TmS for s in cls.L[-3:]]: #Trend[-3]还没有信号
            cls.any_opp2(stL[-3], level)
            #if not cls.almost_wiped(stL[-3]):
            #    cls.any_opp2(stL[-3], level)
        cls.any_opp2(stL[-2], level)
        #if not cls.almost_wiped(stL[-2]):
        #   cls.any_opp2(stL[-2], level)
        return None



    @classmethod
    def any_opp2(cls, st, level):
        new_signal = {'level': level-1, 'TmIdx': cls.m.TmIdx, 'drt': st.drt, 'sigV':cls.m.dt[-1][3], 'lv_TmS':st.start.TmIdx, 'st_idx': st.mp[0]}

        # is_overlap
        flag = 0
        
        if st.pp == 1:
            flag = 1
        elif st.pp in [3,5]:
            cnt_big = 0
            cnt_small = 0
            for st0 in st.stick_stack[:st.pp:2]:
                if (st0.start.V - st0.peak.V)/(st.start.V - st.peak.V) > 0.80:
                    cnt_big += 1
                elif  (st0.start.V - st0.peak.V)/(st.start.V - st.peak.V) < 0.25:
                    cnt_small += 1
            for st0 in st.stick_stack[1:st.pp:2]:
                if  (st0.peak.V - st0.start.V)/(st.start.V - st.peak.V) < 0.25:
                    cnt_small += 1
            if cnt_big == 1 and (cnt_big + cnt_small) == st.pp:
                flag = 2

        
        if flag > 0:
            new_signal['flag'] = flag
            new_signal['remark'] = '{}Lv{}_{}'.format(st.drt,st.level, st.start.TmIdx)
            cls.newSig(**new_signal)
            return True
        
        return False

    @classmethod
    def almost_wiped(cls, st):
        # if any coming ST0[:-1] wiped the st1
        st_half = (st.start.V + st.peak.V)/2
        threshold = st_half

        if (cls.m.dt[-1][3] - threshold) * st.drt < 0: 
            #cls.Fremark.append('st[{}] wiped: crt_k wipe st1 half'.format(st.start.TmIdx))
            return True

        st0_L = cls.m.findList('st', st.level - 1)[st.mp[st.pp]:]
        
        for st0 in st0_L:
            if (st0.start.V - threshold) * st.drt < 0  or (st0.peak.V - threshold) * st.drt < 0:
                #cls.Fremark.append('st[{}] wiped:st0{} wipe st1 half'.format(st.start.TmIdx, st0.start.TmIdx))
                return True

        #cls.Fremark.append('st[{},half{}] not wiped:st0L_start{}'.format(st.start.TmIdx, threshold, st0_L[0].start.TmIdx))
        return False
    
    @classmethod
    def newSig(cls, **kwargs):
        new_signal = cls.__new__(cls)
        cls.L.append(new_signal)

        new_signal.stockID = cls.m.stockID
        new_signal.level = kwargs['level']
        new_signal.TmInit = kwargs['TmIdx']
        new_signal.drt = kwargs['drt']
        new_signal.sigV = kwargs['sigV']
        new_signal.score = kwargs['flag']
        new_signal.remark = kwargs['remark']
        new_signal.lv_TmS = kwargs['lv_TmS']
        new_signal.st_idx = kwargs['st_idx']
       
    @classmethod
    def resetL(cls):
        cls.L = []
        cls.remark = []


class SIG_CCrawl(object):
    m = Market()
    ef = EventFactory()
    sig_name = 'CCrawl'
    L =[]
    remark =[]
    
    def __init__(self, levelL):
        self.level = -1
        self.drt = 0
        self.status = 0
        self.TmS = 0
        self.open_tm = 0
        self.center = ''
        self.TmIdx = 0
        self.ID = ''

        self.regAction(levelL)
        self.resetL()
        return None

    @classmethod
    def any_opp(cls, level):  # hook: Center_NEW10,  reg by running init
        for cc in cls.m.findList('center', level)[::-1]:
            if cc.is_main == 5:
                center_crt = cc
                break
        #cls.remark.append('plus{} any opp: cc_st_idx{}'.format(cls.m.findList('st', level)[center_crt.st_idxL[0]].start.TmIdx, center_crt.st_idxL))
        
        i = center_crt.st_idxL[0]
        if i < 5:
            return None
        st_plus = cls.m.findList('st', level)[i]
        st_A = abs(st_plus.start.V - st_plus.peak.V)
        #cls.remark.append('st_plus_idx:{}, st_A:{}'.format(i, st_A))

        stL_prev = cls.m.findList('st', level)[i-1:i-5:-1]
        H = max([st.peak.V for st in stL_prev])
        L = min([st.peak.V for st in stL_prev])
        stL_A = H - L
        
        con = st_A / stL_A
        #cls.remark.append('stL_prev:{}, stL_A:{}, pct:{}'.format(stL_prev, stL_A, con))


        if con < 2.5:
            # new SIG
            drt = cls.m.findList('st', level)[center_crt.st_idxL[0]].start.drt
            TmS = cls.m.findList('st', level)[center_crt.st_idxL[0]].peak.TmIdx
            new_signal = {'level': level, 'drt': drt, 'status':0, 'TmS':TmS, 'center': center_crt,'TmIdx': cls.m.TmIdx, 'ID':cls.m.stockID}
            cls.newSig(**new_signal)

        return None

    @classmethod
    def established(cls): # 暂时只链式更新最后一个  # .L跨品种需中断
        if len(cls.L) > 0:
            if cls.L[-1].ID == cls.m.stockID:
                cls.L[-1].established2()


    def established2(self): #hook: Trend_NEW  reg by @classmethod
        if self.status != 0:
            return None
        if len(self.center.st_idxL) < 4:
            return None
        flag, _settle_length, rr = self.m.st_settle(self.center.st_idxL[1:], self.level) 
        self.remark.append('ESTA:cc{}:{},{}'.format(self.TmS, self.center.st_idxL, rr))
        if flag == 1 and self.status == 0:
            self.open_tm = self.m.get_day(self.m.TmIdx)
            self.status = 1
        return None
    
    def following(self):

        return None

    @classmethod
    def newSig(cls, **kwargs):
        new_signal = cls.__new__(cls)
        cls.L.append(new_signal)

        new_signal.level = kwargs['level']
        new_signal.drt = kwargs['drt']
        new_signal.status = kwargs['status']
        new_signal.TmS = kwargs['TmS']
        new_signal.center = kwargs['center']
        new_signal.TmIdx = kwargs['TmIdx']
        new_signal.ID = kwargs['ID']
        new_signal.open_tm = 0

    @classmethod
    def regAction(cls, levelL):
        signal_methods = []
        for level in levelL:
            if level == 0:
                obj_name = 'Stick'
            else:
                obj_name = 'TrendLv' + str(int(level))
            
            signal_methods.append({
                'level_num': level,
                'obj_name': obj_name,
                'event_name': 'NEW',
                'obj_p': 'SIG_CCrawl',
                'method': 'established',
                'param': ''
            })

        for m in signal_methods:
            cls.ef.regAction(**m)
        return None


    @classmethod
    def resetL(cls):
        #cls.L = []
        cls.remark = []
