#!/usr/bin/env python

import sys
import os
sys.path.append(os.getcwd())
import requests
import pprint
import json
import shutil
from pyutils import *
from config import *
from simlogging import mconsole

cnf = initConfig()
disable_certs="-Dio.swagger.parser.util.RemoteUrl.trustAll=true"

def main():
    global FILEROOT
    if os.getcwd().endswith("lib"): FILEROOT="../files"
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

def getYAML(fn,version,app):
    # https://raw.githubusercontent.com/InterDigitalInc/AdvantEDGE/release-1.9.0/go-apps/platform-control-ctrl/api/swagger.yaml
    url = BASEURL.replace("VERSION",version)
    url= f"{url}meep-{app}/api/swagger.yaml"
    r = requests.get(url, allow_redirects=True)
    if r.status_code == 200: open(f"{fn}",'wb').write(r.content)
    print(fn,version)

if __name__ == '__main__': main()

        
