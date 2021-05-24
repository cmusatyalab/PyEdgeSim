#!/usr/bin/env python

import sys
import os
import pprint
import json
import shutil
sys.path.append("./lib")
from pyutils import *
from config import *
from simlogging import mconsole,configureLogging

from advantedgeapilib import *
from setupBuildEnv import setMEEPPATH

cnf = initConfig()
api = AdvantEDGEApi()

def main():
    configureLogging()
    getOpenRTiST(cnf)
    startOpenRTiST(cnf)
    pass

def deployAdvantEDGE(cnf):
    meepctl = os.path.join(*[cnf['ADVANTEDGEDIR'],"bin","meepctl","meepctl"])
    setMEEPPATH()
    meepctl = "meepctl"
    if oscmd("{} deploy dep".format(meepctl)) != 0: return -1
    if oscmd("{} dockerize all".format(meepctl)) != 0: return -1
    if oscmd("{} deploy core".format(meepctl)) != 0: return -1
    return 0

def getOpenRTiST(cnf):
    srcimg = "cmusatyalab/openrtist"
    dstimg = "meep-docker-registry:30001/openrtist:real"
    oscmd("docker pull {}".format(srcimg))
    oscmd("docker tag {} {}".format(srcimg,dstimg))
    oscmd("docker push {}".format(dstimg))
    return 0

def startOpenRTiST(cnf):
    scenname = cnf['SCENARIO']
    sandbox = cnf['SANDBOX']
    api.setSandbox(sandbox)
    mconsole("(Re)starting OpenRTiST scenario {} in sandbox {}".format(scenname,sandbox))    
    api.startScenario(scenname,restart=True)
    return 0

def stopDeployment(cnf,settletime=120):
    mconsole("Shutting down deployment and waiting {} seconds".format(settletime))
    cmdstr = "kubectl get namespace -o json|jq -r '.items[] | select( .metadata.name | test(\"{}\")) | .metadata.name'" \
        .format(cnf['SANDBOX'])
    ns = cmd0(cmdstr)
    if len(ns) > 0:
        oscmd("kubectl delete namespace {}".format(cnf['SANDBOX']))
    cmdstr = "bash -c 'meepctl delete core;meepctl delete dep;sleep {}'".format(settletime)
    oscmd(cmdstr)

def startDeployment(cnf,settletime=0):
    mconsole("Starting deployment and waiting {} seconds".format(settletime))
    cmdstr = "bash -c 'meepctl deploy dep;meepctl deploy core;sleep {}'".format(settletime)
    oscmd(cmdstr)
    mconsole("You will need to recreate sandbox {} and deploy scenario {} in it" \
            .format(cnf['SANDBOX'],cnf['SCENARIO']))

def installCharts(cnf):
    datadir = "./data"
    destdir = os.path.expanduser("~/.meep/virt-engine")
    entry = input("Copy scenarios and charts into AdvantEDGE [y/N] ") or "y"
    if entry in ['Y','y']:
        for root, dirs, files in os.walk(datadir):
            if len(files) > 0:
                fdestdir = root.replace(datadir,destdir)
                os.makedirs(fdestdir,exist_ok=True)
                for fn in files:
                    srcfn = os.path.join(root,fn)
                    dstfn = os.path.join(fdestdir,fn)
                    shutil.copy2(srcfn,dstfn)
    return 0


if __name__ == '__main__': main()
