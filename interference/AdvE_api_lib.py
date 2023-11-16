#!/usr/bin/env python

import sys
import os
from datetime import datetime
import time
import json
import re
import pprint
from importlib import import_module

from pyutils import *
from simlogging import mconsole
from no_ssl_verification import no_ssl_verification

runfailuretests = False
api = None
testsandbox = 'horizon-filter-1'
testscenname = 'horizon-filter-1'

class AdvantEDGEApi(object):
    def __init__(self, SANDBOX = None, SCENARIO = None, **kwargs):
        ''' Import the right client packages  '''
        global sbclient
        global pltclient
        global monclient
        global client
        mconsole(f"Configuring sandbox={SANDBOX} scenario={SCENARIO}")
        PKGLST=["client","monitorclient","platformclient","sandboxclient"]
        self.scenariodictionary = {}
        self.sandbox = SANDBOX
        self.scenario = SCENARIO
        self.apiip = kwargs['APIIP'] if 'APIIP' in kwargs else '127.0.0.1'
        # PKGLST=[f"{pkg}-{SANDBOX}-{SCENARIO}" for pkg in PKGLST]
        try:
            sbclient = import_module(PKGLST[3])
            sbclient = self.dontVerifySSL(sbclient)
            self.setSandbox(SANDBOX)
            pltclient = import_module(PKGLST[2])
            pltclient = self.dontVerifySSL(pltclient)
            monclient = import_module(PKGLST[1])
            monclient = self.dontVerifySSL(monclient)
            client = import_module(PKGLST[0])
            client = self.dontVerifySSL(client)
            ApiException = client.rest.ApiException
            EventMobility = client.models.event_mobility.EventMobility
        except:
            mconsole(f"Could not import the client APIs for sandbox {SANDBOX} and scenario {SCENARIO}",level="ERROR")
            mconsole("Please run with -A option one time to generate API libraries",level="ERROR")
            sys.exit(1)
        self.apidict = {
            'eventreplay':sbclient.EventReplayApi(),
            'scenarioconfiguration':pltclient.ScenarioConfigurationApi(),
            'scenarioexecution':sbclient.ActiveScenarioApi(),
            'eventsend':sbclient.EventsApi(),
            'podstates':monclient.PodStatesApi()
            }

        pass
        
    ''' Basic Class Utilities '''
    def dontVerifySSL(self, swaggerclient):
        configuration = swaggerclient.Configuration()
        configuration.host = re.sub("https://.+?\/", f"https://{self.apiip}/",configuration.host)
        configuration.verify_ssl = False
        configuration.ssl_ca_cert = None
        configuration.assert_hostname = False
        configuration.cert_file = None
        swaggerclient.Configuration.set_default(configuration) 
        retclient = swaggerclient
        return retclient

        
    def setSandbox(self,sandbox): 
        self.sandbox = sandbox if sandbox is not None else testsandbox
        configuration = sbclient.Configuration()
        configuration.host = re.sub("sandboxname", sandbox ,configuration.host)
        sbclient.Configuration.set_default(configuration)

    def getApiKeys(self):
        return list(self.apidict.keys())
    
    def getSubApi(self,key):
        subapi = self.apidict[key] if key in self.apidict else None
        if subapi is None:
            mconsole("Invalid Key: %s" % key,level="ERROR")
        return subapi

    def _printresponse(self,resp):
        pprint(resp)
        
    ''' AdvantEDGE Class Utilities '''
    ''' Handling Scenarios '''
        
    def startScenario(self,scenname, verbose= False, restart=False, terminate_timeout = 45, activate_timeout=20, **kwargs):
        ''' Starts up a new scenario if not already running 
            Also, stops any already running scenario '''
        
        if not self.isScenario(scenname,verbose=verbose):
            mconsole("Invalid scenario name: %s" % scenname,level="ERROR")
            return False
        if self.isScenarioRunning():
            activescenario = self.getActiveScenario()
            if restart or (activescenario is not None and activescenario.name != scenname):
                self.terminateActiveScenario()
                if self.waitScenarioTerminated(terminate_timeout):
                    activescenario = self.activateScenario(scenname)
        else:
            activescenario = self.activateScenario(scenname)
        if not self.waitScenarioRunning(activate_timeout):
            mconsole("Could not start scenario",level="ERROR")
            return False
        else:
            mconsole("Scenario {} running".format(scenname))
            return True
        
    def activateScenario(self,scenname,**kwargs):
        ''' Starts a scenario '''
        api_response = None
        if not self.isScenario(scenname):
            mconsole("Scenario %s is not a real scenario" % scenname,level="ERROR")
            return None
        activescen = self.getActiveScenario()
        if activescen is None:
            api_instance = self.getSubApi('scenarioexecution')
            api_response = api_instance.activate_scenario(scenname)
        elif activescen.name == scenname:
            mconsole("Scenario %s already active" % scenname)
            api_response = scenname
        else:
            mconsole("Scenario %s already running; Terminate first" % activescen.name)
            api_response = activescen.name
        return api_response
    
    def isScenario(self,scenname,**kwargs):
        ''' Is it a Real Scenario? '''
        scenlst = []
        scenarios = self.getScenarioList(**kwargs)
        if scenarios is not None: scenlst = [scen for scen in scenarios if scen.name == scenname]
        return True if len(scenlst) > 0 else False
        
    def getScenarioList(self,verbose=False, **kwargs):
        ''' Get all of the available scenarios '''
        api_instance = self.getSubApi('scenarioconfiguration')
        api_response = api_instance.get_scenario_list()
        scenarios = api_response.scenarios
        if scenarios is not None: devnull = [mconsole("Scenario: %s" % scen.name) for scen in scenarios if verbose]
        return scenarios
    
    def getMyScenario(self,scenname, verbose=False, **kwargs):
        scenarios = self.getScenarioList()
        for xx in scenarios: 
            if xx.name == scenname: return xx
        return None
    
    def getActiveScenario(self,verbose = False, **kwargs):
        ''' Get the currently running scenario '''
        api_instance = self.getSubApi('scenarioexecution')
        # try:
        api_response = api_instance.get_active_scenario()
        # except sbclient.rest.ApiException as e:
        #     if verbose:
        #         mconsole ("No Active Scenario: {}\n".format(e),level="ERROR")
        #     else:
        #         mconsole("No Active Scenario")
        #     api_response=None
        return api_response

    def terminateActiveScenario(self):
        ''' Terminate the currently running scenario '''
        api_instance = self.getSubApi('scenarioexecution')
        try:
            api_response = api_instance.terminate_scenario()
        except sbclient.rest.ApiException as e:
            mconsole("No Active Scenario: %s\n" % (e))
            api_response=None
        return api_response
    
    def purgeActiveScenario(self,scenarioname):
        cmd_all("/snap/bin/helm ls",output=True)
        cmd_all("bash ./purgescenario.sh %s" % scenarioname,output=True)
        pass
    
    class scenariodata(object):
        ''' Helper class for parsing the scenario data '''
        def __init__(self,paramdict, **kwargs):
            self.net_char = paramdict['net_char']
            self.type = paramdict['type']
            self.name = paramdict['name']
            
    def parseScenario(self,scenario,printon=False):
        ''' Go through the running scenario to get relevant info '''
        ''' Returns a dictionary with the scenario data '''
        if printon:
            print(scenario.name)

        scendict = {'name':scenario.name,'deployment':scenario.deployment,
                    'domainlst':[],'zonelst':[],'locationlst':[], 'physloclst':[],'processlst':[]}
        scendict['deploymentdata'] = self.scenariodata({
            'name':'Internet', 
            'net_char':scenario.deployment.net_char,
            'type':'SCENARIO'
        })
        for domain in scenario.deployment.domains:
            thisdomain = domain.name
            scendict['domainlst'].append((thisdomain,domain.type))
            domaindict = {'name':thisdomain,'type':domain.type,'net_char':domain.net_char,'domain':domain}
            for zone in domain.zones:
                thiszone = zone.name
                scendict['zonelst'].append((thiszone,zone.type))
                if printon:
                    print('\t\t',thiszone)
                zonedict = {'name':thiszone,'type':zone.type,'net_char':zone.net_char,'zone':zone}
                for location in zone.network_locations:
                    thisloc = location.name
                    scendict['locationlst'].append((thisloc,location.type))
                    if printon:
                        print('\t\t\t',thisloc)
                    locdict = {'name':thisloc,'type':location.type,'net_char':location.net_char,'location':location}                    
                    if location.physical_locations is not None:
                        for physlocation in location.physical_locations:
                            thisphyslocation = physlocation.name
                            scendict['physloclst'].append((thisphyslocation,physlocation.type))
                            if printon:
                                print('\t\t\t\t',thisphyslocation)
                            physlocdict = {'name':thisphyslocation,'type':physlocation.type,'net_char':physlocation.net_char,'physlocation':physlocation}
                            if physlocation.processes is not None:
                                for aprocess in physlocation.processes:
                                    thisproc = aprocess.name
                                    scendict['processlst'].append((thisproc,aprocess.type))
                                    if printon:
                                        print('\t\t\t\t\t',thisproc)
                                    procdict = {'name':thisproc,'type':aprocess.type,'net_char':aprocess.net_char,'process':aprocess}
                                    physlocdict[thisproc] = procdict
                                locdict[thisphyslocation] = physlocdict
                    zonedict[thisloc] = locdict
                domaindict[thiszone] = zonedict
                pass
            scendict[thisdomain] = domaindict
        return scendict
    
    def waitScenarioTerminated(self,timout):
        ''' Helper to wait until the running scenario ends '''
        WAITSECONDS = timout
        self.isScenarioRunning()
        for ii in range(0,WAITSECONDS):
            if not self.isScenarioTerminated():
                time.sleep(2)
            else:
                break
        if ii == WAITSECONDS-1:
            mconsole("Timed out waiting for scenario",level="ERROR")
            return False
        return True
    
    def isScenarioTerminated(self):
        ''' Helper to check if the running scenario has ended '''
        podnames = self.getPodNames(scenpods=True)
        if len(podnames) == 0:
            return True
        podstatus = self.getPodStatus(podnames)
        [mconsole("Waiting for pod to terminate: %s %s" % (pod[0],pod[1])) for pod in podstatus]
        return False
    
    def waitScenarioRunning(self, timout):
        ''' Wait until the scenario is running '''
        WAITSECONDS = timout
        for ii in range(0,WAITSECONDS):
            if not self.isScenarioRunning():
                time.sleep(2)
            else:
                break
        if ii == WAITSECONDS-1:
            mconsole("Timed out waiting for scenario",level="ERROR")
            return False
        mconsole("Scenario is running")
        return True
        pass
    
    def isScenarioRunning(self):
        ''' Check if the scenario is running '''
        podnames = self.getPodNames(scenpods=True)
        if len(podnames) == 0:
            return False
        podstatus = self.getPodStatus(podnames)
        isrunning = True
        for pod in podstatus:
            if pod[1] != "Running":
                isrunning = False
                mconsole("Waiting for pod to run: %s %s" % (pod[0],pod[1]))
        return isrunning
    
    ''' Scenario Dictionary Methods '''
    ''' The scenario dictionary is the local data extracted from the scenario '''
    def setScenarioDictionary(self):
        activescenario = self.getActiveScenario()
        self.scenariodictionary = self.parseScenario(activescenario)
        return self.scenariodictionary
        
    def getScenarioDictionary(self):
        return self.scenariodictionary

    def dumpScenarioDictionary(self, verbose=False, **kwargs):
        verbose = kwargs['verbose'] if 'verbose' in kwargs else False
        scendict = kwargs['scenario_dictionary'] if 'scenario_dictionary' in kwargs else self.scenariodictionary

        print("Zones:")
        devnull = [print('\t',zone) for zone in scendict['zonelst'] if 'zone' in zone]
        print("POAs:")
        devnull = [print('\t',poa) for poa in scendict['locationlst'] if 'poa' in poa]
        print("UEs and Edge Nodes:")
        devnull = [print('\t',loc) for loc in scendict['physloclst'] if 'ue' in loc or 'edge-node' in loc]
        print("Processes:")
        devnull = [print('\t',proc) for proc in scendict['physloclst']]
    
    def findNodeInDictionary(self,name,verbose=False):
        ''' Search the dictionary for node with name and return data about that node '''
        sd = self.scenariodictionary
        retval = None
        def condprint(str1,str2):
            if verbose:
                print(str1,str2)
        if name == "Internet":
            return sd['deploymentdata']
        for domain in sd['deployment'].domains:
            if domain.name == name:
                condprint("Domain Match",name)
                retval = domain
                break
            else:
                for zone in domain.zones:
                    if zone.name == name:
                        condprint("Zone Match",name)
                        retval = zone
                        break
                    else:
                        for location in zone.network_locations:
                            if location.name == name:
                                condprint("Location Match",name)
                                retval = location
                                break
                            elif location.physical_locations is not None:
                                for physlocation in location.physical_locations:
                                    if physlocation.name == name:
                                        condprint("physlocation Match",name)
                                        retval = physlocation
                                        break
                                    elif physlocation.processes is not None:
                                        for aprocess in physlocation.processes:
                                            if aprocess.name == name:
                                                condprint("physlocation Match",name)
                                                retval = aprocess    
                                                break
        return retval
        
    ''' Events (Mobility and Network Characteristics  '''
    ''' Wrapper methods '''
    def setMultipleValues(self,pdct,verbose=False): # TODO add new new net_chars
        name = pdct['name']
        for key in pdct.keys():
            if key == 'latency':
                self.setLatency(name,pdct['latency'])
            elif key == 'latencyVariation':
                self.setLatencyVariation(name,pdct['latencyVariation'])
            elif key == 'throughput':
                self.setThroughput(name,pdct['throughput'])
            elif key == 'packetLoss':
                self.setPacketLoss(name,pdct['packetLoss'])
        if verbose:
            print(name, self.getNodeNetChar(name))
    
    def getLatency(self,elementname):
        retval = self.getNetVal(elementname, 'latency')
        return retval

    def getLatencyVariation(self,elementname):
        retval = self.getNetVal(elementname, 'latencyVariation')
        return retval        
    
    def getThroughput(self,elementname):
        retval = self.getNetVal(elementname, 'throughput')
        return retval        

    def getPacketLoss(self,elementname):
        retval = self.getNetVal(elementname, 'packetLoss')
        return retval        
        
    def getNetVal(self,elementname,key):
        retdict = self.getNodeNetChar(elementname)
        retval = 0 if retdict is None or not key in retdict or retdict[key] is None else retdict[key]
        return retval
    
    def setLatency(self,elementname,latency):
        netchardict = self.getNodeNetChar(elementname)
        if netchardict is None:
            mconsole("Unable to get info for %s" % elementname,level="ERROR")
            return None
        if netchardict['latency'] != latency:
            netchardict['latency'] = latency
            ev = self.createNetworkEvent(netchardict,name="Test",elementname=elementname)
            self.sendNetworkEvent(ev)
        return latency

    def setLatencyVariation(self,elementname,jitter):
        netchardict = self.getNodeNetChar(elementname)
        if netchardict is None:
            mconsole("Unable to get info for %s" % elementname,level="ERROR")
            return None
        if netchardict['latencyVariation'] != jitter:
            netchardict['latencyVariation'] = jitter
            ev = self.createNetworkEvent(netchardict,name="Test",elementname=elementname)
            self.sendNetworkEvent(ev)
        return jitter
        

    def setLatencyDistribution(self,distribution,elementname = "Internet",verbose=False):
        allowed_dist = ["Normal", "Pareto", "Paretonormal","Uniform"]
        if distribution not in allowed_dist:
            mconsole("Distribution {} not allowed; Choose from: {}".format(distribution,allowed_dist),level="ERROR")
            return None
        mconsole("Setting latency distribution to {}".format(distribution),level="DEBUG")
        netchardict = self.getNodeNetChar(elementname)
        netchardict['latencyDistribution'] = distribution
        ev = self.createNetworkEvent(netchardict,name="Test",elementname=elementname)
        self.sendNetworkEvent(ev)        
        return distribution

    def setThroughput(self,elementname,throughput):
        netchardict = self.getNodeNetChar(elementname)
        if netchardict is None:
            mconsole("Unable to get info for %s" % elementname,level="ERROR")
            return None
        if netchardict['throughput'] != throughput:
            netchardict['throughput'] = throughput # All the same/symmetric
            netchardict['throughputDL'] = throughput 
            netchardict['throughputUL'] = throughput            
            ev = self.createNetworkEvent(netchardict,name="Test",elementname=elementname)
            self.sendNetworkEvent(ev)
        return throughput
    
    def setPacketLoss(self,elementname,packet_loss):
        netchardict = self.getNodeNetChar(elementname)
        if netchardict is None:
            mconsole("Unable to get info for %s" % elementname,level="ERROR")
            return None
        if netchardict['packetLoss'] != packet_loss:
            netchardict['packetLoss'] = packet_loss
            ev = self.createNetworkEvent(netchardict,name="Test",elementname=elementname)
            self.sendNetworkEvent(ev)
        return packet_loss
        
    def moveElement(self,mover,dest):
        ev = self.createMobilityEvent(elementname=mover,dest=dest,name="Test")
        self.sendMobilityEvent(ev)

    def getNodeNetChar(self,elementname):
        self.setScenarioDictionary()
        elementdata = self.findNodeInDictionary(elementname)
        retdict = self.getElementNetworkInfo(elementdata)
        return retdict
    
    def createNetworkEvent(self,netchardict,evname = "DEFAULTNAME", elementname = None,
                 verbose=False,**kwargs):
        ''' Check for needed arguments '''
        if elementname is None:
            mconsole("Missing element name or type",level="ERROR")
            return None
        ''' Set default arguments '''
        elementtype = netchardict['elementtype']
        del netchardict['elementtype']
        emdict = {'elementType':elementtype,'netChar':netchardict}
        emdict['elementName'] = elementname
        emdict2 = {'name':elementname,'type':'NETWORK-CHARACTERISTICS-UPDATE'}
        emj = json.dumps(emdict2)
        mconsole("{}\n{}".format(emj,emdict),level="DEBUG")
        myevent = sbclient.Event(emj,event_network_characteristics_update=emdict)    
        return myevent  
    
    def createMobilityEvent(self, evname = "DEFAULTNAME", elementname = None,
                            dest=None, verbose=False, **kwargs):
        ''' Check for needed arguments '''
        if elementname is None or dest is None:
            mconsole("Missing element name or dest",level="ERROR")
            return None
        emdict = {'elementName':elementname,'dest':dest}
        emdict2 = {'name':evname,'type':'MOBILITY'}
        emj = json.dumps(emdict2)
        if verbose:
            print(emdict,emj)
        myevent = sbclient.Event(emj,event_mobility=emdict)    
        return myevent

    def sendMobilityEvent(self,ev):
        self._sendAdvEvent(ev,'MOBILITY')

    def sendNetworkEvent(self,ev):
        self._sendAdvEvent(ev,'NETWORK-CHARACTERISTICS-UPDATE')
    
    def _sendAdvEvent(self,ev,evtype):
        api_instance = self.getSubApi('eventsend')
        try:
            api_response = api_instance.send_event(evtype, ev)
        except sbclient.rest.ApiException as e:
            mconsole("Exception when calling %s: %s\n" % (evtype,e),level="ERROR")
        except:
            e = getExceptData()
            mconsole("Exception when calling %s: %s\n" % (evtype,e),level="ERROR")

    def getElementNetworkInfo(self,element):
        if element is None:
            mconsole("No element data",level="ERROR")
            return None
        nc = element.net_char
        retdict = {'elementname':element.name,'elementtype':element.type}
        retdict['latency'] = nc.latency
        retdict['latencyVariation'] = nc.latency_variation
        retdict['latencyDistribution'] = nc.latency_distribution
        retdict['throughput'] = nc.throughput
        retdict['throughputDL'] = nc.throughput_dl
        retdict['throughputUL'] = nc.throughput_ul     
        retdict['packetLoss'] = nc.packet_loss
        return retdict

    def getPodStates(self, verbose=False,**kwargs):
        api_instance = self.getSubApi('podstates')
        long = 'true'
        try:
            api_response = api_instance.get_states_with_http_info(long=long)
            if verbose:
                pprint(api_response)
        except:
            e = getExceptData()
            mconsole("Exception when calling PodStatesApi->get_states: %s\n" % e,level="ERROR")
            api_response = None
        return api_response
    
    def getPodNames(self,scenpods=False):
        cmdout = cmd("kubectl get pods --namespace %s" % self.sandbox)
        podnames = [line.split(" ")[0] for line in cmdout[1:]]
        if scenpods:
            podnames = [pod for pod in podnames if not pod.startswith("meep-") and pod != '']
        return podnames
    
    def getPodStatus(self,podlst):
        podtuplst = [] 
        for pod in podlst:
            cmdout = cmd("kubectl get pods --namespace %s --field-selector metadata.name=%s" % (self.sandbox,pod))
            podstat = cmd("echo %s|awk '{print $3}'" % cmdout[1])[0] if len(cmdout) > 1 else None
            podtuplst.append((pod,podstat))
        return podtuplst

