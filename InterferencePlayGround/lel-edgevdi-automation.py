#!/usr/bin/env python
import sys
import os
from datetime import datetime
import time
import json
from optparse import OptionParser

import client
import simlogging
from simlogging import mconsole

from pyutils import *
from AdvE_api_lib import AdvantEDGEApi
from AdvE_automation import AdvantEDGEAutomation

from setupAPIs import setupAPIs

cnf = {
    "APIIP":"127.0.0.1",
    "ADVANTEDGEVER":"1.8.0",
    "SCENARIO":"horizon-filter-1",
    "SANDBOX":"horizon-filter-1",
    "AUTOMATION":"horizontestlinux1",
    "FILEROOT":"Automation",
    "LATENCYDISTRIBUTION":"Normal"
}

stablizetime = 10
LOGNAME=__name__

def main():
    global logger
    LOGFILE="lel-edgevdi.log"
    logger = simlogging.configureLogging(LOGNAME=LOGNAME,LOGFILE=LOGFILE,loglev=logging.INFO, coloron=False)
    
    parser = OptionParser()
    parser.add_option("-p", "--profile", dest="testprofile", default = cnf['AUTOMATION'],
        help="TODO", metavar="STRING")
    parser.add_option("-f", "--profilefilename", dest="testprofilefn", default = None,
        help="TODO", metavar="STRING")
    parser.add_option("-t", "--test", dest="testlist",
        help="TODO", metavar="STRING")
    parser.add_option("-s", "--sandbox", dest="sandbox", default = cnf['SANDBOX'],
        help="TODO", metavar="STRING")
    parser.add_option("-S", "--scenario", dest="scenario", default = cnf['SCENARIO'],
        help="TODO", metavar="STRING")
    parser.add_option("-i", "--apiip", dest="apiip", default = cnf['APIIP'],
        help="TODO", metavar="STRING")
    parser.add_option("-V", "--apiversion", dest="apiversion", default = cnf['ADVANTEDGEVER'],
        help="TODO", metavar="STRING")
    parser.add_option("-R", "--fileroot", dest="fileroot", default = cnf['FILEROOT'],
        help="TODO", metavar="STRING")
    parser.add_option("-d", "--distribution", dest="distribution", default = cnf['LATENCYDISTRIBUTION'],
        help="TODO", metavar="STRING")    
    parser.add_option("-A", "--api-generate", action="store_true", dest="apiregen", default=False, 
        help="TODO")    
    parser.add_option("-P", "--ploton", action="store_true", dest="ploton", default=False, 
        help="TODO")
    parser.add_option("-g", "--generate", action="store_true", dest="generate", default=False, 
        help="TODO")
    parser.add_option("-z", "--zero", action="store_true", dest="zero", default=False, 
        help="Zero out the configuration at the beginning and end")    
    parser.add_option("-r", "--restart", action="store_true", dest="restart", default=False, 
        help="Restart the scenario at the beginning of the test")
 
    (options, args) = parser.parse_args()    
    kwargs = vars(options)

    if options.apiregen: 
        setupAPIs(**kwargs)
        mconsole("APIs are now configured. This program will exit so that the new API modules are reimported")
        mconsole("Please restart the application without the -A option")
        sys.exit(0)
    
    if options.generate: oscmd("python ./profile_manager.py")
    
    automaton = AdvantEDGEAutomation(**kwargs)
    
    if automaton.setupEnvironment(): automaton.runAutomationTest(runzero=kwargs['zero'])
    
    pass


        
''' Testing '''
        
        
if __name__ == '__main__': main()
        