#!/usr/bin/env python
import sys
import os
import time
import json

from pyutils import *
from simlogging import mconsole

from testScenarios import *
from InterferenceScenarios import *


profjsonfn = "./testScenarios.json"

def main():
    aa = ADVE_ProfMgr(prfdict = testprofiledict)
    numevents = 30
    latscale = 1.3
    jitscale = 1.3
    tptscale = 1.0
    losscale = 1.0
    ''' Generate LEL Test Scenario '''
    leltestprofile = aa.newProf(name = "leltestprofile",application = "edgevdi", latencyDistribution = "Pareto")
    leltestprofile.composeProf(initcond = 0, exceptions = 0,netcharevents = numevents,mobilityevents=0)
    leltestprofile.addInitialConditions(DEFINIT)
    chardict = {'newlatency':20,'newlatencyVariation':4,'newthroughput':1000, 'newpacketLoss':2,
             'newname':"zone1-poa1",'newwaitafter':5}
    for evnum in range(0,numevents):
        leltestprofile.modifyNetCharEvent(evnum,**chardict)
        if numevents / max(1,evnum) > 2: # First half of events
            chardict['newlatency'] = round(chardict['newlatency']*latscale)
            chardict['newlatencyVariation'] = round(chardict['newlatencyVariation']*jitscale)
            chardict['newthroughput'] = round(chardict['newthroughput']/tptscale)
            chardict['newpacketLoss'] = round(chardict['newpacketLoss']*losscale)
        else: # Second half of events
            chardict['newlatency'] = round(chardict['newlatency']/latscale)
            chardict['newlatencyVariation'] = round(chardict['newlatencyVariation']*jitscale)
            chardict['newthroughput'] = round(chardict['newthroughput']/tptscale)
            chardict['newpacketLoss'] = round(chardict['newpacketLoss']*losscale)

    leltestprofile.prettyPrint()
    leltestprofile.saveProf("./{}.json".format('leltestprofile'))
    
    pass

