import json
import numpy as np

class Event(object):
    L = [[]*3]
    remark = []
    def __init__(self, **kwargs):
        # essential param
        
        self.level_num = kwargs['level']
        self.level = str(kwargs['level'])
        self.obj_name = kwargs['obj_name']
        self.event_name = kwargs['event_name']

        self.L[self.level_num].append(self)

    def __str__(self):
        return '({0.level!s}, {0.obj_name!s}, {0.event_name!s})'.format(self)
    
    def remove_event(self):
        self.L[self.level_num].remove(self)
        return None

    @classmethod
    def setEventL(cls, layer):
        cls.L = [[]*layer]
        return None

class EventFactory(object):
    # config will from JSON
    event_config ={'NEWLV': ['self.updateHLv()', 'self.findBigStick()'],
    'LVUPD': ['self.updateLvBybar()']}

    def __init__(self, f=None):
        if f is not None:
            self.read_config(f)
        
    def play(self, event):
        
        func_list =[]
        #print(event)
        objs = self.event_config[event.level_num][event.obj_name][event.event_name]['obj_p']
        methods = self.event_config[event.level_num][event.obj_name][event.event_name]['method']
        params = self.event_config[event.level_num][event.obj_name][event.event_name]['param']
        for obj,m,p in zip(*[objs,methods,params]):
            func_str = '{}.{}({})'.format(obj,m,p)
            if obj + m + p == '':
                func_str = ''
            func_list.append(func_str)

            
        event.remove_event()
        return func_list

    @classmethod
    def read_config(cls, filepath):
        cls.event_config = dict()         
        with open(filepath, mode='r', encoding='utf-8') as f:             
            cls.event_config = json.load(f)
            
    @classmethod
    def regAction(cls,  **kwargs):
        ###

        actions = cls.event_config[kwargs['level_num']][kwargs['obj_name']][kwargs['event_name']]
        actions['obj_p'].append(kwargs['obj_p'])
        actions['method'].append(kwargs['method'])
        actions['param'].append(kwargs['param'])
        return None

    @classmethod
    def removeAction(cls, **kwargs):
        actions = cls.event_config[kwargs['level_num']][kwargs['obj_name']][kwargs['event_name']]
        for i, obj in enumerate(actions['obj_p']):
            if obj == kwargs['obj_p']:
                if actions['method'][i] == kwargs['method']:
                    actions['obj_p'].pop(i)
                    actions['method'].pop(i)
                    actions['param'].pop(i)
                    break        
        return None

    @classmethod
    def regEvent(cls, **kwargs):
        # exception: if signal has already existed
        if kwargs['level_num'] in list(range(len(cls.event_config))):
            if kwargs['obj_name'] in cls.event_config[kwargs['level_num']]:
                cls.event_config[kwargs['level_num']][kwargs['obj_name']][kwargs['event_name']] = \
                {'method': [], 'obj_p': [], 'param': []}
            else:
                cls.event_config[kwargs['level_num']][kwargs['obj_name']] = \
                {kwargs['event_name']:{'method': [], 'obj_p': [], 'param': []}}

        return None

class Singal(object):
    L = []
    new_L = []

    def __init__(self, signal_type, **kwargs):
        self.signal_type = signal_type
        self.level = kwargs['level']
        if 'msg' in kwargs.keys():
            self.msg = kwargs['msg']
        self.new_L.append(self) #要

    @classmethod
    def updateTm(cls, time):
        for new_signal in cls.new_L:
            new_signal.Tm = time
            cls.new_L.remove(new_signal)
            cls.L.append(new_signal)
        return None

