#!/usr/bin/env python
import sys
print(sys.path)
sys.path.append(".")
sys.path.append("../lib")
import numpy as np

from pyutils import *
import simlogging
from simlogging import mconsole
from profile_manager import ADVE_ProfMgr as ProfMgr
from InterferenceScenarios import *

INTDIR = "./interference_profiles"
LOGNAME=__name__

NETCHARNODE='horizon-cloudlet'
MOBILITYNODE = 'zone1-poa1'

VARIANTS= 5
LATRANGE = range(50,400)

def main():
    global logger
    LOGFILE="interference_scenarios.log"
    logger = simlogging.configureLogging(LOGNAME=LOGNAME,LOGFILE=LOGFILE,loglev=logging.INFO, coloron=False) 

    aa = ProfMgr(prfdict = None)
    
    zeroprof = genZero(aa,saveOn=True)
    
    normallst = genNormal(aa,saveOn=True,variants = 5)
    badsignallst = genBadSignal(aa,getFresh(aa),saveOn=True, latrange = LATRANGE,variants = VARIANTS)
    loadlst = genLoad(aa,getFresh(aa),saveOn=True,variants = VARIANTS)
    combolst = genCombo(aa,getFresh(aa),saveOn=True,latrange = LATRANGE,variants = VARIANTS)
    pass

def getFresh(aa): return genNormal(aa,saveOn=False,variants = 1)

def genZero(aa,name = "zero", saveOn=False):
    tmpprof = aa.newProf(name = name,application = "edgevdi", latencyDistribution = "Normal")
    tmpprof.composeProf(initcond = 0, exceptions = 0,netcharevents = 0,mobilityevents=0)
    tmpprof.addInitialConditions(ZEROINIT)
    if saveOn: tmpprof.saveProf("{}/{}.json".format(INTDIR,name))
    return tmpprof

def genNormal(aa,name = "tmpprof",variants = 1, saveOn=False,verbose = True):
    retlst = []
    for config in NETCONFIGS:
        for varno in range(0,variants):
            config['duration'] = genRandom(duration=True)['duration']
            name = config['name']
            dist = config['latencyDistribution'] if 'latencyDistribution' in config else 'Normal'
            tmpprof = aa.newProf(name = name,application = "edgevdi", latencyDistribution = dist)
            tmpprof.composeProf(initcond = 0, exceptions = 0,netcharevents = 1,mobilityevents=0)
            tmpprof.addInitialConditions(config)
            
            ''' Need to have an event to enable running for duration '''
            chardict = {'newlatency':config['POA']['latency'],
                        'newlatencyVariation':config['POA']['latencyVariation'],
                        'newthroughput':config['POA']['throughput'], 
                        'newpacketLoss':config['POA']['packetLoss'],
                        'newname':MOBILITYNODE,'newwaitafter':config['duration']}
            tmpprof.modifyNetCharEvent(0,**chardict)
            newname = "{}_V{:02d}".format(name,varno)
            tmpprof.setName(newname)
            if saveOn: tmpprof.saveProf("{}/{}.json".format(INTDIR,newname,varno))
            if verbose: mconsole("Generate normal variant {}".format(newname))
            retlst.append(tmpprof)
    pass
    return retlst
 
def genBadSignal(aa,inlst,**kwargs): return genProfile(aa,inlst,type="BadSignal",**kwargs)
def genLoad(aa,inlst,**kwargs): return genProfile(aa,inlst,type="Load",**kwargs)
def genCombo(aa,inlst,**kwargs): return genProfile(aa,inlst,type="Combo",**kwargs)

def genProfile(aa,inlst, name = "tmpprof", type = None, variants = 5, saveOn=False, printOn = False,**kwargs):
    retlst = []
    for tmpprof in inlst: # Each network type -- derived from normal scenarios
        origname = tmpprof.getName()
        for varno in range(0,variants): # multiple variants
            ''' Scenario length and steps '''
            randdict = genRandom(duration=True,steps=True)
            dur = randdict['duration']
            steps = randdict['steps']
            durlst = genRandomList(dur,steps)
            ''' Network Characteristics for each step '''
            if type == 'Load':
                dictlst = genRandomLoad(steps=steps,durlst = durlst,**kwargs)
            elif type == "BadSignal":
                dictlst = genRandomBadSignal(steps=steps, durlst = durlst, **kwargs)
            elif type == "Combo":
                dictlst = genRandomCombo(steps=steps, durlst=durlst, **kwargs)
            else:
                mconsole("Bad profile type: {}",type)
                return retlst
            
            jj = 0
            for ii in range(0,len(dictlst)):
                if 'latency' in dictlst[ii].keys():     
                    dictlst[ii]['waitafter'] = durlst[jj]
                    jj += 1
                    
            ''' Prepare the scenario '''
            newname = "{}_{}_V{:02d}".format(origname,type,varno)
            mconsole("Generate variant {}".format(newname))                
            tmpprof.setName(newname)
            tmpprof.addTestEvents(dictlst)
            if printOn: tmpprof.prettyPrint()
            if saveOn: tmpprof.saveProf("{}/{}.json".format(INTDIR,newname))
            retlst.append(tmpprof)
    return retlst