class ADVE_ProfMgr(object):
    def __init__(self, fn = profjsonfn, prfdict = None, **kwargs):
        self.fn = fn
        self.prfdict = prfdict
        self.kwargs = kwargs
        pass
    
    class Profile(object):
        def __init__(self,name = None,application = None, latencyDistribution = "Normal",
                     initial_conditions= [],
                     exceptions= [],
                     test_events = [],
                     **kwargs):
            self.kwargs = kwargs
            self.prfdata = {'name':name,'application':application,"latencyDistribution":latencyDistribution,
                             'initial_conditions':initial_conditions,
                             'exceptions':exceptions,
                             'test_events':test_events}
            
        def composeProf(self,initcond = 1, exceptions = 1, mobilityevents = 1,netcharevents = 1):
            prfdata = self.prfdata.copy()
            if initcond != 0: prfdata['initial_conditions'] = [INITCONDTEMPLATE.copy() for ii in range(0,initcond)]
            if exceptions != 0: prfdata['exceptions'] = [EXCEPTIONTEMPLATE.copy() for ii in range(0,exceptions)]
            if mobilityevents != 0: prfdata['test_events'] = [MOBILITYEVENTTEMPLATE.copy() for ii in range(0,mobilityevents)]
            if netcharevents != 0: prfdata['test_events'] = prfdata['test_events'] + [NETCHAREVENTTEMPLATE.copy() for ii in range(0,netcharevents)]
            
            self.prfdata = prfdata

        def modifyException(self,exceptnum,newname = None, newlatency = None,newlatencyVariation = None, 
                               newthroughput = None, newpacketLoss = None):
            if newname is not None: self.prfdata['exceptions'][exceptnum]['name'] = newname            
            if newlatency is not None: self.prfdata['exceptions'][exceptnum]['latency'] = newlatency
            if newlatencyVariation is not None: self.prfdata['exceptions'][exceptnum]['latencyVariation'] = newlatencyVariation
            if newthroughput is not None: self.prfdata['exceptions'][exceptnum]['throughput'] = newthroughput
            if newpacketLoss is not None: self.prfdata['exceptions'][exceptnum]['packetLoss'] = newpacketLoss
            pass            
            
        def modifyNetCharEvent(self,eventnum,newname = None, newlatency = None,newlatencyVariation = None, 
                               newthroughput = None,newpacketLoss = None, newwaitafter = None):
            if self.prfdata['test_events'][eventnum]['type'] != "NETWORK-CHARACTERISTICS-UPDATE":
                mconsole("Event # {} is not a network characteristic event.\n{}" \
                         .format(eventnum,self.prfdata['test_events'][eventnum]['type']),level="ERROR")
                return -1
            if newname is not None: self.prfdata['test_events'][eventnum]['name'] = newname            
            if newlatency is not None: self.prfdata['test_events'][eventnum]['latency'] = newlatency
            if newlatencyVariation is not None: self.prfdata['test_events'][eventnum]['latencyVariation'] = newlatencyVariation
            if newthroughput is not None: self.prfdata['test_events'][eventnum]['throughput'] = newthroughput
            if newpacketLoss is not None: self.prfdata['test_events'][eventnum]['packetLoss'] = newpacketLoss
            if newwaitafter is not None: self.prfdata['test_events'][eventnum]['waitafter'] = newwaitafter
            pass
        
        def modifyMobilityEvent(self,eventnum,newmover = None, newdest = None, newwaitafter = None):
            if self.prfdata['test_events'][eventnum]['type'] != "MOBILITY":
                mconsole("Event # {} is not a mobility event.\n{}" \
                         .format(eventnum,self.prfdata['test_events'][eventnum]['type']),level="ERROR")
                return -1
            if newmover is not None: self.prfdata['test_events'][eventnum]['mover'] = newmover            
            if newdest is not None: self.prfdata['test_events'][eventnum]['dest'] = newdest
            if newwaitafter is not None: self.prfdata['test_events'][eventnum]['waitafter'] = newwaitafter
            pass
        
        def getProfData(self): return self.prfdata
        def setName(self,name): self.prfdata['name'] = name
        def getName(self): return self.prfdata['name']
        def addInitialConditions(self,initcond): self.prfdata['initial_conditions'] = initcond
        def addExceptions(self,exceptions): self.prfdata['exceptions'] = exceptions
        def addTestEvents(self,test_events): self.prfdata['test_events'] = test_events
        
        def prettyPrint(self):
            pdat = self.prfdata
            for key1 in pdat.keys():
                if isinstance(pdat[key1],(str,int,float)):
                    print("{:<11s}:\t{}".format(key1,pdat[key1]))
                elif isinstance(pdat[key1],(dict)):
                    print("{}:".format(key1))
                    for key2 in pdat[key1].keys():
                        print("\t{:<9s}:\t{}".format(key2,pdat[key1][key2]))
                elif isinstance(pdat[key1],(list)):
                    print("{}:".format(key1))
                    for item,cnt in zip(pdat[key1],range(0,len(pdat[key1]))):
                        print("\tItem # {}".format(cnt))                  
                        for key2 in item.keys():
                            print("\t\t{:<20s}:\t{}".format(key2,item[key2]))
        
        def saveProf(self,fn):  writeJSON(fn,self.prfdata)

    ''' Basic Utility Methods '''
    def newProf(self,name=None,application=None,**kwargs): 
        return self.Profile(name=name, application=application,**kwargs)
    def saveProfDict(self): writeJSON(self.fn,self.prfdict)
        
    def readProfDict(self): return  readJSON(self.fn)
    
    def getProf(self,pf): return self.prfdict[pf]
    
    def getProfDict(self): return self.prfdict
    
    def renameProf(self,pf,newname):
        tprof = pf.copy()
        tprof['name'] = newname
        return tprof
    
    def addProf(self,pf):
        if pf['name'] in list(self.prfdict.keys()):
            mconsole("Profile exists: {}; replacing".format(pf['name']),level="WARNING")
        self.prfdict[pf['name']] = pf
    
    def copyProf(self, pf, npf = None): 
        if not npf: npf = pf + "_copy" 
        return self.addProf(self.renameProf(self.getProf(pf),npf))

if __name__ == '__main__': main()