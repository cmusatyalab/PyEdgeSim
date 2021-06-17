#!/usr/bin/env python3
import json
import os
import io
from tqdm import tqdm
import shlex, subprocess
import time, datetime
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from pandas.plotting import table
import geopandas as gp
from shapely.geometry import Point,LineString,Polygon
import contextily as ctx
from PIL import Image, ImageDraw


from pyutils import *
from gputils import *


defargs = {
    'figsize':(10,10),
    'fontsize':16,
    'saveon':False,
    'crs':{'init':'epsg:4326'},
    'markersize':3,
    'tabon':True,
    'tabfontsize':20,
    'tabscale':(1,2),
    'legendon':True,
    'yscale':1
}
deffont = {'fontweight':'ultralight','color':'blue','size':16,'fontfamily':'cursive','style':'normal'}
args = defargs

plt.rcParams.update({'font.size': args['fontsize']})

def save_plot(ax,fname):
    if args['saveon']:
        ax.get_figure().savefig(os.path.join(HOMEDIR,fname))

        
def ts_lineplot(fdf,ylst,title='',filename='tmp.png',saveon=False,figsize=(10,10),**kwargs):
    # print(title)
    ax = fdf.reset_index().plot(x='TIMESTAMP',y = ylst,title=title,figsize=figsize,**kwargs)
    ax.grid(True)
    if saveon:
        savePlot(ax,filename)
    return ax

def lineplot(tmpdf,xcol,ylst,title='',ax=None, filename='tmp.png', saveon=False,
             xlabel='',ylabel='', logx=False, logy=False,yscale=1,
             tabon=True,legend=True,figsize=(10,10), **kwargs):
    ''' PLot '''
    ymax = max(list(tmpdf[ylst].max()))
    ylim = ymax*yscale*1.1
    # print(ylim)
    ax = tmpdf.reset_index().plot(ax=ax,x=xcol,y=ylst,title=title,figsize=figsize,ylim=(0,ylim),
             logy=logy,logx=logx,legend=legend,**kwargs)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if tabon:
        tabcolWidths = [0.2 for col in range(0,len(ylst))]
        tab = table(ax,np.round(tmpdf[ylst].describe(),2),loc='upper center',colWidths=tabcolWidths)
        tab.set_fontsize(args['tabfontsize'])
        tab.scale(args['tabscale'][0],args['tabscale'][1])
    if saveon:
        save_plot(ax,filename)
    return ax

def scatterplot(fdf,xcol,ycol,ax = None,yscale=1.0,ymax=None, labelcol=None, fontsize=10,
                saveon=False, filename='tmp.png',
                title='',figsize=(10,10),**kwargs): # TODO Table and Legend and Log Scale
    if ax is None:
        ax = plt.figure(figsize=figsize).add_subplot(111)
    if ymax is None:
        ymax = fdf[ycol].max()
    ylim = (0,ymax*yscale*1.1)
    setTitle(ax,title)
    if labelcol is not None:
        plotLabels(fdf,xcol,ycol,labelcol=labelcol,ax=ax,fontsize=10)
    setAxesLabels(ax,xlabel=xcol,ylabel=ycol)
    setAxesScales(ax,yaxisdict={'ylim':ylim,'yscale':'linear'})
    plot_points(fdf,xcol,ycol,ax,**kwargs)
    if saveon:
        savePlot(ax,filename)
    return ax

def histplot(dfin,title='Unknown Title',ax=None,filename='tmp.png', 
    figsize=(10,10), xlabel='',ylabel='',tabon=True, saveon=False,
    bins=10, alpha=0.5, fontsize = 30, yticks = True,
    tabfontsize = 30, tabsizex = 1,tabsizey=2,**kwargs):
    
    font = {'size':fontsize}
    matplotlib.rc('font',**font)
    df = pd.DataFrame(dfin) # in case actually a series
    ''' Parameters '''
    bycol = kwargs['by'] if 'by' in kwargs else 'LAT'
    if ax is None:
        ax = plt.figure(figsize=figsize).add_subplot(111)
    ''' Plot '''
    ax = df.plot.hist(bins=bins,alpha=alpha,title=title,figsize=figsize,by=bycol,ax=ax,**kwargs)
    ax.set_xlabel(xlabel)
    if not yticks: ax.set_yticklabels([])
    print(tabon)
    if tabon:
        tabcolWidths = [0.2]
        tab = table(ax,np.round(df.describe(),2),loc='upper right',colWidths=tabcolWidths)
        tab.set_fontsize(tabfontsize)
        tab.scale(tabsizex,tabsizey)
    if saveon:
        print("Saving %s" % filename)
        savePlot(ax,filename)
    return ax


