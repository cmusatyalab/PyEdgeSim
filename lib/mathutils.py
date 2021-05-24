import os
import sys
import re
from datetime import datetime
import pandas as pd
import numpy as np
import math
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt

import operator
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

from pyutils import *
from pdutils import *


def sigmoid(x):
    return (1 / (1 + np.exp(-x)))

def doublert(ser):
    ''' Calculate the doubling rate of a column '''
    y = ser.to_numpy().astype(float)

    # get the deltas to check if there was no increase
    # between two consecutive data points        
    dy = np.diff(y)

    # these are the places without increase
    idx = np.argwhere(dy) #could also be np.where(dy == 0.0)[0]

    y_fixed = y.copy()

    # create the x axis, probably days 
    x = np.arange(y.shape[0])

    # Hack: increase the second identical value be a
    # small amount so the interpolation works
    # increase the indices by one to increment the second value
    y_fixed[idx + 1] += 0.001

    # you need scipy > 0.17 for extrapolation to work
    f = interp1d(y_fixed, x, fill_value="extrapolate")

    # there are the values you need?
    y_half = y / 2.0

    # get the according x values by interpolation
    x_interp = f(y_half)

    # delta between the current day and the date when
    # the value was half
    dbl = x - x_interp

    # this already looks quite good, but double check!
    return dbl


''' Curve Fitting '''
def getLinearCurve(fdf, xcol, ycol, p0 = [1,1,1],ploton=False):
    xnarr = np.array(fdf[xcol])
    ynarr = np.array(fdf[ycol])
    xx = np.linspace(min(xnarr),max(xnarr),len(xnarr))
    fpopt,fpcov = curve_fit(fitLinear,xnarr,ynarr,p0=p0)
    yy = fitLinear(xx,*fpopt)
    if ploton:
        plt.plot(xnarr,ynarr,lw=1)
        plt.plot(xx,yy,lw=3)
    return pd.Series(yy),fpopt,fpcov

def getExponentialCurve(fdf, xcol, ycol, p0 = [1,1,1],ploton=False):
    xnarr = np.array(fdf[xcol])
    ynarr = np.array(fdf[ycol])
    xx = np.linspace(min(xnarr),max(xnarr),len(xnarr))
    fpopt,fpcov = curve_fit(fitExponential,xnarr,ynarr,p0=p0)
    yy = fitExponential(xx,*fpopt)
    if ploton:
        plt.scatter(xnarr,ynarr,c='blue')
        plt.plot(xx,yy,lw=3,c='orange')
    return pd.Series(yy),fpopt,fpcov

def getQuadraticCurve(fdf, xcol, ycol, p0 = [1,1,1],ploton=False):
    xnarr = np.array(fdf[xcol])
    ynarr = np.array(fdf[ycol])
#     xnarr,ynarr = lr_convertXY(fdf,[xcol],ycol)
    xx = np.linspace(min(xnarr),max(xnarr),len(xnarr))
    fpopt,fpcov = curve_fit(fitQuadratic,xnarr,ynarr,p0=p0)
    yy = fitQuadratic(xx,*fpopt)
    if ploton:
        plt.plot(xnarr,ynarr,lw=1)
        plt.plot(xx,yy,lw=3)
    return pd.Series(yy),fpopt,fpcov

def getCubicCurve(fdf, xcol, ycol, p0 = [1,1,1,1],ploton=False):
    xnarr = np.array(fdf[xcol])
    ynarr = np.array(fdf[ycol])
    xx = np.linspace(min(xnarr),max(xnarr),len(xnarr))
    fpopt,fpcov = curve_fit(fitCubic,xnarr,ynarr,p0=p0)
    yy = fitCubic(xx,*fpopt)
    if ploton:
        plt.plot(xnarr,ynarr,lw=1)
        plt.plot(xx,yy,lw=3)
    return pd.Series(yy),fpopt,fpcov

def fitLinear(x, a, b):
    return a*x + b

def fitExponential(x,a,b,c):
    return a*np.exp(b*x) + c

def fitQuadratic(x,a,b,c):    
    return (a*(x**2.0)) + (b*x) + c

def fitCubic(x,a,b,c,d):    
    return (a*(x**3.0)) + (b*(x**2.0)) + (c*x) + d

def estCurve(fdf, xcol, cc, type='linear'):
    retser = None
    if type=='linear':
        a = cc[0]
        b = cc[1]
        retser = fdf[xcol].map(lambda x: a * x + b)
    elif type=='exponential':
        a = cc[0]
        b = cc[1]
        c = cc[2]
        retser = fdf[xcol].map(lambda x: a*np.exp(b*x) + c)
    elif type=='geometric':
        a = cc[0]
        b = cc[1]
        c = cc[2]
        retser = fdf[xcol].map(lambda x: (a*(x**2.0)) + (b*x) + c)      
    elif type=='cubic':
        a = cc[0]
        b = cc[1]
        c = cc[2]
        d = cc[3]
        retser = fdf[xcol].map(lambda x: (a*(x**3.0)) + (b*(x**2.0)) + (c*x) + d)       
    return retser

