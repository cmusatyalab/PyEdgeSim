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
#     'model1':{
#         'name': 'model1',
#         'application':'openrtist', 'initial_conditions': DEFINIT,
#         'exceptions':[
#         ],
#         'test_events': [
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m1-cloudlet','waitafter':modelwait},
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2b-3-cloudlet','waitafter':0},                
#             ],
#     },
#     'model2a-4':{
#         'name': 'model2a-4',
#         'application':'openrtist', 'initial_conditions': DEFINIT,
#         'exceptions':[
#         ],
#         'test_events': [
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2a-cloudlet','waitafter':modelwait},
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2b-3-cloudlet','waitafter':0},                
#             ],
#     },
#     'model2b':{
#         'name': 'model2b', 'application':'openrtist',
#         'initial_conditions': DEFINIT,
#         'exceptions':[
#         ],
#         'test_events': [
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2b-3-cloudlet','waitafter':modelwait},
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2b-3-cloudlet','waitafter':0},         
#             ],
#     },
#     'model3':{
#         'name': 'model3',
#         'application':'openrtist',
#         'initial_conditions': DEFINIT,
#         'exceptions':[
#         ],
#         'test_events': [
#                 {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':0,'latency':1},               
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2b-3-cloudlet','waitafter':modelwait},
#                 {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':0,'latency':5},                
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2b-3-cloudlet','waitafter':0},
#             ],
#     },
#     'allmodels':{
#         'name': 'allmodels',
#         'application':'openrtist',
#         'initial_conditions': DEFINIT,
#         'exceptions':[
#         ],
#         'test_events': [
# #                 {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o2','waitafter':0,'latency':50},
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m1-cloudlet','waitafter':60},
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2a-cloudlet','waitafter':defwait},  
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2b-3-cloudlet','waitafter':defwait},
#                 {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':0,'latency':1},                
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2b-3-cloudlet','waitafter':defwait},
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m1-cloudlet','waitafter':defwait},
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'m2b-3-cloudlet','waitafter':0},                
#             ], 
#     },
#     'cloudletmove':{
#         'name': 'cloudletmove',
#         'application':'openrtist',
#         'initial_conditions': DEFINIT,
#         'exceptions':[
#         ],
#         'test_events': [
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'near-cloudlet','waitafter':0},
#                 {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone2-o1','waitafter':0,'latency':3},
#
#                 {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':0,'latency':0}, # at the Tower (1+1=2)
#                 {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-poa1','waitafter':defwait,'latency':1},
#
#                 {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':0,'latency':3}, # At the RAN
#                 {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-poa1','waitafter':defwait,'latency':3},
#
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'far-cloudlet','waitafter':0}, # at the core    
#                 {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'zone1-o1','waitafter':0,'latency':3}, 
#                 {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'operator1','waitafter':defwait,'latency':3},
#
#                 {'type':'MOBILITY','mover':'openrtist-svc1','dest':'near-cloudlet','waitafter':0},                            
#             ], 
#     },
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