def genRandomBadSignal(steps = 1, durlst = [1], **kwargs):
    dictlst = [genRandom(latency=True,jitter=True,packetloss=True, dur = dur, **kwargs) \
               for dur in durlst]
    return dictlst

def genRandomLoad(steps = 1, durlst = [0], **kwargs): 
    retlst = []
    tmpdict = {}
    for step,dur in zip(range(0,steps),durlst):
        bwmix,bwall = genCongestionMix()
        mconsole("Generating load of {} kbps".format(sum(bwmix)),level="DEBUG")
        ''' Connect and disconnect as appropriate '''
        for ue in bwall:
            tmpdict['mover'] = "iperf-ue1-{}k".format(ue)
            tmpdict['waitafter'] = 0
            tmpdict['type'] = 'MOBILITY'
            if ue in bwmix:
                tmpdict['dest'] = MOBILITYNODE
            else:
                tmpdict['dest'] = "DISCONNECTED"
            retlst.append(tmpdict.copy())
        ''' Run with load for awhile '''
        retlst[-1]['waitafter'] = dur
        ''' End by disconnecting all '''
    for ue in bwall:
        tmpdict['mover'] = "iperf-ue1-{}k".format(ue)
        tmpdict['waitafter'] = 0
        tmpdict['type'] = 'MOBILITY'
        tmpdict['dest'] = "DISCONNECTED"
        retlst.append(tmpdict.copy())
    return retlst

def genRandomCombo(steps=1,durlst = [1], **kwargs):
    retlst = []
    ldlstlen = len(convallst)
    for dur in durlst:
        retlst += genRandomLoad()[:-ldlstlen] + genRandomBadSignal(durlst = [dur])
    retlst += genRandomLoad()[ldlstlen:]
    return retlst

''' Generate random variables '''

def genRandom(duration = False, durdist = 'Uniform', durrange = range(30,121), dur = 1, 
              steps = False, stepdist = 'Uniform', steprange = range(5,11),
              latency = False, latdist = 'Uniform',latrange = range(40,200), 
              jitter = False, jitdist = 'Uniform', jitrange = range(5,50),
              packetloss = False, pldist = 'Uniform', plrange = range(5,20),
              dlbw = False,
              llist = False, lsum = 30, llen = None,
              **kwargs):
    retdict = {}
    if duration:
        retdict['duration'] = genRandomInt(durdist,durrange)
    if steps:
        retdict['steps'] = genRandomInt(stepdist,steprange)
    if latency:
        retdict['latency'] = genRandomInt(latdist,latrange)
        retdict['type'] = 'NETWORK-CHARACTERISTICS-UPDATE'
        retdict['name'] = NETCHARNODE
        retdict['waitafter'] = dur
    if jitter:
        retdict['latencyVariation'] = genRandomInt(jitdist,jitrange)
    if packetloss:
        retdict['packetLoss'] = genRandomInt(pldist,plrange)
    if dlbw:
        retdict['throughput'] = genRandomLoad()
    if llist:
        llen = llen if llen is not None else lsum/10
        retdict['list'] = genRandomList(lsum,llen)
    return retdict

def genRandomList(lsum,llen):
    retlst = [round(item) \
              for item in list(np.random.dirichlet(np.ones(llen),size=1)[0] * lsum)]
    mconsole("Total Duration target: {} actual: {}".format(lsum, sum(retlst)),level="DEBUG")
    return retlst
    
def genRandomInt(dist,drange):
    if dist != "Uniform":
        mconsole("Distribution {} not yet implemented; using Uniform".format(dist),level="ERROR")
    return np.random.randint(drange[0],high=drange[-1])

convallst = [50,100,200,400,800,1600]
def genCongestionMix():
    mixlen = np.random.choice(range(1,len(convallst)),1)
    bwlst = np.random.choice(convallst,mixlen[0],replace = False)
    return bwlst,convallst

    
if __name__ == '__main__': main()
