#!/usr/bin/env python

import os
import sys
import filecmp
import subprocess
import shutil
import platform
import datetime
import requests
from pyutils import  *

from types import SimpleNamespace  

baseURL = None
# cnf = {'HOST': '127.0.0.1', 'PORT': 5002}

def main(): # For testing -- job_execute called by GUI
    # testurl = "https://www.google.com"
    # resp = requests.get(testurl)
    interference = False
    lbo = False
    zero = True
    NLTE = False
    N5G = False
    RANDOM = False
    kwargs = locals()
    # kwargs['cnf'] = cnf
    job_execute(kwargs)
    pass

def job_execute(kwargs):
    global baseURL
    global win
    k = SimpleNamespace(**kwargs)
    baseURL = getBaseURL(k)
    win = k.win
    profile = None
    try:
        if k.zero:
            resp = runZero(k)
        elif k.N5G:
            resp = run5G(k)
        elif k.NLTE:
            resp = runLTE(k)
        elif k.RANDOM:
            resp = runRandom(k)
        elif k.PROFILE:
            resp = runProfile(k)
        elif k.APIGEN:
            resp = runAPIGen(k)
        else:
            console("No key provided")
    except Exception as e:
        console(f"Bad variable: {e}")
    return

def runZero(k):
    req = baseURL + "zero"
    req = wrapURL(req,k)
    # resp = oscmd(f"curl {req}")
    resp = requests.get(req)
    return resp

def run5G(k):
    req = baseURL + "5g"
    req = wrapURL(req,k)
    resp = requests.get(req)
    return resp

def runLTE(k):
    req = baseURL + "lte"
    req = wrapURL(req,k)
    resp = requests.get(req)
    return resp

def runRandom(k):
    req = baseURL + "random"
    req = wrapURL(req,k)
    resp = requests.get(req)
    return resp

def runProfile(k):
    if(k.profile == "NA"):
        console("No profile specified")
        return None
    req = baseURL + "profile"
    req = wrapURL(req,k)
    resp = requests.get(req)
    return resp

def runAPIGen(k):
    req = baseURL + "apigen"
    req = wrapURL(req,k)
    resp = requests.get(req)
    return resp

def console(msg):
    print(msg)
    if win is not None:
        win.dbgwidg.write(str(msg + "\n"))
        win.statusbar.showMessage(msg)
        
def getBaseURL(k):
    return f"http://{k.cnf['HOST']}:{k.cnf['PORT']}/api?"

def wrapURL(req,k):
    if k.interference: req += "&interference"
    if k.lbo: req += "&lbo"
    req += f"&sandbox={k.sandbox}&scenario={k.scenario}&profilefn={k.profile}"
    return req
        
if __name__ == '__main__': main()

