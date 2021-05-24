#!/usr/bin/env python
# coding: utf-8
import os
import sys
import re
import datetime
from datetime import timedelta
import pandas as pd
import requests
from simlogging import mconsole

from influxdb import InfluxDBClient
from influxdb import DataFrameClient

from pyutils import *
from pdutils import *
from pdpltutils import *
from gputils import *
from mathutils import *
from iputils import *

IP2LITE="IP2LOCATION-LITE-DB5.CSV"

def createReport(cnf,filename=None):
  
    ORTISTIP = cnf['APIIP']
    ORPORT=30086
    ORDBNAME= "openrtistdb"
    dclient = InfluxDBClient(host=ORTISTIP, port=ORPORT, database=ORDBNAME)
    dpdclient = DataFrameClient(host=ORTISTIP, port=ORPORT, database=ORDBNAME)

    # SCENIP = cmd0("kubectl get pods -o json|jq -r '.items[] | select( .metadata.name | test(\"influxdb\")) | .status.podIP'")
    # SCPORT=8086
    SCENIP = ORTISTIP
    SCPORT = ORPORT
    SCDBNAME=cnf['INFLUXSCENDB']
    sclient = InfluxDBClient(host=SCENIP, port=SCPORT, database=SCDBNAME)
    spdclient = DataFrameClient(host=SCENIP, port=SCPORT, database=SCDBNAME)

    ''' Get the session data of most recent session '''
    ''' Openrist Data '''
    try:
        allmeasdf =  convTS(dpdclient.query("select * from allmeasure")['allmeasure']).sort_values('TIMESTAMP')
    except KeyError:
        mconsole("Can't create report; No measurements in OpenRTistDB", level="ERROR")
        return -1
        
    sessid = allmeasdf.SESSIONID.iloc[-1]
    mconsole("Latest session ID is {}".format(sessid))
    
    sessmeasdf = allmeasdf[allmeasdf.SESSIONID == sessid].copy()
    firstts = sessmeasdf.TIMESTAMP.iloc[0]
#     dumpdf(sessmeasdf)
    qq = "select * from traceroute where SESSIONID = '%s'" % sessid
    trtedf = convTS(dpdclient.query(qq)['traceroute'])
    
    ''' AdvantEDGE Data '''
    qq = "select * from network"
    netdf = convTS(spdclient.query(qq)['network']).sort_values('TIMESTAMP')
    netdf = netdf[netdf.TIMESTAMP >= firstts] # Select for session
    
    qq = "select * from events"
    evdf = convTS(spdclient.query(qq)['events']).sort_values('TIMESTAMP')
    evdf = evdf[evdf.TIMESTAMP >= firstts] # Select for session
    
    ''' Now bracket the dataset by the first and last events '''
    if len(evdf) > 0:
        first_ts = evdf.iloc[0]['TIMESTAMP']
        last_ts = evdf.iloc[-1]['TIMESTAMP']
    else:
        ''' Whole session '''
        first_ts = sessmeasdf.iloc[0]['TIMESTAMP']
        last_ts = sessmeasdf.iloc[-1]['TIMESTAMP']
    
    mconsole("Session starts at {} and ends at {}".format(first_ts,last_ts))
    sessmeasdf = sessmeasdf[(sessmeasdf.TIMESTAMP >= first_ts) & (sessmeasdf.TIMESTAMP <= last_ts)]
    netdf = netdf[(netdf.TIMESTAMP >= first_ts) & (netdf.TIMESTAMP <= last_ts)]
    evdf = evdf[(evdf.TIMESTAMP >= first_ts) & (evdf.TIMESTAMP <= last_ts)]
    trtedf2 = parseTraceRoute(cnf,trtedf)
    ''' Prepare the report '''
    createPlots(sessmeasdf,trtedf2,netdf,evdf, cnf,filename=filename)

    return 0

def createPlots(measdf,trdf, netdf, evdf, cnf,  filename = None):
    fig,axs = plt.subplots(ncols=2,nrows=3,figsize=(20,20))
    fig.suptitle("AdvantEDGE OpenRTiST Simulation Report",fontsize=20)
    ax = axs[0][0]
    ax = ts_lineplot(measdf,['INTERVALRTT'],ylabel = "Round Trip Time (ms)",xlabel='Time',
                     title="OpenRTiST Round Trip Time", legend = None, ax=ax)
    ax.set_xticklabels([])
    
    ax = axs[0][1]
    ax = ts_lineplot(measdf,['INTERVALFPS'],ylabel = "Frames Per Second",xlabel='Time',
                     title="OpenRTiST Frames per Second",legend = None, ax=ax)
    ax.set_xticklabels([])
    
    ax = axs[1][0]
    ax = histplot(measdf.INTERVALRTT, bins=50, title="", ylabel="Round Trip Time",saveon=False, density=True,
         ax=ax,legend=None,tabon=False, xlabel='Round Trip Time (ms)')
    ax.set_yticklabels([])
    
    ax = axs[1][1]
    ax = histplot(measdf.INTERVALFPS, bins=50, title="" ,saveon=False, density=True,
         ax=ax,legend=None,tabon=False, xlabel='Frames Per Seconds')
    ax.set_yticklabels([])
    
    ax = axs[2][1]
    ax = ts_lineplot(netdf,['ul'],ylabel = "Network Latency",xlabel='Time',legend = None, ax=ax)
    ax.set_xticklabels([])
    ax.set_title("AdvantEDGE Network Latency",fontsize=14)
    
    ax = axs[2][0]
    ax = plotTraceRoute(trdf,cnf,ax=ax)
