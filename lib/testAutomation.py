#!/usr/bin/env python

import sys

import os
from datetime import datetime
import time
import json
import client
from simlogging import mconsole

from pyutils import *
from advantedgeapilib import *
from testScenarios import *

api = AdvantEDGEApi()


def runAutomationTest(cnf, restart=False):
    entry = input("Run the test automation? [y/N] ") or "n"
    if entry not in ['Y','y']: return 0
    testscenname = cnf['SCENARIO']
    testprofile = cnf['AUTOMATION']
    stablizetime = 10
    api.setSandbox(cnf['SANDBOX'])
    scenariorunning = api.startScenario(testscenname)
    if not scenariorunning:
        mconsole("Could not start scenario: %s" % testscenname,level="ERROR")
        sys.exit(1)

    ''' Parse active scenario '''
    activescenario = api.getActiveScenario()
    mconsole("Active Scenario: %s" % activescenario.name)
    mconsole("Start Test %s" % testprofile)
    testprofiledata = testprofiledict[testprofile]
    ''' Set Network Characteristics to equivalent of zero '''
    mconsole("Set test profile to %s" % 'zero')
    setupTestProfile(testprofiledict['zero'],verbose=True)
    time.sleep(stablizetime)
    mconsole("Set test profile to %s" % testprofiledata['name'])
    setupTestProfile(testprofiledata,verbose=True)
    time.sleep(stablizetime)
    runEvents(testprofile,verbose=True)
    mconsole("Set test profile to %s" % 'zero')
    setupTestProfile(testprofiledict['zero'],verbose=True)
    time.sleep(stablizetime)
    mconsole("End Test")
    return 0
 
def shutdown(terminateatshutdown=False):
    if terminateatshutdown:
        api.terminateActiveScenario()
         
def runEvents(tstpfnm, verbose=False):
    testprof = testprofiledict[tstpfnm]
    evlst = testprof['test_events']
    for ev in evlst:
        if ev['type'] == 'MOBILITY':
            mconsole("Moving %s to %s and waiting %i seconds" % 
                      (ev['mover'],ev['dest'],ev['waitafter']))
            api.moveElement(ev['mover'],ev['dest'])
        elif ev['type'] == 'NETWORK-CHARACTERISTICS-UPDATE':
            charstr = ""
            charkeys = [key for key in ev.keys() if key in ['latency','latencyVariation','throughput','packetLoss']]
            for charkey in charkeys:
                charstr += "{}={} ".format(charkey,ev[charkey])
            mconsole("New {} network characteristics: {}and waiting {} seconds" \
                      .format(ev['name'],charstr,ev['waitafter']))
            api.setMultipleValues(ev)
        time.sleep(ev['waitafter'])
        pass
 
def setupTestProfile(testprof,verbose=False):
    sd = api.setScenarioDictionary()
    ''' Set Initial Conditions '''
    initcond = testprof['initial_conditions']
    ''' Get nodes '''
    uelst = [physloc for physloc in sd['physloclst'] if physloc[1] == 'UE']
    poalst = [loc for loc in sd['locationlst'] if loc[1] == 'POA']
    zonelst = [zone for zone in sd['zonelst'] if zone[1] == 'ZONE'] 
    operatorlst = [dom for dom in sd['domainlst'] if dom[1] == 'OPERATOR']
    ueapplst = [app for app in sd['processlst'] if app[1] == 'UE-APP']
    edgeapplst = [app for app in sd['processlst'] if app[1] == 'EDGE-APP']
    dplydata = sd['deploymentdata']
    ''' Configure  '''
    for node in [('Internet','SCENARIO')] + uelst + poalst + zonelst + operatorlst + ueapplst + edgeapplst:
        nodecond = initcond[node[1]]
        api.setLatency(node[0],nodecond['latency'])
        api.setLatencyVariation(node[0],nodecond['latencyVariation'])
        api.setThroughput(node[0],nodecond['throughput'])
        api.setPacketLoss(node[0],nodecond['packetLoss'])
    for excpt in testprof['exceptions']:
        api.setMultipleValues(excpt,verbose=verbose)
 

