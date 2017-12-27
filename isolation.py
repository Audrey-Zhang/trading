# -*- coding: utf-8 -*-
def T_count(strTm1,strTm2,dfA):
    tmp = list(dfA['Tm'])
    dif = tmp.index(strTm2) - tmp.index(strTm1)
    return dif