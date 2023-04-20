import sys
import os
print(sys.path)
from api_exec import job_execute

def api_handle(request):
    results = {}
    print(f"got api request {request.args}")
    

    zero = True if 'zero' in request.args else False 
    nlte = True if 'lte' in request.args else False
    n5g = True if '5g' in request.args else False
    rand = True if 'random' in request.args else False
    apigen = True if 'apigen' in request.args else False
    
    interference = True if 'interference' in request.args else False 
    lbo = True if 'lbo' in request.args else False
    scenario = request.args['scenario'] if 'scenario' in request.args else "horizon-filter-1"
    sandbox = request.args['sandbox'] if 'sandbox' in request.args else "horizon-filter-1"
    
    kwargs = locals()
    results = job_execute(**kwargs)
    # results =  {"RESPONSE": f"zero={zero} interference={interference} nlte={nlte} n5g={n5g} rand={rand}"}
    print(f"responding with {results}")
    return results

def main(): # For API Testing
    class InterferenceRequest(object):
        def __init__(self,**kwargs):
            self.args = kwargs
    req = InterferenceRequest(lte=True,lbo=True,scenario="horizon-filter-1",sandbox="horizon-filter-1")
    for ii in range(0,5):
        api_handle(req)
    pass
        
    
    
if __name__ == '__main__': main()    
    
