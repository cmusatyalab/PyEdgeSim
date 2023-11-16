#!/usr/bin/env python

import sys
import os
sys.path.append(os.getcwd())
import pprint
import json
import shutil
from pyutils import *
from config import *
from simlogging import mconsole

cnf = initConfig()
disable_certs="-Dio.swagger.parser.util.RemoteUrl.trustAll=true"

def main():
    setupAutomation(cnf)
    
def setupAutomation(cnf):
    entry = input("Setup automation? [y/N] ") or "n"
    if entry in ['Y','y']:     
        setupAPIs(cnf)
    return 0

def setupAPIs(cnf):
    APILST=["ctrl-engine",'mon-engine','platform-control','sandbox-control']
    PKGLST=["client","monitorclient","platformclient","sandboxclient"]
    for pkg,api in zip(PKGLST,APILST):
        srcfn = f"files/meep-{api}-swagger-{cnf['ADVANTEDGEVER']}.yaml"
        dstfn = f"meep-{api}-swagger.yaml"
        cmdstr = f"sed \'s#<IP>#{cnf['APIIP']}#;s#<SANDBOX>#{cnf['SANDBOX']}#\' {srcfn} > {dstfn}"
        oscmd(cmdstr)
        # shutil.copy2(srcfn,dstfn)
        javastr = f"java -jar files/swagger-codegen-cli.jar generate -i {dstfn} {disable_certs} -l python -o ./{api}-client/python -DpackageName={pkg}"
        pipstr = f"pip install ./{api}-client/python"
        deletestr = f"rm -rf ./{api}-client"
        cmdstr = f"{javastr} && {pipstr} && {deletestr}"
        oscmd(javastr)
        oscmd(pipstr)
        # cmdstr = javastr
        # cmdstr = f"bash -c '{cmdstr}'"
        # oscmd(cmdstr)

    return 0

if __name__ == '__main__': main()

        
