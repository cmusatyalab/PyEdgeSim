import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from pandas.plotting import table
import matplotlib
import matplotlib.pyplot as plt
import geopandas as gp
import shapely
from shapely.geometry import Point,LineString,Polygon,MultiPolygon
from scipy.spatial import cKDTree

# from osgeo import ogr
# from osgeo import gdal,ogr,osr,gdalnumeric
import shapefile as shp  # Requires the pyshp package
import matplotlib.pyplot as plt

import contextily as ctx

crs = {'init':'epsg:4326'}
ctxprovider=ctx.sources.OSM_A

''' Working with Points 
    Some of these can be lambda for apply/map functions 
  '''
def pt2geom(fdf,latcol='LAT',lngcol='LONG'):
    geometry = [Point(xy) for xy in zip(pd.to_numeric(fdf[lngcol]),pd.to_numeric(fdf[latcol]))]
    return geometry

def strpt2shapelypt(strin):
    if isinstance(strin,Point):
        return strin
    tlst = strin.split(' ')
    lng = float(tlst[1].replace('(',''))
    lat = float(tlst[2].replace(')',''))
    pt = Point(lng,lat)
    return pt

def strply2shapelyply(cell): # map: lambda cell has string Polygon
    if isinstance(cell,str):
        return shapely.wkt.loads(cell)
    else:
        return cell
    
def str2shapely(cell): # map: lambda cell has string Polygon or Point
    try:
        if isinstance(cell,str):
    #         print(cell)
            if 'POINT' in cell:
                return strpt2shapelypt(cell)
            elif 'POLYGON' in cell:
                return strply2shapelyply(cell)
            else:
                print("Unknown Type: %s" % cell)
                return np.nan
        elif np.isnan(cell):
            return cell
        else:
            print("Not String: {} {}".format(cell,type(cell)))
    except:
#         print("Not String: {} {}".format(cell,type(cell)))
        pass
    return cell

def flt2shapelypt(fdf,loncol=None,latcol=None): # Longitude first
    return Point(fdf[loncol],fdf[latcol])

def strpts2dist(fpt1,fpt2): # Distance in miles
    fdf = dfptstr2geom(pd.DataFrame([pt1,pt2],columns=['geometry'])).reset_index()
    fgp = df2gp(fdf,geom=fdf['geometry'])
    fdist = geodist(fgp)
    return fdist

def shapelypt2strpt(ptin):
    return ptin if isinstance(ptin,str) else str(ptin)

''' Working with DataFrames '''
def dfstr2shapely(fdf,subset=['geometry']):
    for col in subset:
        fdf[col] = fdf[col].map(str2shapely)
    return fdf
def dfptstr2geom(fdf):
    geometry = fdf['geometry'].map(strpt2shapelypt)
    return geometry

def dfstrgeom2ptgeom(fdf):
    fdf['geometry']= dfptstr2geom(fdf)
    return fdf

def df2gp(fdf,geometry=None):
    if geometry is None:
        geometry = fdf['geometry']
    if isinstance(geometry.iloc[0], str):
        geometry = geometry.map(str2shapely)
    return gp.GeoDataFrame(fdf,crs=crs,geometry=geometry)

''' Working with GeoPandas '''
def geodist(gpdf): # in miles
    ''' Distance between two adjacent rows '''
    gpdf = gpdf.to_crs(epsg=3310)
    dist = gpdf.distance(gpdf.shift()) * 0.00062137
    return (dist)

def geodist2(gpdf,col1='geometry',col2=None): # in miles
    ''' Distance between two geometry columns '''
    fgp = gpdf.copy()
    fgp1 = fgp.to_crs(epsg=3310)
    fgp[col1] = fgp[col2]
    fgp2 = fgp.to_crs(epsg=3310)
    dist = fgp1.distance(fgp2) * 0.00062137
    return (dist)

