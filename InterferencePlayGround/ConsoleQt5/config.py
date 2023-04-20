import os
import json
defconfig = {

}

configfile = __file__.replace(".py",".json")

def readConfig():
    fileconfig = None
    if os.path.isfile(configfile):
        with open(configfile,'r') as f:
            fileconfig = json.load(f)
    return fileconfig

def writeConfig(currentconfig):
    with open(configfile,'w') as f:
        json.dump(currentconfig,f,indent=4)

def initConfig():
    initconfig = defconfig.copy()
    fileconfig = readConfig()
    if fileconfig is not None:
        fullconfig = initconfig
        fullconfig.update(fileconfig)
    else:
        fullconfig = initconfig
        writeConfig(fullconfig)
    fullconfig = customConfig(fullconfig)
    return fullconfig

def customConfig(incnf):
    customconfig = {
    }
    incnf.update(customconfig)
    return incnf

def formatConfig():
    basecnf = initConfig()
    return []
# initConfig()
