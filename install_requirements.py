#!/usr/bin/env python
import sys
import os

def oscmd(cmdstr): # Prints out to console and returns exit status
    return os.system(cmdstr)

''' Apt installs '''
INSTALL="default-jdk openjdk-8-jre jq influxdb-client webpack npm"
cmdstr = f"bash -c ' sudo apt update && sudo apt install -y {INSTALL}'"
oscmd(cmdstr)

pipsetup="pip install requests;pip install -r pip_requirements.txt"
setupclient="python lib/setupAutomation.py"
setupgdal = "lib/_installgdal.sh"
cmdstr = f"bash -c ' {pipsetup} && {setupgdal} && {setupclient}' "
oscmd(cmdstr)

''' K9s '''
setupk9s = "python lib/k9s_setup.py"
oscmd(setupk9s)

