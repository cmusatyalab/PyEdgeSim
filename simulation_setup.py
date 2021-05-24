#!/usr/bin/env python
import os
import sys
sys.path.append("./lib")
# import platform
from optparse import OptionParser
import shutil
from simlogging import *

from config import *
from pyutils import *

from setupRunTime import *
from setupBuildEnv import *
from setupAutomation import *
from setupDataManagement import *
from setupDeployment import *
from testAutomation import *
from createReport import *

cnf = initConfig()
LOGNAME=__name__

def main():
    global logger
    LOGFILE="simulation_setup.log"
    logger = configureLogging(LOGNAME=LOGNAME,LOGFILE=LOGFILE,coloron=False)
    try:
        mconsole("Starting {}".format(__file__))
        batch_console(batchfile="welcome.txt")
        (options,args) = cmdOptions(cnf)
        kwargs = options.__dict__.copy()
        retcode = job_execute(kwargs)
        if retcode == 0:
            mconsole("Successfully completed {} with code {}".format(__file__,retcode))
        else: 
            mconsole("Failed completion of {} with code {}".format(__file__,retcode),level="ERROR")
    except KeyboardInterrupt:
        sys.exit(0)

def cmdOptions(tmpcnf):
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-d", "--debug",
                  action="store_true", dest="debug", default=False,
                  help="Debugging mode")
    return  parser.parse_args()

def job_execute(kwargs):
    cnf.update(kwargs)
    ''' Set up runtime environment (CPU Only) '''
    entry = input("Do you want to setup runtime environment? [y/N] ") or "n"
    if entry in ['Y','y']:
        if setupDockerDaemon(cnf) == -1:
            mconsole("You need to reboot",level = "ERROR")
            entry = input()
            return -99
        if setupKubernetes(cnf) != 0: return -1
        if setupHelm(cnf) != 0: return -2
        if installAdvantEDGE(cnf) != 0: return -3
    ''' Set up build environment (CPU Only) '''
    entry = input("Do you want to setup build environment? [y/N] ") or "n"
    if entry in ['Y','y']:
        if installGO(cnf) != 0: return -4
        if installNodeJS(cnf) != 0: return -5
        if installESLint(cnf) != 0: return -6
        if installGolangCILint(cnf) != 0: return -7
        if installMeepCTL(cnf) != 0: return -8
        if buildMeepAll(cnf) != 0: return -9
    ''' Deploy AdvantEDGE '''
    entry = input("Do you want to deploy AdvantEDGE? [y/N] ") or "n"
    if entry in ['Y','y']:
        if deployAdvantEDGE(cnf) != 0: return -10
    entry = input("Do you want to setup data management? [y/N] ") or "n"
    if entry in ['Y','y']:        
        if setupInfluxDB(cnf) != 0: return -11
        if setupGrafana(cnf) != 0: return -12
    entry = input("Do you want to get OpenRTiST? [y/N] ") or "n"
    if entry in ['Y','y']:
        if getOpenRTiST(cnf) != 0: return -13 
    entry = input("Do you want to deploy the scenario? [y/N] ") or "n"
    if entry in ['Y','y']:        
        if startOpenRTiST(cnf) != 0: return -14
    entry = input("Do you want to setup automation? [y/N] ") or "n"
    if entry in ['Y','y']:        
        if setupAutomation(cnf) != 0: return -15
    entry = input("Do you want to run the test automation? [y/N] ") or "n"
    if entry in ['Y','y']:
        if runAutomationTest(cnf) != 0: return -16
    entry = input("Do you want to create the test report? [y/N] ") or "n"        
    if entry in ['Y','y']:
        if createReport(cnf,filename="report.png") != 0: return -17
    else:
        mconsole("SUCCESS!")
    return 0


def batch_console(batchfile=None,batchlist=None,level="INFO"):
    if batchfile is not None and os.path.isfile(batchfile):
        with open(batchfile,"r") as f:
            batchlist = f.readlines()
    if batchlist is not None:
        for line in batchlist:
            mconsole(line.strip('\n'),level=level)
    else:
        mconsole("No file or list specified",level="ERROR")


if __name__ == '__main__': main()