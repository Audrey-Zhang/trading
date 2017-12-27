# -*- coding: utf-8 -*-
"""
Created on Mon Dec 04 19:31:28 2017

@author: zhangyun29
"""

import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import matplotlib.ticker as mtk
import numpy as np

def drawLvStd(ax,stdArr,vlcolor):
    dtCnt = len(stdArr)    
    xxx = range(0,dtCnt)
    ymin = []
    ymax = []
    for i in range(0,len(idxS)):
        ymin.append(float('nan'))
        ymax.append(float('nan'))
    for i in range(0,len(stdArr)):
        ymin[idxS.index(stdArr[i][2])] = stdArr[i][0]
        ymax[idxS.index(stdArr[i][2])] = stdArr[i][1]
    ax.vlines(xxx,ymin,ymax,color = vlcolor,lw = 5,alpha=0.75)
    

def x_fmt_func(x,pos=None):
    idx = np.clip(int(x+0.5),0, dtCnt-1)  
    print "x=", x
    return idxS[idx]

def candlestickz(ax,o,h,l,c):
    pass

def dwAxO(ax,os,hs,ls,cs):
    mpf.candlestick2_ochl(ax, os,hs,ls,cs, width=0.6, colorup='w', colordown = 'w', alpha=0.15)
    ax1.set_xlim(left = 0.0)    
    #tmp = ax.get_xlim()[0]
    #print tmp
    
def dwAxStd(ax,os,hs,ls,cs):
    mpf.candlestick2_ochl(ax, os,hs,ls,cs, width=0.6, colorup='r', colordown = 'g', alpha=0.75)
    ax1.set_xlim(left = 0.0)    
    #tmp = ax.get_xlim()[0]

'''
fig = plt.figure(figsize=(70,40))
ax = fig.gca(projection='3d')

# Make data.
X = np.arange(0, 20, 1)
Y = np.arange(0, len(distriD['count']), 1)
X, Y = np.meshgrid(X, Y)
z = np.array(distriD['count'])
region = np.s_[0:26,0:20]
X,Y,Z = X[region],Y[region],z[region]

# Plot the surface.
surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)

# Customize the z axis.
ax.set_zlim(-1.01, 2.21)
ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)