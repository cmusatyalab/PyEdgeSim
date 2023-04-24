#!/usr/bin/env python
import sys, os
print(sys.path)
sys.path.insert(0,"./lib")
from optparse import OptionParser
from pyutils import *

from simlogging import *
from config import *
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
        batch_console(batchfile="doc/welcome.txt")
        (options,_) = cmdOptions(cnf)
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
    entry = input("Setup runtime environment? [y/N] ") or "n"
    if entry in ['Y','y']:
        if setupKubernetes(cnf) != 0: return -1
        if setupHelm(cnf) != 0: return -2
        if installAdvantEDGE(cnf) != 0: return -3
    ''' Set up build environment (CPU Only) '''
    entry = input("Setup build environment? [y/N] ") or "n"
    if entry in ['Y','y']:
        if installGO(cnf) != 0: return -4
        if installNodeJS(cnf) != 0: return -5
        if installESLint(cnf) != 0: return -6
        if installGolangCILint(cnf) != 0: return -7
        if installMeepCTL(cnf) != 0: return -8
        if buildMeepAll(cnf) != 0: return -9
    ''' Deploy AdvantEDGE '''
    if deployAdvantEDGE(cnf) != 0: return -10
    ''' Pull OpenRTiST '''
    if getOpenRTiST(cnf) != 0: return -13
    ''' Set up the scenario '''
    if installCharts(cnf) != 0: return -13
    ''' Deploy the scenario in the sandbox '''         
    if startOpenRTiST(cnf) != 0: return -14
    ''' Data Management '''
    entry = input("Setup data management? [y/N] ") or "n"
    if entry in ['Y','y']:        
        if setupInfluxDB(cnf) != 0: return -11
        if setupGrafana(cnf) != 0: return -12
    ''' Automation '''
    if setupAutomation(cnf) != 0: return -15
    if runAutomationTest(cnf) != 0: return -16
    ''' Create automation report '''
    if createReport(cnf,filename="report.png") != 0: return -17
    else: mconsole("SUCCESS!")
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
