# Using the Interference Generator
## Generating new profiles

In `InterferenceScenarios.py` create your baseline network configuration. For example, the following models a 4G LTE network with local breakout to the cloudlet:

```
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
```

Configure any options in `interference_generator.py` *(TODO: Make command line options)*


```
VARIANTS= 5
LATRANGE = range(50,400)
```


Run the following to create multiple profile variants of normal, bad signal, load, and a combo of bad signal and load.

No options required

```
> python interference_generator.py

```

You can, of course, edit the generated profiles by hand to tweak paramters and steps. As with editing any complex json file, this can be error prone.


## Playing profiles

```
$ python ./interference_run_random.py -h
Usage: interference_run_random.py [options]

Options:
  -h, --help            show this help message and exit
  -g, --generate        Generate fresh profiles before running
  -r, --restart         Restart the AdvantEDGE scenario before running
                        profiles
  -A, --api-generate    Regenerate API client bindings and exit
  -z, --zero-between    Run the zero profile between other profiles (TODO)
  -f <filename>, --profilefilename=<filename>
                        Specify a specific interference profile to run
  -N, --normal          Run only normal profiles
  -L, --load            Run only loaded profiles
  -C, --combo           Run only combination profiles
  -B, --badsignal       Run only bad signal profiles
  -Z, --zero            Run the zero profile
  -T STRING, --testerid=STRING
                        Give testerid
  -s STRING, --sandbox=STRING
                        Give the sandbox name (DEFAULT = horizon-filter-1)
  -S STRING, --scenario=STRING
                        Give the scenario name (DEFAULT = horizon-filter-1)
  -i STRING, --apiip=STRING
                        Give the IP for the api server (DEFAULT = 127.0.0.1)
  -V STRING, --advantedgever=STRING
                        Give the AdvantEDGE Version (DEFAULT = 1.8.0)
  -p STRING, --profile=STRING
                        NOT TESTED
  -t STRING, --test=STRING
                        NOT TESTED
  -R STRING, --fileroot=STRING
                        TODO
  -d <Normal, Pareto, Paretonormal, Uniform>, --distribution=<Normal, Pareto, Paretonormal, Uniform>
                        Set distribution for latency
```

### Cheatsheet

To set all latency, jitter, throughput back to zero:

```
python interference_run_random.py -Z
```

To run a random series of profiles in series:

```
python interference_run_random.py
```

To run a specific profile:

```
python interference_run_random.py -f interference_profiles/N4G_LTE_LBKOUT_V00_BadSignal_V00.json
```

To run a random series of badsignal profiles in series:

```
python interference_run_random.py -B
```

## The interference console

1. Install the flask application on the AdvantEDGE host

```
mkdir ~/flask
cp -pvr interference_api/* ~/flask
cd ~/flask
pip install -r requirements.txt
```
2. Run the flask server

```
./flask.sh
```

3. Start the GUI on the client

```
cd <path-to-interference-generator>/ConsoleQt5
python console_GUI.py
```

## APPENDIX 1: Example Profile
A complete example "combo" profile for a 4G LTE network with local breakout experience varying latency, jitter, packet loss and load.



