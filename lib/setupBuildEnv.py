#!/usr/bin/env python

import sys
import os
import pprint
import json
import shutil
sys.path.append("./lib")
from pyutils import *
from config import *
from simlogging import mconsole

cnf = initConfig()

nvmenvstr = 'export NVM_DIR=\"$HOME/.nvm\";[ -s \"$NVM_DIR/nvm.sh\" ] && \. \"$NVM_DIR/nvm.sh\";[ -s \"$NVM_DIR/bash_completion\" ] && \. \"$NVM_DIR/bash_completion\"'

def main():
    installGO(cnf)
    installNodeJS(cnf)
    installESLint(cnf)
    installGolangCILint(cnf)
    installMeepCTL(cnf)
    buildMeepAll(cnf)

def installGO(cnf):
    GOVER = cnf['GOVERSION']
    entry = input("Install GO? [y/N] ") or "n"
    if entry in ['Y','y']:
        tmpdir = cnf['TMPDIR'] if 'TMPDIR' in cnf else "/tmp"
        gofn = os.path.join(tmpdir,"go1.{}.linux-amd64.tar.gz".format(GOVER))
        oscmd("wget -P {} https://dl.google.com/go/go1.{}.linux-amd64.tar.gz".format(tmpdir,GOVER))
        if oscmd("sudo tar -C /usr/local -xzf {}".format(gofn)) == 0:
            os.remove(gofn)
        # oscmd("mkdir -p ~/gocode/bin")
        # gstr = "GOPATH"
        # if oscmd('grep "{}" ~/.bashrc'.format(gstr)) != 0:
        #     oscmd("echo export GOPATH=$HOME/gocode >>~/.bashrc")
        #     oscmd("echo 'export PATH=$PATH:$GOPATH/bin:/usr/local/go/bin' >>~/.bashrc")
        #     ''' Must run . ~/.bashrc before go will work '''
        setGOPATH()
    return 0

def setGOPATH():
    # hm = os.environ['HOME']
    # gobin = "{}/gocode/bin:{}/go/bin:/usr/local/go/bin".format(hm,hm)
    gobin = "{}/go/bin:/usr/local/go/bin".format(os.environ['HOME'])
    setPATH(gobin)



def installNodeJS(cnf):
    entry = input("Install NodeJS? [y/N] ") or "n"
    if entry in ['Y','y']:
        oscmd("sudo apt-get update ; sudo apt-get install -y nodejs-dev node-gyp libssl1.0-dev")
        oscmd("sudo apt-get update ; sudo apt-get install -y build-essential libssl-dev npm")
        tmpdir = cnf['TMPDIR'] if 'TMPDIR' in cnf else "/tmp"
        if 'NVM_DIR' in os.environ:
            os.environ.pop('NVM_DIR')
        jsfn = os.path.join(tmpdir,"install.sh")
        oscmd("curl -skL https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh -o {}".format(jsfn))
        if oscmd("bash {}".format(jsfn)) == 0:
            os.remove(jsfn)
        os.environ['NVM_DIR'] = os.path.join(os.environ['HOME'],".nvm")
        oscmd("bash -c '{};nvm install 10.16.3'".format(nvmenvstr))
        setNVMPATH()  
        oscmd("npm install -g npm")
        retlst = cmd("node -v;npm -v")
        mconsole("NodeJS Version: {} NPM Version: {}".format(retlst[0],retlst[1]) )
    return 0

def setNVMPATH():
    # /home/user/.nvm/versions/node/v10.16.3/bin/npm
    npmbin = "{}/.nvm/versions/node".format(os.environ['HOME'])
    npmbin = os.path.join(*[npmbin,os.listdir(npmbin)[0],"bin"])
    setPATH(npmbin)
    # os.environ['PATH'] = "{}:{}".format(os.environ['PATH'],npmbin)
         
def installESLint(cnf):
    entry = input("Install ESLint? [y/N] ") or "n"
    if entry in ['Y','y']:
        setNVMPATH()
        oscmd("bash -c 'npm install -g eslint@5.16.0'")
        oscmd("bash -c 'npm install -g eslint-plugin-react'")
    return 0

def installGolangCILint(cnf):
    entry = input("Install GolangCI-Lint? [y/N] ") or "n"
    if entry in ['Y','y']:
        setGOPATH()
        inststr = "cd ~;GO111MODULE=on go get github.com/golangci/golangci-lint/cmd/golangci-lint@v1.18.0"
        verstr = "go/bin/golangci-lint --version"
        cmdstr = "{};{}".format(inststr,verstr)
        oscmd('bash -c "{}"'.format(cmdstr))
    return 0

def installMeepCTL(cnf):
    entry = input("Install MeepCTL? [y/N] ") or "n"
    if entry in ['Y','y']:
        setGOPATH()
        addn = cnf['ADVANTEDGEDIR']
        cmdstr = "cd {}/go-apps/meepctl;./install.sh".format(addn)
        oscmd('bash -c "{}"'.format(cmdstr))
        nodeip = cmd0("kubectl get nodes -o json|jq -r '.items[].status.addresses[] | select( .type | test(\"InternalIP\")) | .address'")
        setMEEPPATH(addn)        
        oscmd("meepctl config ip {};meepctl config gitdir {};meepctl config".format(nodeip,addn))
    return 0

def setMEEPPATH(hpath):
    meepbin = os.path.join(*[hpath,"bin","meepctl"])
    setPATH(meepbin)
    return meepbin
    
def buildMeepAll(cnf):
    entry = input("Build Meep microservices? [y/N] ") or "n"
    if entry in ['Y','y']:
        oscmd("which npm")
        setMEEPPATH(cnf['ADVANTEDGEDIR'])
        pthstr = "export PATH=$PATH:/usr/local/go/bin:~/go/bin"
        meepctl = os.path.join(*[cnf['ADVANTEDGEDIR'],"bin","meepctl","meepctl"])
        if oscmd("bash -c '{};{} build all --nolint'".format(pthstr,meepctl)) != 0: return -1
    return 0
# Utilities
def setPATH(npath,setrc = True):
    if npath not in os.environ['PATH']: os.environ['PATH'] = "{}:{}".format(npath,os.environ['PATH'])
    if setrc: setBashRC(npath)
        
def setBashRC(npath):
    oscmd('bash -c "grep \'{}\' ~/.bashrc || echo \'export PATH={}:\$PATH:\' >> ~/.bashrc"'.format(npath,npath))

#
if __name__ == '__main__': main()