class Market(object):
    dt = []
    remark = []
    def __init__(self, stockID='', level_cnt=4):
        self.stockID = stockID
        self.layer = level_cnt
        self.TmIdx = 0
        obj_name_list = ['Lv', 'PLv', 'PCLv', 'MPLv','PT01Lv','CLv']
        obj_name = ['st', 'pair', 'pairchain', 'mergedpair', 'pattern01', 'center']
        self.obj_list = {k:[[] for i in list(range(self.layer+1))] for k in obj_name}
        for i in range(level_cnt):
            for j, obj in enumerate(obj_name_list):
                exec('self.' + obj+str(i)+'_L = []') 
                exec('self.obj_list[obj_name['+str(j)+']]['+str(i)+'] = self.' + obj+str(i)+'_L')
        self.SIG_L = []
        #self.CenterStrict_LD = {}
        self.position = []

        self.bin_cnt = 20

        self.clear()        

    def update(self, data_k):
        self.dt.append(data_k)
        self.TmIdx = data_k[4]

    def findList(self, name, level):
        return self.obj_list[name][level]

    def get_day(self, TmIdx):
        tm =self.dt[TmIdx][5]
        day =tm.strftime('%Y-%m-%d')
        return day

    @classmethod
    def clear(cls):
        cls.remark.clear()
        cls.dt.clear()
    
    # ===================== Global calculation method ==============================
    # st_settle: Input: st_idxL;  Ouput: 从起始点开始是否settle, settle_length
    # ccHL
    # ==============================================================================

    def st_settle(self, st_idxL, st_level): 
        remark = []
        if len(st_idxL) < 3:
            remark.append('center.stL < 3')
            return 0,0,''

        ss, flag, settle_length = 0, 0, 0        

        ml = self.findList('st', st_level)
        stL = [ml[i] for i in st_idxL]
        

            
        for i,st in enumerate(stL):
            j = max(3, i+1)
            H = max([st.start.V for st in stL[:j]])
            L = min([st.start.V for st in stL[:j]])
            st_pct = abs(st.start.V - st.peak.V) / (H - L)
            ss += st_pct
            if ss / (i+1) > 1:
                remark.append('Error: start or peak of st is wrong, so the pct > 1')
            if ss / (i+1) > 0.6:                
                settle_length = i + 1
            elif i + 1 > 7:
                break
            else:
                remark.append('pct<thread:{},{},{},{},{},{}'.format(len(stL), ss, i+1, H-L, st_pct, ss / (i+1)))
                break
        if settle_length >= 3:
            flag = 1
        return flag, settle_length, remark

    
    def ccHL(self, his, spec = 0.7):
        scale = his[0]
        distr = his[1]
        core = distr.argmax()

        L, H = core, core
        all_time = distr.sum()
        ss = distr[core]
        while (ss/all_time < spec):
            # get 2 sides:
            if L > 0:
                L = L - 1
                L_value = distr[L]
            else:
                L_value = 0
            if H+1 < self.bin_cnt:
                H = H + 1
                H_value = distr[H]
            else:
                H_value = 0

            if L_value >= H_value:
                ss = ss + L_value
                if ss/all_time > spec:
                    H = H - 1
                    break
                else:
                    ss = ss + H_value
            else:
                ss = ss + H_value
                if ss/all_time > spec:
                    L = L + 1
                    break
                else:
                    ss = ss + L_value
        return L, H, scale[L], scale[H]

class Position(object):
    m = Market() 
    L = []
    
    def __init__(self, kw):
        # kw = {'drt': self.obj_list[0].drt, 'level': self.level, 'TmSig': m.dt[-1][4]
        #     ,'pattern_name':self.__class__.__name__, 'objs':self.obj_list
        #       , 'open_event':{'level_num':self.level=>>0！！！, 'obj_name': 'Stick', 'event_name':'NEW'}
        #      , 'open_action': {'method':'open_position', 'param':'m.dt[-1]'}}
        self.drt = kw['drt']
        self.TmSig = kw['TmSig']
        self.pattern = kw['pattern_name']
        self.pattern_objs = kw['objs']
        self.open_action = kw['open_action']
        self.open_event = {'level_num':0, 'obj_name': 'Stick', 'event_name':'NEW'}
        # 判断open_position frozen range
        
        self.L.append(self)
        # 注册信号，收到信号后open(k), 即： Tm V 
        i = str(len(self.L) - 1)
        self.open_action['obj_p'] = 'm.position['+i+']'
        d = {**self.open_event, **self.open_action}
        EventFactory.regAction(**d)
        # 注册信号，用来更新limit_check(), stop_check()
        #d = {'level_num':kw['level'], 'obj_name': kw['limit_obj_name'], 'event_name':kw['limit_event_name'],
        #     'obj_p':'m.position['+i+']', 'method':'checkt_event', 'param':''}
        #EventFactory.reg_event(d)
        
        # setup limit_check() stop_check()
    
    def open_position(self, k):
        self.TmOp = k[4]
        self.openV = k[3]
        d ={**self.open_event, **self.open_action}
        EventFactory.removeAction(**d)
        
        
        return None