def findnearest(fdfA, fdfB,k=1,units='mile'):
    ''' Finds the nearest K points to each row of fdfA from fdfB 
        Returns a pandas dataframe not a geopandas dataframe '''
    gdA = fdfA.copy().reset_index()
    gdB = fdfB.copy().reset_index()
    nA = np.array(list(zip(gdA.geometry.x, gdA.geometry.y)) )
    nB = np.array(list(zip(gdB.geometry.x, gdB.geometry.y)) )
    
    ''' Find Nearest '''
    btree = cKDTree(nB)
    distlst, idxlst = btree.query(nA, k=k)
    
    ''' Join with fdfA '''
    distcols = ["Dist_NEAR{}".format(ii) for ii in range(0,k)]   
    distdf = pd.DataFrame(distlst,columns=distcols)
    if units == 'mile': # default radians
        distdf[distcols] = distdf[distcols].apply(lambda col: col*66) # convert to miles
    idxcols = ["NEAR{}".format(ii) for ii in range(0,k)]    
    idxdf = pd.DataFrame(idxlst,columns=idxcols)
    gdf = pd.concat([gdA.reset_index(drop=True),distdf,idxdf],axis=1)
    gdB = gdB.drop(columns=['index']).reset_index()
    gdBcol = gdB.columns
    for nearcol in idxcols:
        gdC = gdB.copy()
        gdC.columns = gdC.columns.map(lambda col: str(col) + '_' + nearcol) # force suffix
        gdf = gdf.set_index(nearcol).join(gdC) \
            .reset_index().rename(columns={'level_0':nearcol})
    gdf = gdf.drop(columns=idxcols + ['index'])
    
    ''' Clean-up '''
    for var in [gdA,gdB,gdC,nA,nB,distdf,idxdf,distlst,idxlst]:
        del var

    return gdf

''' GeoPandas Plotting '''
gp_deffont = {'fontweight':'ultralight','color':'blue','size':16,'fontfamily':'cursive','style':'normal'}
def gp_getDefFont(): # Use if you want to change some of the options
    return gp_deffont
def gp_setAxesScales(ax,xscaledict={},yscaledict={},option=None,**kwargs): # TODO x and y limits
    if not option is None:
        ax.axis(option)
def gp_setAxesLabels(ax,xlabel='',ylabel='',font = {'size':16}):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
def gp_setTitle(ax,title,**kwargs):
    ax.set_title(title,**kwargs)
def getPolygon(bnddf):
    return Polygon([(p.x,p.y) for p in bnddf['geometry']])
def getPolygonXY(bnddf):
    return getPolygon(bnddf).exterior.xy

def getCentroid(row): # Apply-Lambda
    geom = row.geometry
    if isinstance(geom, Polygon):
#         print("Is Polygon",geom.centroid)
        return geom.centroid
    else:
        return np.nan

def getPointXY(ptdf):
    x = ptdf['geometry'].x
    y = ptdf['geometry'].y
    return x,y
def plot_points(ptdf,ax,s=50,**kwargs):
    x,y = getPointXY(ptdf)
    ax.scatter(x,y,s=s,alpha=0.5,**kwargs)
def plot_poly_boundary(bnddf,ax,**kwargs):
    x,y = getPolygonXY(bnddf)
    ax.plot(x,y)
    
def gp_scatterplot(fgp,ax = None,ptype='Points',mapon=False,figsize=(10,10),ctxprovider=ctxprovider,**kwargs):
    if mapon:
        fgp = fgp.to_crs(epsg=3857)
    if ax is None:
        ax = plt.figure(figsize=figsize).add_subplot(111)
    plot_points(fgp,ax)
    if mapon:
        ctx.add_basemap(ax,  source=ctxprovider)
    return ax
def gp_plot_poly_boundary(fgp,ax=None,figsize=(10,10),mapon=True,ctxprovider=ctxprovider,**kwargs):
    ''' fgp geometry is list of points containing the boundary '''
    if mapon:
        fgp = fgp.to_crs(epsg=3857)    
    if ax is None:
        ax = plt.figure(figsize=figsize).add_subplot(111)
    x,y = getPolygonXY(fgp)
    ax.plot(x,y)
    if mapon:
        ctx.add_basemap(ax,  source=ctxprovider)
    return ax

