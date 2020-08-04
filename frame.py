import json
import numpy as np

class Event(object):
    L = [[]*3]
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

    def __init__(self, f):
        self.read_config(f)
        
    def play(self, event):
        
        func_list =[]
        print(event)
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
    def regAction(cls, dd):
        # exception 
        ###

        actions = cls.event_config[dd['level_num']][dd['obj_name']][dd['event_name']]
        actions['obj_p'].append(dd['obj_p'])
        actions['method'].append(dd['method'])
        actions['param'].append(dd['param'])
        return None

    @classmethod
    def removeAction(cls, dd):
        actions = cls.event_config[dd['level_num']][dd['obj_name']][dd['event_name']]
        for i, obj in enumerate(actions['obj_p']):
            if obj == dd['obj_p']:
                if actions['method'][i] == dd['method']:
                    actions['obj_p'].pop(i)
                    actions['method'].pop(i)
                    actions['param'].pop(i)
                    break        
        return None

    @classmethod
    def regSignal(cls, dd):
        # exception: if signal has already existed
        if dd['level_num'] in list(range(len(cls.event_config))):
            cls.event_config[dd['level_num']][dd['obj_name']] = \
                {dd['event_name']:{'method': [], 'obj_p': [], 'param': []}}
        return None



    

class Singal(object):
    L = []
    new_L = []

    def __init__(self, signal_type, **kwargs):
        self.signal_type = signal_type
        self.level = kwargs['level']
        if 'msg' in kwargs.keys():
            self.msg = kwargs['msg']
        self.new_L.append(self)

    @classmethod
    def updateTm(cls, time):
        for new_signal in cls.new_L:
            new_signal.Tm = time
            cls.new_L.remove(new_signal)
            cls.L.append(new_signal)
        return None

class Market(object):
    dt = []
    def __init__(self, level_cnt=4):
        self.layer = level_cnt
        self.TmIdx = 0
        obj_name_list = ['Lv', 'PLv', 'PCLv', 'MPLv','PT01Lv']
        obj_name = ['st', 'pair', 'pairchain', 'mergedpair', 'pattern01']
        self.obj_list = {k:[[] for i in list(range(self.layer+1))] for k in obj_name}
        for i in range(level_cnt):
            for j, obj in enumerate(obj_name_list):
                exec('self.' + obj+str(i)+'_L = []') 
                exec('self.obj_list[obj_name['+str(j)+']]['+str(i)+'] = self.' + obj+str(i)+'_L')
        self.SIG_L = []
        self.CenterStrict_LD = {}
        self.position = []

        self.bin_cnt = 20
        

    def update(self, data_k):
        self.dt.append(data_k)
        self.TmIdx = data_k[4]

    def findList(self, name, level):
        return self.obj_list[name][level]

    # ======================= Private ==============================================
    

    # ===================== Global calculation method ==============================
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
        EventFactory.regAction(d)
        # 注册信号，用来更新limit_check(), stop_check()
        #d = {'level_num':kw['level'], 'obj_name': kw['limit_obj_name'], 'event_name':kw['limit_event_name'],
        #     'obj_p':'m.position['+i+']', 'method':'checkt_event', 'param':''}
        #EventFactory.reg_event(d)
        
        # setup limit_check() stop_check()
    
    def open_position(self, k):
        self.TmOp = k[4]
        self.openV = k[3]
        d ={**self.open_event, **self.open_action}
        EventFactory.removeAction(d)
        
        
        return None