''' Polynomial Regression'''
# These are not fully tested

def polyRegress(fdf,xcol,ycol,degree=2,predict=False,ploton=False,printy=False): # alias
    return lr_polyRegress(fdf,xcol,ycol,degree=degree,predict=predict,ploton=ploton,printy=printy)

def lr_polyRegress(fdf,xcol,ycol,degree=2,predict=False,ploton=False):
    model,polynomial_features,fdf2 = lr_polyMultiRegress(fdf,[xcol],ycol,degree=degree,predict=predict,ploton=ploton)
    return model,polynomial_features,fdf2

def lr_polyMultiRegress(fdf,xcolst,ycol,degree=2,predict=True,ploton=False,printy=False):
    x,y = lr_convertXY(fdf,xcolst,ycol)
    polynomial_features= PolynomialFeatures(degree=degree)
    x_poly = polynomial_features.fit_transform(x)
    model = LinearRegression()
    model.fit(x_poly,y)
    fdf2 = None
    if predict:
        fdf2 = lr_predictY(fdf,xcolst,ycol,model, polynomial_features)
        if ploton:
            lr_plot(x,y,fdf2['PREDICTED_Y'])
    return model,polynomial_features,fdf2

def lr_predictY(fdf,xcolst,ycol,model,polyfeat):
    x,y = lr_convertXY(fdf,xcolst,ycol)
    x_poly = polyfeat.fit_transform(x)
    y_poly_pred = model.predict(x_poly)
    rmse = np.sqrt(mean_squared_error(y,y_poly_pred))
    r2 = r2_score(y,y_poly_pred)
    print("RMSE=%f" % rmse)
    print("R-SQUARED=%f" % r2)
    tdf = pd.DataFrame({'ACTUAL_Y':y.flatten(),'PREDICTED_Y':y_poly_pred.flatten()})
    pdf = fdf.join(tdf)
    return pdf

def lr_convertXY(fdf,xcolst,ycol):
    x = fdf[xcolst].to_numpy()
    y = fdf[ycol].to_numpy()[:,np.newaxis]
    return x,y

def lr_splitTraining(fdf,test_size=0.2, shuffle=True, **kwargs):
    train, test = train_test_split(fdf, test_size=0.2, shuffle=True,**kwargs)
    return train,test

def lr_toDummy(fdf,collst,prefix=None):
    fdf1 = None
    if prefix is None:
        prefix = collst
    for col,pref in zip(collst,prefix):
        if fdf[col].dtype == 'bool':
            fdf[col] = fdf[col].map(lambda cell: 1 if cell else 0)
        fdf2 = pd.get_dummies(fdf[col],prefix=pref)
        if fdf1 is None:
            fdf1 = fdf2.copy()
        else:
            fdf1 = fdf1.join(fdf2)
    fdf = fdf.join(fdf1)
    return fdf

def lr_plot(x,y,y_poly_pred):
    plt.scatter(x, y, s=10)
    # sort the values of x before line plot
    sort_axis = operator.itemgetter(0)
    sorted_zip = sorted(zip(x,y_poly_pred), key=sort_axis)
    x, y_poly_pred = zip(*sorted_zip)
    plt.plot(x, y_poly_pred, color='m')
    plt.show()

import sklearn.metrics as metrics
import statsmodels.api as sm
def lr_r2(fdf,xcol,ycol):
    x,y = lr_convertXY(fdf,[xcol],ycol)
    r2=metrics.r2_score(x,y)
    return r2

def lr_printStats(fdf,ytruecol, ypredcol,model = None,OLS=True):
    # Regression metrics
    PRECISION = 4
    y_true,y_pred = lr_convertXY(fdf,[ytruecol],ypredcol)

    if model is not None:
        print("MODEL COEFFICIENTS: {}".format(model.coef_[0]))
        print("MODEL PARAMETERS: {} \nMODEL INTERCEPT: {}".format(model.get_params(),model.intercept_))    
    explained_variance=metrics.explained_variance_score(y_true, y_pred)
    mean_absolute_error=metrics.mean_absolute_error(y_true, y_pred) 
    mse=metrics.mean_squared_error(y_true, y_pred) 
    mean_squared_log_error=metrics.mean_squared_log_error(y_true, y_pred)
    median_absolute_error=metrics.median_absolute_error(y_true, y_pred)
    r2=metrics.r2_score(y_true, y_pred)

    print('Explained Variance: \t\t%f' % round(explained_variance,PRECISION))    
    print('Mean Squared Log Error (MSLE): \t%f' % round(mean_squared_log_error,PRECISION))
    print('R-squared: \t\t\t%f' % round(r2,4))
    print('Mean Absolute Error (MAE): \t%f' % round(mean_absolute_error,PRECISION))
    print('Mean Squared Error (MSE): \t%f' % round(mse,PRECISION))
    print('Root Mean Squared Error (RMSE): %f' % round(np.sqrt(mse),PRECISION))
    
    if OLS:
        y_true_adj = sm.add_constant(y_true.ravel())
        results = sm.OLS(y_pred,y_true_adj).fit()
        print(results.summary())  