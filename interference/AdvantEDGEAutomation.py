#!/usr/bin/env python
import sys
import os
from datetime import datetime
import time
import json
from optparse import OptionParser
import requests
requests.urllib3.disable_warnings()
import client

from simlogging import mconsole
from pyutils import *
from influxutils import *

from AdvantEDGEApi import AdvantEDGEApi
from testScenarios import testprofiledict


class AdvantEDGEAutomation(object):
    def __init__(self, **kwargs):
        self.stablizetime = 4
        self.api = AdvantEDGEApi(**kwargs)
        if 'influxon' in kwargs and kwargs['influxon']:
            host = kwargs['cloudletip']
            port = kwargs['influxport']
            dbname = kwargs['influxdbname']
            self.influxclient = InfluxDBClient(host=host, port=port)
            createDB(self.influxclient,dbname)
            self.influxdfclient = DataFrameClient(host=host, port=port, database=dbname)
            dbs = getDBs(self.influxclient)
        else:
            kwargs['influxon'] = False
        self.vars = kwargs
        pass
    
    def setupEnvironment(self):
        ''' Make sure right scenario is running '''
        testscenname = self.vars['SCENARIO']
        sandbox = self.vars['SANDBOX']
        distribution = self.vars['distribution']
        if not self.api.startScenario(testscenname):
            mconsole("Could not start scenario: %s; Most likely, the sandbox %s does not exist" % (testscenname, sandbox),level="ERROR")
            return False
        self.api.setLatencyDistribution(distribution,elementname = testscenname, verbose=True)
        return True
    
    def runAutomationTest(self, runzero = True):
        testscenname = self.vars['SCENARIO']
        if self.vars['testprofilefn'] is not None:
            runprofile = readJSON(self.vars['testprofilefn']) 
        else:
            runprofile = testprofiledict[self.vars['testprofile']]
        sandbox = self.vars['SANDBOX']
        distribution = self.vars['distribution']
        api = self.api
        mconsole("Start Test %s" % runprofile['name'])
    
        ''' Set Network Characteristics to equivalent of zero '''
        if runzero: self.runZero()
        mconsole("Set test profile to %s" % runprofile['name'])
        self.vars['activeprofile'] = runprofile['name']
        self.InfluxMeasure(on = 1)
        self.setupTestProfile(runprofile,verbose=True)
        self.stablize()
        self.runEvents(runprofile,api,verbose=True)
        self.InfluxMeasure(on = 0)
        self.vars['activeprofile'] = None
        if runzero: self.runZero()
        mconsole("End Test {}".format(runprofile['name']))
        return 0
    
    def runZero(self):
        mconsole("Set test profile to %s" % 'zero')
        self.setupTestProfile(testprofiledict['zero'],verbose=True)
        self.stablize()

    def runEvents(self,runprofile, api, verbose=False):
        evlst = runprofile['test_events']
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
     
    def setupTestProfile(self, testprof,verbose=False):
        api = self.api
        sd = api.setScenarioDictionary()
        ''' Set Initial Conditions '''
        initcond = testprof['initial_conditions']
        ''' Latency Distribution '''
        latdist = testprof['latencyDistribution'] if 'latencyDistribution' in testprof else 'Normal'
        api.setLatencyDistribution(latdist,elementname = self.vars['SCENARIO'] ,verbose=True)
        ''' Get nodes '''
        uelst = [physloc for physloc in sd['physloclst'] if physloc[1] == 'UE']
        edgelst = [physloc for physloc in sd['physloclst'] if physloc[1] == 'EDGE']
        poalst = [loc for loc in sd['locationlst'] if loc[1] == 'POA']
        zonelst = [zone for zone in sd['zonelst'] if zone[1] == 'ZONE'] 
        operatorlst = [dom for dom in sd['domainlst'] if dom[1] == 'OPERATOR']
        ueapplst = [app for app in sd['processlst'] if app[1] == 'UE-APP']
        edgeapplst = [app for app in sd['processlst'] if app[1] == 'EDGE-APP']
        dplydata = sd['deploymentdata']
        ''' Configure  '''
        for node in  [(self.vars['SCENARIO'],'SCENARIO')] + uelst + edgelst + poalst + zonelst + operatorlst + ueapplst + edgeapplst:
            nodecond = initcond[node[1]]
            api.setLatency(node[0],nodecond['latency'])
            api.setLatencyVariation(node[0],nodecond['latencyVariation'])
            api.setThroughput(node[0],nodecond['throughput'])
            api.setPacketLoss(node[0],nodecond['packetLoss'])
        for excpt in testprof['exceptions']:
            api.setMultipleValues(excpt,verbose=verbose)
        pass
    
    def InfluxMeasure(self,on = 1):
        ''' Create a database entry at the start and end of the profile execution '''
        if not self.vars['influxon']: return
        specdict = {'DATABASE':self.vars['influxdbname'],'NAME':self.vars['influxmeasurement'],
                    'TAGS':['activeprofile','testerid','hdate'],'FIELDS':['on']}
        row = {'activeprofile':self.vars['activeprofile'],'testerid':self.vars['testerid'],'hdate':humandatenow(),
               'on':on}
        writeInfluxDBMeasurment(row,specdict = specdict, client=self.influxclient,verbose = False)
        pass

    def shutdown(self, terminateatshutdown=False):
        if terminateatshutdown:
            api.terminateActiveScenario()
            
    def stablize(self): time.sleep(self.stablizetime)
    def getVars(self): return self.vars
    def setVars(self,Vars): self.vars = Vars
    def getVar(self,key): return self.vars[key] if key in self.vars else None
    def setVar(self,key,value): self.vars[key] = value
      
