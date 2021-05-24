#!/usr/bin/env python

import sys

import os
from datetime import datetime
import time
import json
import sandboxclient as sbclient
import platformclient as pltclient
import monitorclient as monclient

from client.rest import ApiException
from pprint import pprint
from client.models.event_mobility import EventMobility

from pyutils import *
from simlogging import mconsole

runfailuretests = False
api = None
testscenname = 'adv-ortst-sim'
testsandbox = 'adv-ortst-sim'

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOGFILE),
            logging.StreamHandler(sys.stdout)
        ]
    )    
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


class AdvantEDGEApi(object):
    def __init__(self, sandbox = None, **kwargs):
        self.apidict = {
            'eventreplay':sbclient.EventReplayApi(),
            'scenarioconfiguration':pltclient.ScenarioConfigurationApi(),
            'scenarioexecution':sbclient.ActiveScenarioApi(),
            'eventsend':sbclient.EventsApi(),
            'podstates':monclient.PodStatesApi()
            }
        self.scenariodictionary = {}
        self.sandbox = sandbox if sandbox is not None else testsandbox
        pass
        
    ''' Basic Class Utilities '''
    def setSandbox(self,sandbox): 
        self.sandbox = sandbox if sandbox is not None else testsandbox

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
        
        if not self.isScenario(scenname):
            print("Invalid scenario name: %s" % scenname)
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
    
    def isScenario(self,scenname):
        ''' Is it a Real Scenario? '''
        scenlst = []
        scenarios = self.getScenarioList()
        if scenarios is not None: scenlst = [scen for scen in scenarios if scen.name == scenname]
        return True if len(scenlst) > 0 else False
        
    def getScenarioList(self,verbose=False, **kwargs):
        ''' Get all of the available scenarios '''
        api_instance = self.getSubApi('scenarioconfiguration')
        api_response = api_instance.get_scenario_list()
        scenarios = api_response.scenarios
        if scenarios is not None: devnull = [mconsole("Scenario: %s" % scen.name) for scen in scenarios if verbose]
        return scenarios
    
    def getActiveScenario(self):
        ''' Get the currently running scenario '''
        api_instance = self.getSubApi('scenarioexecution')
        try:
            api_response = api_instance.get_active_scenario()
        except sbclient.rest.ApiException as e:
#             print ("No Active Scenario: %s\n" % (e))
            mconsole("No Active Scenario")
            api_response=None
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
        netchardict['latency'] = latency
        ev = self.createNetworkEvent(netchardict,name="Test",elementname=elementname)
        self.sendNetworkEvent(ev)

    def setLatencyVariation(self,elementname,jitter):
        netchardict = self.getNodeNetChar(elementname)
        if netchardict is None:
            mconsole("Unable to get info for %s" % elementname,level="ERROR")
            return None
        netchardict['latencyVariation'] = jitter
        ev = self.createNetworkEvent(netchardict,name="Test",elementname=elementname)
        self.sendNetworkEvent(ev)

    def setThroughput(self,elementname,throughput):
        netchardict = self.getNodeNetChar(elementname)
        if netchardict is None:
            mconsole("Unable to get info for %s" % elementname,level="ERROR")
            return None
        netchardict['throughput'] = throughput
        ev = self.createNetworkEvent(netchardict,name="Test",elementname=elementname)
        self.sendNetworkEvent(ev)
        
    def setPacketLoss(self,elementname,packet_loss):
        netchardict = self.getNodeNetChar(elementname)
        if netchardict is None:
            mconsole("Unable to get info for %s" % elementname,level="ERROR")
            return None
        netchardict['packetLoss'] = packet_loss
        ev = self.createNetworkEvent(netchardict,name="Test",elementname=elementname)
        self.sendNetworkEvent(ev)
        
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
            print("Missing element name or type")
            return None
        ''' Set default arguments '''
        elementtype = netchardict['elementtype']
        del netchardict['elementtype']
        emdict = {'elementType':elementtype,'netChar':netchardict}
        emdict['elementName'] = elementname
        emdict2 = {'name':elementname,'type':'NETWORK-CHARACTERISTICS-UPDATE'}
        emj = json.dumps(emdict2)
        if verbose:
            print(emj,'\n',emdict)
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

if __name__ == '__main__': main()
