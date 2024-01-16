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
K9SURL = "wget https://github.com/derailed/k9s/releases/download/v0.27.3/"
K9SFN="k9s_Linux_amd64.tar.gz"
url = f"{K9SURL}/{K9SFN}"
oscmd(f'/bin/bash -c "wget {url}" && /bin/bash -c "tar xvzf {K9SFN} k9s" && sudo mv k9s /usr/local/bin/')

