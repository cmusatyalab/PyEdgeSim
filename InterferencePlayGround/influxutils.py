import pandas

from pdutils import *

from influxdb import InfluxDBClient,DataFrameClient

# import simlogging
from simlogging import mconsole
''' Influx DB '''
''' Influxdb Config '''

def convTS(fdf,tz = None):
    fdf = renamecol(fdf.reset_index(),col='index',newname='TIMESTAMP')
    fdf['TIMESTAMP'] = fdf['TIMESTAMP'].map(lambda cell: cell.replace(microsecond=0))
    if tz is not None: fdf = changeTZ(fdf,newtz = tz)
    return fdf

def getDBs(client):
    response = client.query("show databases")
    try:
        dbs = [db[0] for db in response.raw['series'][0]['values']]
        return dbs
    except:
        mconsole("Could not parse influxdb database list: {}".format(response),level="ERROR")
    return None

def createDB(client,dbname):
    dbs = getDBs(client)
    if dbs is not None and len(dbs) > 0 and dbname in dbs:
        ''' Check openrtistdb influxdb '''
        mconsole("Database {} exists in influxdb".format(dbname))
    else:
        mconsole("Creating database {} in influxdb".format(dbname))
        client.create_database(dbname)
        client.alter_retention_policy("autogen", database=dbname, duration="30d", default=True)
        client.create_retention_policy('DefaultRetentionPolicy', '30d', "3", database = dbname, default=True)
        dbs = getDBs(client)
        if not dbname in dbs:
            mconsole("Could not create: {}".format(DBNAME),level="ERROR")
            return -1

def writeInfluxDBMeasurment(row,specdict = None,client=None,verbose = False, **kwargs):
    if verbose: mconsole(specdict)
    ''' Construct measurement from spec '''
    database = specdict['DATABASE']
    measurement_name = specdict['NAME']
    if 'TIMESTAMP' in row:
        ts = int(row['TIMESTAMP'].timestamp()*1000)
    else:
        ts = ""
    datstr = "{}".format(measurement_name)
    for tag in specdict['TAGS']: datstr += ",{}={}".format(tag,row[tag])
    datstr += " "
    for field in specdict['FIELDS']: datstr += "{}={},".format(field,row[field])
    datstr = datstr[:-1] + " {}".format(ts) # Remove comma at end and add timestamp
    data = [datstr.strip()] # strip in case no timestamp

    if client.write_points(data, database=database, time_precision='ms', batch_size =10000, protocol='line'):
        if verbose: mconsole("Success writing measurement: {}".format(measurement_name))
    else:
        mconsole("Writing measurement failed")
    if verbose: mconsole(data)
    
def handleInfluxDBMeasurement(fdf,measurement_name="perfmon",**kwargs):
    mconsole("Writing {} {} measurements".format(len(fdf),measurement_name))
    fdf.apply(writeInfluxDBMeasurment,measurement_name=measurement_name,**kwargs,axis=1)
