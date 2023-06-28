#!/usr/bin/env python

import sys
import os
sys.path.append(os.getcwd())
import pprint
import json
import shutil
from pyutils import *
from types import SimpleNamespace 

from simlogging import mconsole
cnf = {
    "APIIP":"127.0.0.1",
    "ADVANTEDGEVER":"1.8.0",
    "SCENARIO":"horizon-filter-1",
    "SANDBOX":"horizon-filter-1",
    "AUTOMATION":"horizontestlinux1",
    "FILEROOT":"Automation",
    "LATENCYDISTRIBUTION":"Normal"
}

def main():
    args = SimpleNamespace(**cnf)
    setupAPIs(apiversion = args.ADVANTEDGEVER, apiip = args.APIIP, sandbox = args.SANDBOX, scenario = args.SCENARIO, fileroot = args.FILEROOT)
    

def setupAPIs(apiversion = None, apiip = None, sandbox = None, scenario = None, fileroot = None, delete=True, **kwargs):
    APILST=["ctrl-engine",'mon-engine','platform-control','sandbox-control']
    PKGLST=["client","monitorclient","platformclient","sandboxclient"]
    PKGLST=["{}-{}-{}".format(pkg,sandbox,scenario) for pkg in PKGLST]

    for pkg,api in zip(PKGLST,APILST):
        srcfn = "{}/meep-{}-swagger-{}.yaml".format(fileroot,api,apiversion)
        dstfn = "meep-{}-swagger.yaml".format(api)
        cmdstr = "sed \'s#<IP>#{}#;s#<SANDBOX>#{}#\' {} > {}" \
            .format(apiip,sandbox,srcfn,dstfn)
        oscmd(cmdstr)
        # shutil.copy2(srcfn,dstfn)
        javastr = "java -jar {}/swagger-codegen-cli.jar generate -i {} -l python -o ./{}-client/python -DpackageName={}" \
                    .format(fileroot,dstfn,api,pkg)
        pipstr = "pip install ./{}-client/python".format(api)
        if delete:
            deletestr = "rm -rf ./{}-client".format(api)
            cmdstr = "{} && {} && {}".format(javastr,pipstr,deletestr)
        else:
            cmdstr = "{} && {}".format(javastr,pipstr)        
        cmdstr = "bash -c '{}'".format(cmdstr)
        oscmd(cmdstr)
    return 0


        
if __name__ == '__main__': main()