```
{
    "name": "N4G_LTE_LBKOUT_V00_Combo_V00",
    "application": "edgevdi",
    "latencyDistribution": "Normal",
    "initial_conditions": {
        "name": "N4G_LTE_LBKOUT",
        "application": "horizon",
        "duration": 61,
        "UE": {
            "latency": 0,
            "latencyVariation": 0,
            "throughput": 10000,
            "packetLoss": 0
        },
        "POA": {
            "latency": 25,
            "latencyVariation": 1,
            "throughput": 10000,
            "packetLoss": 0
        },
        "ZONE": {
            "latency": 0,
            "latencyVariation": 0,
            "throughput": 10000,
            "packetLoss": 0
        },
        "OPERATOR": {
            "latency": 0,
            "latencyVariation": 0,
            "throughput": 10000,
            "packetLoss": 0
        },
        "UE-APP": {
            "latency": 0,
            "latencyVariation": 0,
            "throughput": 10000,
            "packetLoss": 0
        },
        "EDGE-APP": {
            "latency": 0,
            "latencyVariation": 0,
            "throughput": 10000,
            "packetLoss": 0
        },
        "EDGE": {
            "latency": 0,
            "latencyVariation": 0,
            "throughput": 10000,
            "packetLoss": 0
        },
        "SCENARIO": {
            "latency": 0,
            "latencyVariation": 0,
            "throughput": 10000,
            "packetLoss": 0
        }
    },
    "exceptions": [],
    "test_events": [
        {
            "mover": "iperf-ue1-50k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-100k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-200k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-400k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-800k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-1600k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "latency": 145,
            "type": "NETWORK-CHARACTERISTICS-UPDATE",
            "name": "horizon-cloudlet",
            "waitafter": 3,
            "latencyVariation": 33,
            "packetLoss": 11
        },
        {
            "mover": "iperf-ue1-50k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-100k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-200k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-400k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-800k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-1600k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "latency": 122,
            "type": "NETWORK-CHARACTERISTICS-UPDATE",
            "name": "horizon-cloudlet",
            "waitafter": 9,
            "latencyVariation": 7,
            "packetLoss": 18
        },
        {
            "mover": "iperf-ue1-50k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-100k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-200k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-400k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-800k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-1600k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "latency": 190,
            "type": "NETWORK-CHARACTERISTICS-UPDATE",
            "name": "horizon-cloudlet",
            "waitafter": 2,
            "latencyVariation": 39,
            "packetLoss": 5
        },
        {
            "mover": "iperf-ue1-50k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-100k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-200k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-400k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-800k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-1600k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "latency": 170,
            "type": "NETWORK-CHARACTERISTICS-UPDATE",
            "name": "horizon-cloudlet",
            "waitafter": 1,
            "latencyVariation": 8,
            "packetLoss": 5
        },
        {
            "mover": "iperf-ue1-50k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-100k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-200k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-400k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-800k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-1600k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "latency": 131,
            "type": "NETWORK-CHARACTERISTICS-UPDATE",
            "name": "horizon-cloudlet",
            "waitafter": 7,
            "latencyVariation": 8,
            "packetLoss": 10
        },
        {
            "mover": "iperf-ue1-50k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-100k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-200k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-400k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-800k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-1600k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "latency": 69,
            "type": "NETWORK-CHARACTERISTICS-UPDATE",
            "name": "horizon-cloudlet",
            "waitafter": 3,
            "latencyVariation": 16,
            "packetLoss": 5
        },
        {
            "mover": "iperf-ue1-50k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-100k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-200k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-400k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-800k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-1600k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "latency": 97,
            "type": "NETWORK-CHARACTERISTICS-UPDATE",
            "name": "horizon-cloudlet",
            "waitafter": 1,
            "latencyVariation": 46,
            "packetLoss": 18
        },
        {
            "mover": "iperf-ue1-50k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-100k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-200k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-400k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-800k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-1600k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "latency": 124,
            "type": "NETWORK-CHARACTERISTICS-UPDATE",
            "name": "horizon-cloudlet",
            "waitafter": 2,
            "latencyVariation": 22,
            "packetLoss": 13
        },
        {
            "mover": "iperf-ue1-50k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "zone1-poa1"
        },
        {
            "mover": "iperf-ue1-100k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-200k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-400k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-800k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-1600k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "latency": 123,
            "type": "NETWORK-CHARACTERISTICS-UPDATE",
            "name": "horizon-cloudlet",
            "waitafter": 6,
            "latencyVariation": 47,
            "packetLoss": 10
        },
        {
            "mover": "iperf-ue1-50k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-100k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-200k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-400k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-800k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        },
        {
            "mover": "iperf-ue1-1600k",
            "waitafter": 0,
            "type": "MOBILITY",
            "dest": "DISCONNECTED"
        }
    ]
}
```