def gp_getInside(cell, pgp,col):
    ''' Find which polygon a point is in. cell is a point, pgp is a gp of polygons and keys, 
        col is the column containing the key value in pgp '''
    lz = np.nan
    lz = pgp.apply(lambda row: row[col] if cell.within(row['geometry']) else lz,axis=1).dropna()
    if lz.shape[0] > 1:
        dumpdf(lz)
    if lz.shape[0] == 0:
        return np.nan
    return lz.iloc[0]

def getPolyXY(poly):
    if isinstance(poly,Polygon):
        return [(poly.exterior.xy)]
    if isinstance(poly,MultiPolygon):
        subpolyXYlst = []
        for subpoly in poly:
            x,y = subpoly.exterior.xy
            subpolyXYlst.append((x,y))
        return subpolyXYlst
    else:
        print("isnot polygon")
        print(type(poly),poly)
    return [(np.nan,np.nan)]
def plotPoly(row,ax,**kwargs): # Lambda
    xylst = getPolyXY(row['geometry'])
    for tup in  xylst: # Single tuple for Polygon, multiple tuple for multipolygon
        x = tup[0]
        y = tup[1]
        if x != np.nan:
            ax.plot(x,y,**kwargs)
def gp_plotPoly(fgp,mapon=False, ax=None,figsize=(10,10),ctxprovider=ctxprovider,**kwargs): 
    ''' GeoPandas DataFrame with 'geometry' containing Polygons '''
    if ax is None:
        ax = plt.figure(figsize=figsize).add_subplot(111)    
    if mapon:
        fgp = fgp.to_crs(epsg=3857)
    devnull = fgp.apply(plotPoly,ax=ax,**kwargs,axis=1)
    if mapon:
        ctx.add_basemap(ax,  source=ctxprovider)
    return ax

def gp_plotPoint(fgp,ax,s=50,alpha=0.5,**kwargs): # Lambda
    x,y = getPointXY(fgp)
    ax.scatter(x,y,s=s,alpha=alpha,**kwargs)
def gp_plotPoints(fgp,ax = None,ptype='Points',mapon=False, title=None,
                  figsize=(10,10),ctxprovider=ctxprovider,**kwargs):
    '''   GeoPandas DataFrame with 'geometry'containing Points '''
    if mapon:
        fgp = fgp.to_crs(epsg=3857)
    if ax is None:
        ax = plt.figure(figsize=figsize).add_subplot(111)
    gp_plotPoint(fgp,ax,**kwargs)
    gp_setAxesScales(ax,option=False)
    if not title is None:
        gp_setTitle(ax,title)
    if mapon:
        ctx.add_basemap(ax,  source=ctxprovider)
    return ax
def gp_plotLines(fgp,ax = None,geocol='geometry',ptype='Lines',mapon=False, title=None,
                  figsize=(10,10),ctxprovider=ctxprovider,**kwargs):
    ''' GeoPandas DataFrame with 'geometry' containing LineStrings '''
    ''' Note: color parameter is 'color' '''
    if geocol != 'geometry':
        fgp['geometry'] = fgp[geocol]    
    if mapon:
        fgp = fgp.to_crs(epsg=3857)
    if ax is None:
        ax = plt.figure(figsize=figsize).add_subplot(111)
    ax = fgp.plot(axes=ax,**kwargs)
    gp_setAxesScales(ax,option=False)
    if not title is None:
        gp_setTitle(ax,title)
    if mapon:
        ctx.add_basemap(ax,  source=ctxprovider)
    return ax

def gp_Points2Lines(fgp):
    fgp['geometryshift'] = fgp['geometry'].shift(-1)
    fgp = fgp.dropna()
    return fgp.apply(lambda row: LineString([row['geometry'],row['geometryshift']]), axis = 1)
    
def gp_getMarkerSize(ser,maxsize=1000,minsize=30): # Return normalized marker series
    sermax = ser.max()
    retser = ser.map(lambda cell: max(minsize, cell*maxsize/sermax))
    return retser
def gp_getCentroid(fdf): # Lambda
    return fdf['geometry'].map(getCentroidPoly)
#     return row.geometry.centroid if isinstance(row.geometry, Polygon) else np.nan

''' Point Labels '''
def makeLabel(row,delimiter=', ',labelcol=[],**kwds): # Apply-Lambda
    retlab = ''
    for col in labelcol:
        colval = str(row[col])
        retlab += colval + delimiter
    retlab = retlab[:-2] # remove trailing delimiter and space
    return retlab
