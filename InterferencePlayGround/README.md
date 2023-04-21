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
[Combo_Example](interference_profiles/Combo_Example.json)