#     ax.set_title("Trace Route Path",y=1.0,pad=-30,fontsize=14,color='red')
    ax.set_title("Trace Route Path",fontsize=14)
    
    plt.tight_layout()
    if filename is not None:
        fig.savefig(filename)
    return fig
    
def parseTraceRoute(cnf,trtedf):
    global ipdbdf
    ipdbdf = getIP2LITE(cnf)
    fdfx = trtedf.copy()
    ''' Melt the Data '''
    id_vars = [col for col in fdfx.columns if not col.startswith('IP')]
    value_vars = [col for col in fdfx.columns if col.startswith('IPVAL')]
    fdfx = drp_lst(pd.melt(fdfx,id_vars=id_vars,value_vars=value_vars,var_name='IPPOS',value_name='IPNO')         .sort_values(['TIMESTAMP','IPPOS']).reset_index(),['index'])
    fdfx['IPADD'] = fdfx['IPNO'].map(ipno2ipadd)
    # dumpdf(fdfx)

    ''' Join with location database '''
    fdfx = fdfx.apply(addLoc, axis=1).set_index('TIMESTAMP')
    # dumpdf(fdfx)
    # dumpdf(fdfx[['IPADD','city_name','region_name']].dropna())
    return fdfx

def getIP2LITE(cnf):
    IP2LITE="IP2LOCATION-LITE-DB5.CSV"
    ffn = os.path.join(*[cnf['PROJECTHOME'],"Downloads",IP2LITE])
    if not os.path.isfile(ffn):
        fetchIP2LITE(ffn)
    if os.path.isfile(ffn):
        tdfx = pd.read_csv(ffn)
        collst=['ip_from','ip_to','country_code','country_name','region_name','city_name','latitude','longitude']
        tdfx.columns = collst
        retdf = tdfx.copy().reset_index()
    else:
        mconsole("{} file not available".format(IP2LITE),level="ERROR")
        return None
    return retdf

def fetchIP2LITE(destination):
    URL = "https://docs.google.com/uc?export=download"
    id = "1B-u99usa59ZmlMLSBDfvITn9iXoGD48l"
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None
    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
    
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    session = requests.Session()
    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)
    save_response_content(response, destination)

def matchIPNO(ipno):
    fdfx = ipdbdf[(ipdbdf.ip_from <= ipno) & (ipdbdf.ip_to >= ipno) & (ipdbdf.latitude != 0)]
    rowind = fdfx['index']
    if rowind.size > 0:
        return rowind.iloc[0]
    return -1

def addLoc(row):
    indno = matchIPNO(row.IPNO)
    if indno >= 0:
        nrow = ipdbdf.iloc[indno]
        row = row.append(nrow)
    return row

def plotTraceRoute(trdf,cnf,ax=None):
    ctxprovider=ctx.sources.ST_TONER_LITE
    tdfx = trdf.copy().dropna()
    tdfx['geometry'] = pt2geom(tdfx,latcol='latitude',lngcol='longitude')
    tdfx['geometryshift'] = tdfx['geometry'].shift(-1)
    tdfx['geometryshift'].iloc[-1] = tdfx['geometry'].iloc[0] # Make it around trip
    tgp = df2gp(tdfx)
    
    tgp = tgp.dropna()
    tgp['LINEGEO'] = tgp.apply(pts2ls, axis = 1)
    # dumpdf(tgp.head(1))
    
    uscorners = [[48.783560,-124.608168],[47.179016,-68.720687],[25.211685,-80.615475],[25.895913,-97.446996]]
    usdf = pd.DataFrame(uscorners,columns=['LAT','LONG'])
    usdf['geometry'] = pt2geom(usdf)
    usgp = df2gp(usdf)
    
    ax= gp_plotPoints(usgp,mapon=True,figsize=(20,20),alpha=0.01,ax=ax)
    ax= gp_plotPoints(tgp,mapon=True,c='red',figsize=(20,20),s=200,ax=ax)
    ax= gp_plotPoints(tgp.tail(1),mapon=True,c='blue',figsize=(20,20),ax=ax,s=1000,marker="*")
    ax = gp_plotLines(tgp,mapon=True,geocol='LINEGEO',ax=ax,color='green',ctxprovider=ctxprovider)
    return ax


def convTS(fdf):
    fdf = renamecol(fdf.reset_index(),col='index',newname='TIMESTAMP')
    fdf['TIMESTAMP'] = fdf['TIMESTAMP'].map(lambda cell: cell.replace(microsecond=0))
    return fdf

def gp_Points2Lines(fgp):
    fgp['geometryshift'] = fgp['geometry'].shift(-1)
    fgp = fgp.dropna()
    retser = fgp.apply(pts2ls, axis = 1)
    return retser
def pts2ls(row):
#     print(row)
    ls = LineString([row['geometry'],row['geometryshift']])
    return ls

