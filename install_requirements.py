#!/usr/bin/env python
import sys
import os

def oscmd(cmdstr): # Prints out to console and returns exit status
    return os.system(cmdstr)
oscmd("sudo apt update")
''' Java '''
oscmd("sudo apt install default-jdk -y")
oscmd("sudo apt install openjdk-8-jre -y")
oscmd("sudo apt install -y jq influxdb-client webpack npm python3-pyqt5")

pipsetup="pip install requests;pip install -r pip_requirements.txt"
setupclient="python lib/setupAutomation.py"

cmdstr = f"bash -c ' {pipsetup} && {setupclient}' "
oscmd(cmdstr)

''' K9s '''
K9SURL = "wget https://github.com/derailed/k9s/releases/download/v0.27.3/"
K9SFN="k9s_Linux_amd64.tar.gz"
url = f"{K9SURL}/{K9SFN}"
oscmd(f'/bin/bash -c "wget {url}" && /bin/bash -c "tar xvzf {K9SFN} k9s" && sudo mv k9s /usr/local/bin/')

''' gdal '''
cmdstr = "lib/_installgdal.sh"
oscmd(cmdstr)