def getDefFont(): # Use if you want to change some of the options
    return gp_deffont
def setAxesLabels(ax,xlabel='',ylabel='',font = {'size':16}):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
def setTitle(ax,title,**kwargs):
    ax.set_title(title,**kwargs)

def setAxesScales(ax,xaxisdict={},yaxisdict={},option=None,**kwargs): # TODO x and y limits
    if not option is None:
        ax.axis(option)
    if 'xlim' in xaxisdict:
        ax.set(xlim=xaxisdict['xlim'])
    if 'ylim' in yaxisdict:
        ax.set(ylim=yaxisdict['ylim'])
    if 'xscale' in xaxisdict:
        ax.set_xscale(yaxisdict['yscale'])
    if 'yscale' in yaxisdict:
        ax.set_yscale(yaxisdict['yscale'])
        
def plot_points(ptdf,xcol,ycol,ax=None,s=50,figsize=(10,10),alpha=0.5,legendon=True,**kwargs):
    if ax is None:
        ax = plt.figure(figsize=figsize).add_subplot(111)
    ax.scatter(ptdf[xcol],ptdf[ycol],s=s,alpha=alpha,**kwargs)
    if legendon:
        ax.legend()
    return ax

    
def makeLabel(row,delimiter=', ',labelcol=[],**kwds): # Apply-Lambda
    retlab = ''
    for col in labelcol:
        colval = str(row[col])
        retlab += colval + delimiter
    retlab = retlab[:-2] # remove trailing delimiter and space
    return retlab

def plotLabel(row,xcol=None,ycol=None,ax=None,xoffset=0,yoffset=0,**kwds): # Apply-Lambda
    ax.text(row[xcol]+xoffset,row[ycol]+yoffset,row['label'],**kwds)

def plotLabels(fdf,xcol,ycol,labelcol=[],ax=None,mapon=False, 
                  figsize=(10,10),fontdict=gp_deffont,title=None,delimiter=", ",**kwargs):
    '''   GeoPandas DataFrame with 'geometry'containing Points '''
    if ax is None:
        ax = plt.figure(figsize=figsize).add_subplot(111)
    if len(labelcol) > 0:
        tlabgp = fdf[labelcol + [xcol,ycol]]
        tlabgp['label'] = tlabgp.apply(makeLabel,labelcol=labelcol,delimiter=delimiter,**kwargs,axis=1)
        tlabgp.apply(plotLabel,xcol=xcol,ycol=ycol,ax=ax,fontdict=fontdict,**kwargs,axis=1)
    if mapon:
        ctx.add_basemap(ax)
    return ax

def savePlot(ax,fn,**kwargs):
    ax.get_figure().savefig(fn,**kwargs)
    
''' Class to create gifs from axes '''
class Giffer():
    def __init__(self):
        self.imglst = []
    def addAX(self,ax):
        self.imglst.append(Giffer.ax2PIL(ax))

    def genGIF(self,fn,**kwargs):
        self.imlst2gif(fn,**kwargs)
        self.imglst = [] # Clean-up
    
    @staticmethod
    def ax2PIL(ax):
        buf = io.BytesIO()
        ax.get_figure().savefig(buf, format='png')
        buf.seek(0)
        im = Image.open(buf)
        return im
    
    def imlst2gif(self,fn,duration=1000,loop=0,optimize=False,save_all=True):
        images = []
        if len(self.imglst) > 0:
            print("Number of Axes: {}; Duration of each Axes: {}".format(len(self.imglst),duration))
            self.imglst[0].save(fn, append_images=self.imglst[1:], 
                           optimize=optimize, duration=duration, loop=loop, save_all=save_all)
        else:
            print("No Axes in Giffer list")


