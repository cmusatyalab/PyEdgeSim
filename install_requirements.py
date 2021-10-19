#!/usr/bin/env python
import sys
import os

def oscmd(cmdstr): # Prints out to console and returns exit status
    return os.system(cmdstr)
oscmd("sudo apt update")
''' Java '''
oscmd("sudo apt install default-jdk -y")
oscmd("sudo apt install openjdk-8-jre -y")
oscmd("sudo apt install -y jq influxdb-client webpack npm")
''' K9s '''
BREWPATH = "$HOME/.linuxbrew/bin"
oscmd('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
oscmd("{}/brew install k9s".format(BREWPATH))
oscmd("echo alias k9s=\'{}/k9s\' >> ~/.bashrc".format(BREWPATH))

pipsetup="pip install requests;pip install -r pip_requirements.txt"
setupclient="python lib/setupAutomation.py"

cmdstr = "bash -c ' {} && {}' ".format(pipsetup,setupclient)
oscmd(cmdstr)

cmdstr = "lib/_installgdal.sh"
oscmd(cmdstr)

''' K9s '''
BREWPATH = "$HOME/.linuxbrew/bin"
oscmd('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
oscmd("{}/brew install k9s".format(BREWPATH))
oscmd("echo alias k9s=\'{}/k9s\' >> ~/.bashrc".format(BREWPATH))

