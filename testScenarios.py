''' Make this yamlable TODO '''
deflat=0
deflatv = 0
deftput = 10000
defpktl = 0
defwait = 15
modelwait = 30
DEFINIT = {
            'UE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'POA': {'latency':3,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'ZONE': {'latency':5,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'OPERATOR': {'latency':5,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'UE-APP': {'latency':0,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'EDGE-APP': {'latency':0,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'SCENARIO': {'latency':35,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
        }
testprofiledict = {
    'latencystep':{
        'name': 'latencystep',
        'application':'openrtist',
        'initial_conditions': {
            'UE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'POA': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'ZONE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'OPERATOR': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'UE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'EDGE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'SCENARIO': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
        },
        'exceptions':[
        ],
        'test_events': [
                {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':defwait,'latency':5},
                {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':defwait,'latency':10},
                {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':defwait,'latency':15},
                {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':defwait,'latency':20},
                {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':defwait,'latency':25},
                {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':defwait,'latency':30},
                {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':defwait,'latency':35},
                {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':defwait,'latency':40},
                {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':defwait,'latency':45},
                {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':defwait,'latency':50},                
                {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':0,'latency':0},
                {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2b-3-cloudlet','waitafter':0},                
            ],
         
         
    },    
    'walnut1':{
        'name': 'walnut1',
        'application':'openrtist',
        'initial_conditions': {
            'UE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'POA': {'latency':3,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'ZONE': {'latency':5,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'OPERATOR': {'latency':5,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'UE-APP': {'latency':0,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'EDGE-APP': {'latency':0,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'SCENARIO': {'latency':0,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
        },
        'exceptions':[
        ],
        'test_events': [
        ],
         
    },    
    'zero':{
            'name': 'zero',
            'application':'openrtist',
            'initial_conditions': {
                'UE': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
                'POA': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
                'ZONE': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
                'OPERATOR': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
                'UE-APP': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
                'EDGE-APP': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
                'SCENARIO': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
            },
            'exceptions':[],
            'test_events':[
                {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2b-3-cloudlet','waitafter':0},
            ]
        },
    }
