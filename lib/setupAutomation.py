#!/usr/bin/env python

import sys
sys.path.append("./lib")
import os
import pprint
import json
import shutil
from pyutils import *
from config import *
from simlogging import mconsole

cnf = initConfig()


def main():
    setupAutomation(cnf)
    
def setupAutomation(cnf):
    setupAPIs(cnf)
    return 0

def setupAPIs(cnf):
    APILST=["ctrl-engine",'mon-engine','platform-control','sandbox-control']
    PKGLST=["client","monitorclient","platformclient","sandboxclient"]
    for pkg,api in zip(PKGLST,APILST):
        srcfn = "files/meep-{}-swagger-{}.yaml".format(api,cnf['ADVANTEDGEVER'])
        dstfn = "meep-{}-swagger.yaml".format(api)
        cmdstr = "sed \'s#<IP>#{}#;s#<SANDBOX>#{}#\' {} > {}" \
            .format(cnf['APIIP'],cnf['SANDBOX'],srcfn,dstfn)
        oscmd(cmdstr)
        # shutil.copy2(srcfn,dstfn)
        javastr = "java -jar files/swagger-codegen-cli.jar generate -i {} -l python -o ./{}-client/python -DpackageName={}".format(dstfn,api,pkg)
        pipstr = "pip install ./{}-client/python".format(api)
        deletestr = "rm -rf ./{}-client".format(api)
        cmdstr = "{} && {} && {}".format(javastr,pipstr,deletestr)
        cmdstr = "bash -c '{}'".format(cmdstr)
        oscmd(cmdstr)
    return 0

if __name__ == '__main__': main()

        