def getExceptData():
    return sys.exc_info()[0]

def main():
    api = AdvantEDGEApi(sandbox=testsandbox)
    ''' Test various functions '''
    api.getScenarioList(verbose=True)
    ''' Start and stop scenarios '''
    scenariorunning = api.startScenario(testscenname)
    if not scenariorunning:
        mconsole("Could not start scenario: %s" % testscenname,level="ERROR")
        sys.exit(1)
    ''' Parse active scenario '''
    activescenario = api.getActiveScenario()
    scenariodictionary = api.setScenarioDictionary()
    ''' Run tests '''
    runTests(api)
    mconsole("Completed Processing")

def runTests(api):
    mover = 'ue1'
    dest = 'zone1-poa2'
    api.moveElement(mover,dest)
    mconsole("Moved %s to %s" % (mover,dest))
    target = 'zone1-o1'
    api.setLatency(target,10 + api.getLatency(target))
    mconsole("New latency for %s: %i" % (target,api.getLatency(target)))
    
    api.setLatencyVariation(target,10 + api.getLatencyVariation(target))
    mconsole("New jitter for %s: %i" % (target,api.getLatencyVariation(target)))

    api.setPacketLoss(target,10 + api.getPacketLoss(target))
    mconsole("New packetloss for %s: %i" % (target,api.getPacketLoss(target)))    
    
    api.setThroughput(target,10 + api.getThroughput(target))
    mconsole("New throughput for %s: %i" % (target,api.getThroughput(target)))

if __name__ == '__main__': main()
