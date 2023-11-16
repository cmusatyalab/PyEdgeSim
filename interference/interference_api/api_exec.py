import sys
devnull = [print(line) for line in sys.path]
import os
from types import SimpleNamespace
from pyutils import *

HOME=os.environ['HOME'] if 'HOME' in os.environ else "/home/jblake1"  
ROOT_DIR=f"{HOME}/CMUProjects/LEL/EdgeVDI"
INT_GEN=f"{ROOT_DIR}/interference_run_random.py"
INT_PROF=f"{ROOT_DIR}/interference_profiles"
USER="ubuntu"

def main():
    print(f'INT_GEN exists: {os.path.exists(INT_GEN)}')
    print(f'INT_PROF exists: {os.path.exists(INT_PROF)}')
    interference = False
    lbo = False
    zero = False
    nlte = False
    n5g = False
    rand = False
    apigen = True
    sandbox = 'horizon-filter-2'
    scenario = 'horizon-filter-2'
    kwargs = locals()
    job_execute(**kwargs)
    pass

def job_execute(**kwargs):  
    result = ""
    print(kwargs)
    k = SimpleNamespace(**kwargs)
    cmdstr = f"bash -c \'cd {ROOT_DIR} ; python {INT_GEN} "
    cmdstr += addEnvironment(k)
    
    profile = setProfile(k)
    result += stopRun(k) # Stop existing profile runs 
    
    print(cmdstr)
    try:
        if k.zero:
            result += f"Running zero; interference and local-breakout are ignored"
            cmdstr += " -Z \'"
            cmd_subp(cmdstr)
        elif k.n5g:
            result += f"Running 5g; interference={k.interference}; local-breakout={k.lbo}"
            if profile is not None:
                cmdstr += f" -f {profile} \'"
                cmd_subp(cmdstr)
        elif k.nlte:
            result += f"Running LTE; interference={k.interference}; local-breakout={k.lbo}"
            if profile is not None:
                cmdstr += f" -f {profile} \'"
                cmd_subp(cmdstr)
        elif k.rand:
            result += f"Running random; interference and local-breakout are ignored"
            cmdstr += "\'"
            cmd_subp(cmdstr)
        elif k.apigen:
            result += f"(Re)generating AdvantEDGE APIs for sandbox={k.sandbox} scenario={k.scenario}"
            cmdstr += " -A \'"
            cmd_subp(cmdstr)
        else:
            pass
    except Exception as e:
        print(f"Bad variable: {e}")
    print(result)
    return result


NLTE_LBO="N4G_LTE_LBKOUT_V00.json"
NLTE_IXP="N4G_LTE_REMOTEIXP_V00.json"
NLTE_LBO_INT="N4G_LTE_LBKOUT_V00_BadSignal_V00.json"
NLTE_IXP_INT="N4G_LTE_REMOTEIXP_V00_BadSignal_V02.json"

N5G_LBO="N5G_CBRS_LBKOUT_V00.json"
N5G_IXP="N5G_CBRS_REMOTEIXP_V00.json"
N5G_LBO_INT="N5G_CBRS_LBKOUT_V00_BadSignal_V00.json"
N5G_IXP_INT="N5G_CBRS_REMOTEIXP_V00_BadSignal_V02.json"

def setProfile(k):
    profile = None
    if k.interference:
        if k.nlte: profile = NLTE_LBO_INT if k.lbo else NLTE_IXP_INT
        elif k.n5g: profile = N5G_LBO_INT if k.lbo else N5G_IXP_INT
    else:
        if k.nlte: profile = NLTE_LBO if k.lbo else NLTE_IXP
        elif k.n5g: profile = N5G_LBO if k.lbo else N5G_IXP
        
    print(profile)
    profile = os.path.join(INT_PROF,profile) if profile is not None else None
    return profile

def addEnvironment(k):
    return f" --sandbox={k.sandbox} --scenario={k.scenario} "

from operator import itemgetter
def stopRun(k):
    cmdstr = f"bash -c \'USER={USER};ps -ax|grep {INT_GEN}\'"
    cmdres = cmd_all(cmdstr)
    if len(cmdres['stdout']) > 3:
        pids = " ".join(list(map(itemgetter(0), \
                    [line.split() for line in cmdres['stdout'] if len(line) > 0])))
        cmdstr = f"bash -c \'USER={USER};kill -9 {pids}'"
        cmd_all(cmdstr)
        return "Running jobs stopped; "
    return ""
    
if __name__ == '__main__': main()    