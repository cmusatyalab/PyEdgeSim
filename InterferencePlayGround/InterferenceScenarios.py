''' Make this yamlable TODO '''

deflat=0
deflatv = 1
deftput = 10000
defpktl = 0
defwait = 10
modelwait = 5

''' Use these to construct a profile '''
EXCEPTIONTEMPLATE = {'name':'<ELEMENT>','latency':'<LATENCY>','latencyVariation':'<LATENCYVARIATION>',
                     'throughput':'<THROUGHPUT>','packetLoss':'<PACKETLOSS'}

INITCONDTEMPLATE = {'<NODETYPE>' : {'latency':'<LATENCY>','latencyVariation':'<LATENCYVARIATION>',
                     'throughput':'<THROUGHPUT>','packetLoss':'<PACKETLOSS>'}}

NETCHAREVENTTEMPLATE = {'type':'NETWORK-CHARACTERISTICS-UPDATE','name':'<ELEMENT>','waitafter':'<WAITAFTER>',
                        'latency':'<LATENCY>','latencyVariation':'<LATENCYVARIATION>','throughput':'<THROUGHPUT>','packetLoss':'<PACKETLOSS>'}

MOBILITYEVENTTEMPLATE = {'type':'MOBILITY','mover':'<MOVERELEMENT>','dest':'<DESTELEMENT>','waitafter':'<WAITAFTER>'}

DEFINIT = {
            'name': 'default',
            'application':'horizon',
            'duration':modelwait,
            'UE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'POA': {'latency':3,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'ZONE': {'latency':5,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'OPERATOR': {'latency':5,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'UE-APP': {'latency':0,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'EDGE-APP': {'latency':0,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'EDGE': {'latency':0,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'SCENARIO': {'latency':35,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
}

# TODO CONFIGURE THESE FOR ACTUAL MODEL
''' For this exercise, only POA matters '''
N4G_LTE_LBKOUT =  {
            'name': 'N4G_LTE_LBKOUT',
            'application':'horizon',
            'duration':modelwait,
            'UE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'POA': {'latency':25,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'ZONE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'OPERATOR': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'UE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'EDGE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'EDGE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'SCENARIO': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
}

N4G_LTE_REMOTEIXP =  {
            'name': 'N4G_LTE_REMOTEIXP',
            'application':'horizon',
            'duration':modelwait,
            'UE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'POA': {'latency':70,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'ZONE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'OPERATOR': {'latency':9,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'UE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'EDGE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'EDGE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'SCENARIO': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
}

N4G_LTE_LEL =  {
            'name': 'N4G_LTE_LEL',
            'application':'horizon',
            'duration':modelwait,
            'UE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'POA': {'latency':15,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'ZONE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'OPERATOR': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'UE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'EDGE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'EDGE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'SCENARIO': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
        }


N5G_CBRS_LBKOUT =  {
            'name': 'N5G_CBRS_LBKOUT',
            'application':'horizon',
            'duration':modelwait,
            'UE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'POA': {'latency':10,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'ZONE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'OPERATOR': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'UE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'EDGE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'EDGE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'SCENARIO': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
}

N5G_CBRS_REMOTEIXP =  {
            'name': 'N5G_CBRS_REMOTEIXP',
            'application':'horizon',
            'duration':modelwait,
            'UE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'POA': {'latency':60,'latencyVariation':deflatv,'throughput':deftput,'packetLoss':defpktl },
            'ZONE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'OPERATOR': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'UE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'EDGE-APP': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'EDGE': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
            'SCENARIO': {'latency':0,'latencyVariation':0,'throughput':deftput,'packetLoss':defpktl },
}

NETCONFIGS = [ N4G_LTE_LBKOUT, N4G_LTE_REMOTEIXP, N4G_LTE_LEL,N5G_CBRS_LBKOUT,N5G_CBRS_REMOTEIXP]

ZEROINIT =    {
            'name': 'zero',
            'application':'horizon',
            'duration':modelwait,
            'UE': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
            'POA': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
            'ZONE': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
            'OPERATOR': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
            'UE-APP': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
            'EDGE-APP': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
            'EDGE': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
            'SCENARIO': {'latency':0,'latencyVariation':0,'throughput':1000,'packetLoss':0 },
}

        