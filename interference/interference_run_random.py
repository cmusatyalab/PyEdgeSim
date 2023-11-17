#!/usr/bin/env python
import sys
import os
from datetime import datetime
import time
import json
from optparse import OptionParser
import random

import client
import simlogging
from simlogging import mconsole

from pyutils import *
from AdvantEDGEApi import AdvantEDGEApi
from AdvantEDGEAutomation import AdvantEDGEAutomation

# from setupAPIs import setupAPIs

cnf = {
    "apiip":"127.0.0.1",
    "apiversion":"1.9.2",
    "advantedgever":"1.9.2",
    "SCENARIO":"horizon-filter-1",
    "SANDBOX":"horizon-filter-1",
    "profile":"horizontestlinux1",
    "fileroot":"Automation",
    "distribution":"Normal",
    "testerid":'jblake1',
    "cloudletip":'127.0.0.1',
    "influxon":False,
    "influxport":'30086',
    "influxdbname":"edgevdi",
    "influxmeasurement":"advantedge",
}

INTDIR = "../interference_profiles"
zerofn = os.path.join(INTDIR,"zero.json")

stablizetime = 10
numscen = 20

LOGNAME=__name__

def main():
    global logger
    LOGFILE="interference_run.log"
    logger = simlogging.configureLogging(LOGNAME=LOGNAME,LOGFILE=LOGFILE,loglev = logging.INFO,coloron=False)
    
    parser = OptionParser()
    ''' Startup options '''
    parser.add_option("-g", "--generate", action="store_true", dest="generate", default=False, 
        help="Generate fresh profiles before running")    
    parser.add_option("-r", "--restart", action="store_true", dest="restart", default=False, 
        help="Restart the AdvantEDGE scenario before running profiles")
    parser.add_option("-A", "--api-generate", action="store_true", dest="apiregen", default=False, 
        help="Regenerate API client bindings and exit")
    parser.add_option("-z", "--zero-between", action="store_true", dest="zerobetween", default=False, 
        help="Run the zero profile between other profiles (TODO)")    

    
    ''' Profile selection options '''
    parser.add_option("-f", "--profilefilename", dest="testprofilefn", default = None,
        help="Specify a specific interference profile to run", metavar="<filename>")
    parser.add_option("-N", "--normal", action="store_true", dest="normal", default=False, 
        help="Run only normal profiles")
    parser.add_option("-L", "--load", action="store_true", dest="load", default=False, 
        help="Run only loaded profiles")
    parser.add_option("-C", "--combo", action="store_true", dest="combo", default=False, 
        help="Run only combination profiles")
    parser.add_option("-B", "--badsignal", action="store_true", dest="badsignal", default=False, 
        help="Run only bad signal profiles")
    parser.add_option("-Z", "--zero", action="store_true", dest="zero", default=False, 
        help="Run the zero profile")

    ''' Change default parameters '''
    parser.add_option("-T", "--testerid", dest="testerid", default = cnf['testerid'],
        help="Give testerid".format(cnf['testerid']), metavar="STRING")    
    parser.add_option("-s", "--sandbox", dest="SANDBOX", default = cnf['SANDBOX'],
        help="Give the sandbox name (DEFAULT = {})".format(cnf['SANDBOX']), metavar="STRING")
    parser.add_option("-S", "--scenario", dest="SCENARIO", default = cnf['SCENARIO'],
        help="Give the scenario name (DEFAULT = {})".format(cnf['SCENARIO']), metavar="STRING")
    parser.add_option("-i", "--apiip", dest="apiip", default = cnf['apiip'],
        help="Give the IP for the api server (DEFAULT = {})".format(cnf['apiip']), metavar="STRING")
    parser.add_option("-V", "--advantedgever", dest="advantedgever", default = cnf['advantedgever'],
        help="Give the AdvantEDGE Version (DEFAULT = {})".format(cnf['advantedgever']), metavar="STRING")    
    parser.add_option("-p", "--profile", dest="testprofile", default = cnf['profile'],
        help="NOT TESTED", metavar="STRING")
    parser.add_option("-t", "--test", dest="testlist",
        help="NOT TESTED", metavar="STRING")
    parser.add_option("-R", "--fileroot", dest="fileroot", default = cnf['fileroot'],
        help="TODO", metavar="STRING")
    parser.add_option("-d", "--distribution", dest="distribution", default = cnf['distribution'],
        help="Set distribution for latency", metavar="<Normal, Pareto, Paretonormal, Uniform>")

    (options, _) = parser.parse_args()
    kwargs = cnf.copy()
    kwargs.update(vars(options))

    if kwargs['apiregen']: 
        # setupAPIs(**kwargs)
        mconsole("APIs are now configured. This program will exit so that the new API modules are reimported")
        mconsole("Please restart the application without the -A option")
        sys.exit(0)

    if kwargs['generate']: oscmd("python ./interference_generator.py")
        
    scenlst = [os.path.join(INTDIR,fn) for fn in os.listdir(INTDIR) if fn.startswith("N")]
    
    if kwargs['testprofilefn'] is not None:
        scenlst = [kwargs['testprofilefn']]
    elif kwargs['combo']:
        scenlst = [scen for scen in scenlst if 'Combo' in scen]
    elif kwargs['badsignal']:
        scenlst = [scen for scen in scenlst if 'BadSignal' in scen]
    elif kwargs['load']:
        scenlst = [scen for scen in scenlst if 'Load' in scen]
    elif kwargs['normal']:
        scenlst = [scen for scen in scenlst if 'Load' not in  scen and 'BadSignal' not in scen and 'Combo' not in scen]
    

    
    if not kwargs['zero']: 
        for ii in range(0,numscen):
            kwargs['testprofilefn'] = scenlst[random.randrange(len(scenlst))]
            automaton = AdvantEDGEAutomation(**kwargs)
            if automaton.setupEnvironment(): automaton.runAutomationTest(runzero=kwargs['zerobetween'])
    
    kwargs['testprofilefn'] = zerofn
    automaton = AdvantEDGEAutomation(**kwargs)
    if automaton.setupEnvironment(): automaton.runAutomationTest(runzero=False)

    
        
        
if __name__ == '__main__': main()