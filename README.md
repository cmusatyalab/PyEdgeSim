# PyEdgeSim

## Introduction

https://github.com/InterDigitalInc/AdvantEDGE
https://github.com/InterDigitalInc/AdvantEDGE/wiki

http://reports-archive.adm.cs.cmu.edu/anon/2020/CMU-CS-20-135.pdf

## Prerequisites

Linux server VM or bare metal

Android Client

## Tested on

### Server

- Ubuntu 18.04
- Azure Stack Standard DS5 v2 (16 vcpus, 56 GB memory) instance with 64GB SSD
- Python 3.6
- Docker
- XFCE desktop via TightVNC
- Chrome Browser
- AdvantEDGE 1.7.1

### Client

- Samsung Galaxy S8 with Android 9
- Essential PH-1 with Android 10

## Exercise 1: Configure the Platform

### Server Setup

Install docker and configure $USER as a docker user. Then, reboot.

Install java:

```
> sudo apt update
> sudo apt install default-jdk -y
> sudo apt install openjdk-8-jre -y
```

Open firewall ports 80 (HTTP), 443 (HTTPS), 22 (SSH), 30086 (InfluxDB) and 31001 (OpenRTiST)

Clone the repository and install the required packages

```
> git clone https://github.com/jblakley/PyEdgeSim
> cd PyEdgeSim
> python install_requirements.py
```

When prompted to <u>select the Linuxbrew installation directory</u>, enter ^D then return.

When prompted to set up automation, select "y".

PyEdgeSim configuration details are in `config.json`. You won't need to play with most of these but set the project directory, `PROJECTHOME` to your preferred (usually `$HOME`) and the `PUBLICIP` to the public IP of your server.

Now, its time to set up the simulation. Execute:

`./simulation_setup.py`

This script will walk you through several steps. Each step is as automated as possible so user interaction is minimized. If any step fails, you can usually restart from that point forward by skipping the steps you have already completed. The steps are:

1. Set up the AdvantEDGE runtime environment. This step installs and configures Kubernetes, Helm and AdvantEDGE. It is an automation of directions [here](https://github.com/InterDigitalInc/AdvantEDGE/wiki/env-runtime).
2. Set up the AdvantEDGE build environment. This step installs and configures go, nodejs with nvm & npm,  ESLint, GolangCI-Lint, meepctl and the meep microservices. It is an automation of the directions [here](https://github.com/InterDigitalInc/AdvantEDGE/wiki/env-dev) and [here](https://github.com/InterDigitalInc/AdvantEDGE/wiki/mgmt-workflow).
3. Deploy AdvantEDGE. This step deploys the meep dependencies services then dockerizes and deploys the meep core services.  It is an automation of the directions [here](https://github.com/InterDigitalInc/AdvantEDGE/wiki/mgmt-workflow).

At this point, AdvantEDGE should be running. You can check this by running `k9s` or opening a browser window to `127.0.0.1`. If you start a new bash shell, your `.bashrc` should be configured for `kubectl`, `meepctl`, `go`, `npm` and `nvm`. To verify, run:

```
> kubectl version; meepctl version; go version; npm version; node -v;  nvm --version
```

The script now continues to:

4. Download the docker image for the `OpenRTiST` server and push it into the local repository.
5. Copy the simulation scenario charts into AdvantEDGE.

At this point, before deploying the scenario, some manual effort is required outside of the script.

6. Open a browser window to `127.0.0.1` to connect to the AdvantEDGE console.
7. Select the *CONFIGURE* tab and  import `adv-ortist-sim.yaml` from the PyEdgeSim `data/scenarios` directory. Save the scenario with the name `adv-ortist-sim`.
8. Select the *EXECUTE* tab and create a new sandbox named `adv-ortist-sim`. Wait for the sandbox to be created (*watch the red stoplight turn green*). Now,  deploy the `adv-ortist-sim` scenario. If this is successful, you will see two network elements, `openrtist-client1` and `openrtist-svc1` at the bottom of the *EXECUTE* page. You will also see these two pods when running a `kubectl get pods` command or by looking in `k9s`.

You can now continue the `simulation_setup.py` script.

9. Stop and restart the scenario. This also tests that the automation tools are working properly.
10. Set up the data management elements, influxdb and grafana. 
    - To expose influxdb outside of the server cluster, this step stops the `adv-ortist-sim` scenario, deletes the sandbox and restarts AdvantEDGE. The process will take some time. You can validate that it worked by going to another machine with influxdb installed and running `influx -port 30086 -host <PUBLICIP-OF-SERVER>`. If it can't connect, make sure you opened port 30086 on your server.
    - From the browser, recreate your `adv-ortist-sim` sandbox and redeploy the `adv-ortist-sim` scenario.
    - From the script, setup grafana. 
    - Then, open a browser tab to `http://127.0.0.1/grafana`, login at lower left with username = admin and pw = admin. Use the `+` to import the `Client Framerate and Round Trip Time.json` dashboard from the PyEdgeSim `data/grafana` directory. When the dashboard opens, select `adv_ortist_sim_adv_ortist_sim` from the `ScenarioDB` dropdown menu at the top of the dashboard.
11. The script will prompt you to setup automation. This was already done during the installation requirements but no harm in doing it again to be safe.
12. Run the test automation. You can view the progress from the grafana dashboard. You'll see a network latency step graph in the lower left. Since you have not yet configured the client, you won't see anything meaningful in the upper half of the dashboard. 

The final step in the script is the generation of a test report. We'll come back to this after the client is configured. You've completed the server configuration. For now, you can exit from the `simulation_setup.py` script.

### Client Setup

1. On your android client device, download and install the instrumented OpenRTiST client from [here](http://visualcloudsystems.org/cmudl/app-measurementDB-debug.apk).
2. When the OpenRTiST client opens, approve permission requests as prompted. These enable the client to collect measurements from the device. 
3. On the OpenRTiST client Server List, create a new server using an address of `<YOUR-SERVER-PUBLIC-IP>:31001`. Open that server and approve any other requested permissions. You should now be connected to the OpenRTiST server and can display the artistic style of your choice from the drop down. If you can't connect, check that port 31001 is open on your server.



## Exercise 2: Running the Simulation

With both the client and server running, connected and displaying style transfer, rerun the test automation by skipping through the prior steps in `simulation_setup.py`.  For some reason, it can take a while (10-15 minutes) for influxdb measurements from openrtist to appear in the openrtistdb that grafana draws from. If you don't see them in the upper part of the dashboard, try rerunning the simulation a few times until you see them.

Once you get a complete run with both the lower and upper dashboard showing data, create the test report to see that everything is working. The report is written to a file called `report.png`. It should look something like this.

![](C:\Users\jimbl\Downloads\report.png)

