#!/usr/bin/env python

import sys
import os
import pprint
import json
import shutil
from influxdb import InfluxDBClient
from influxdb import DataFrameClient

from pyutils import *
from simlogging import mconsole
from setupDeployment import stopDeployment,startDeployment

PORT=8086
FPORT=30086
DBNAME= "openrtistdb"

def setupInfluxDB(cnf):
    entry = input("Setup InfluxDB? [y/N] ") or "n"
    if entry in ['Y','y']:
        # conda install -c conda-forge influxdb; sudo apt install influxdb-client
        ''' Check openrtistdb influxdb '''
        exposeInfluxDB(cnf)
        client = InfluxDBClient(host=cnf['APIIP'], port=FPORT)
        dbs = getDBs(client)
        if dbs is not None and len(dbs) > 0 and DBNAME in dbs:
            ''' Check openrtistdb influxdb '''
            mconsole("Database {} exists in influxdb".format(DBNAME))
            # client.create_retention_policy('DefaultRetentionPolicy', '30d', "3", database = DBNAME, default=True)
        else:
            mconsole("Creating database {} in influxdb".format(DBNAME))
            client.create_database(DBNAME)
            client.alter_retention_policy("autogen", database=DBNAME, duration="30d", default=True)
            client.create_retention_policy('DefaultRetentionPolicy', '30d', "3", database = DBNAME, default=True)
            dbs = getDBs(client)
            if not DBNAME in dbs:
                mconsole("Could not create: {}".format(DBNAME),level="ERROR")
                return -1
        if dbs is not None and len(dbs) > 0 and cnf['INFLUXSCENDB'] in dbs:
            ''' Check scenario influxdb '''
            mconsole("Database {} exists in influxdb".format(cnf['INFLUXSCENDB']))
        else:
            mconsole("{} doesn't exist in meep-influxdb-0".format(cnf['INFLUXSCENDB']))
            # return -1         
    return 0

def exposeInfluxDB(cnf):
    settletime = 60
    fn = "files/meep-influxdb.yaml"
    nfn = os.path.join(os.environ['HOME'],".meep/user/values/meep-influxdb.yaml")
    mconsole("Exposing InfluxDB on port 30086; This may take a while")
    if not os.path.isfile(nfn):
        cmdstr = "sudo cp {} {}".format(fn,nfn)
        oscmd(cmdstr)
    ''' This step activates the exposure on a public IP address '''
    stopDeployment(cnf,settletime=settletime)
    startDeployment(cnf,settletime=settletime)
    # verify connection

def setupGrafana(cnf):
    entry = input("Setup Grafana? [y/N] ") or "n"
    if entry in ['Y','y']:    
        mconsole("Install grafana extensions")
        grafanapod = cmd0('kubectl get pod -l app.kubernetes.io/name=grafana -o jsonpath="{.items[0].metadata.name}"')
        grafanaurl="http://{}/grafana".format(cnf['APIIP'])
        chartname = "{}/grafana/{}".format(os.getcwd(),cnf['DASHBOARD'])
        krunpodstr = "kubectl exec {} -- ".format(grafanapod)
        oscmd("{}{}".format(krunpodstr,"grafana-cli plugins install grafana-worldmap-panel"))
        oscmd("{}{}".format(krunpodstr,"grafana-cli plugins install grafana-clock-panel"))
        oscmd("kubectl delete pod {}".format(grafanapod))
        mconsole("Navigate to {}, login (username: admin, pw: admin) \n\tand import '{}' ".format(grafanaurl, chartname))
        input("Press return to continue ")
    return 0

def getDBs(client):
    response = client.query("show databases")
    try:
        dbs = [db[0] for db in response.raw['series'][0]['values']]
        return dbs
    except:
        mconsole("Could not parse influxdb database list: {}".format(response),level="ERROR")
    return None