def gp_plotLabel(row,ax=None,xoffset=5000,yoffset=0,**kwds): # Apply-Lambda
    x,y=getPointXY(row)
    ax.text(x+xoffset,y+yoffset,row['label'],**kwds)

def gp_plotLabels(fgp,labelcol=[],ax=None,mapon=False,includegeom=False,delimiter=', ', # TODO Add geometry
                  figsize=(10,10),fontdict=gp_deffont,title=None,ctxprovider=ctxprovider,**kwargs):
    '''   GeoPandas DataFrame with 'geometry'containing Points '''
    if mapon:
        fgp = fgp.to_crs(epsg=3857)
    if ax is None:
        ax = plt.figure(figsize=figsize).add_subplot(111)
    gp_setAxesScales(ax,option=False)
    if len(labelcol) > 0:
        tlabgp = fgp[labelcol]
        tlabgp['geometry'] = fgp['geometry']
        tlabgp['label'] = tlabgp.apply(makeLabel,labelcol=labelcol,delimiter=delimiter,**kwargs,axis=1)
        tlabgp.apply(gp_plotLabel,ax=ax,fontdict=fontdict,**kwargs,axis=1)
    if not title is None:
        gp_setTitle(ax,title)
    if mapon:
        ctx.add_basemap(ax,  source=ctxprovider)
    return ax

def gp_printCTXproviders(printon=False):
    provlst=[]
    for key in ctx.providers:
        if 'url' in ctx.providers[key].keys():
            provlst.append(ctx.providers[key]['name'])
        else:
            for subkey in ctx.providers[key]:
                try:
                    provlst.append(ctx.providers[key][subkey]['name'])
                except:
                    pass
    provlst.sort()
    if printon:
        devnull = ["ctx.providers."+print(name) for name in provlst]
    return provlst

''' Shapefiles '''
def getShapeFile(fn):
    return shp.Reader(fn)
def gp_readShapefile(fn): 
    return gp.read_file(fn)
def plotShapeFile(sf, ax = None, figsize=(20,20), **kwargs):
    if ax is None:
        ax = plt.figure(figsize=figsize).add_subplot(111)
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        ax.plot(x,y)
    return ax
def getCentroidPoly(geom): 
    return geom.centroid if isinstance(geom, Polygon) else np.nan 

### Tile provider sources ###

# ST_TONER = 'http://tile.stamen.com/toner/tileZ/tileX/tileY.png'
# ST_TONER_HYBRID = 'http://tile.stamen.com/toner-hybrid/tileZ/tileX/tileY.png'
# ST_TONER_LABELS = 'http://tile.stamen.com/toner-labels/tileZ/tileX/tileY.png'
# ST_TONER_LINES = 'http://tile.stamen.com/toner-lines/tileZ/tileX/tileY.png'
# ST_TONER_BACKGROUND = 'http://tile.stamen.com/toner-background/tileZ/tileX/tileY.png'
# ST_TONER_LITE = 'http://tile.stamen.com/toner-lite/tileZ/tileX/tileY.png'

# ST_TERRAIN = 'http://tile.stamen.com/terrain/tileZ/tileX/tileY.png'
# ST_TERRAIN_LABELS = 'http://tile.stamen.com/terrain-labels/tileZ/tileX/tileY.png'
# ST_TERRAIN_LINES = 'http://tile.stamen.com/terrain-lines/tileZ/tileX/tileY.png'
# ST_TERRAIN_BACKGROUND = 'http://tile.stamen.com/terrain-background/tileZ/tileX/tileY.png'

# ST_WATERCOLOR = 'http://tile.stamen.com/watercolor/tileZ/tileX/tileY.png'

# # OpenStreetMap as an alternative
# OSM_A = 'http://a.tile.openstreetmap.org/tileZ/tileX/tileY.png'
# OSM_B = 'http://b.tile.openstreetmap.org/tileZ/tileX/tileY.png'
# OSM_C = 'http://c.tile.openstreetmap.org/tileZ/tileX/tileY.png'

    