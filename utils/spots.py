import geopandas as gpd
import time
import numpy as np
import shapely
from shapely.geometry import Polygon
import math
from rasterstats import zonal_stats


def detectRoofSpots(suitable_area,roof,index,conversionFactor=0.032/3600,step=0.2,w=0.8,h=1.2):
    # Identify the bounding box as before
    roofCenter=roof.centroid
    rotatedRoof=shapely.affinity.rotate(roof,math.acos(suitable_area.iloc[index]['cos']),origin=roofCenter,use_radians=True)
    _boundingBox=rotatedRoof.envelope
    boundingBox=shapely.affinity.rotate(_boundingBox,2*math.pi-math.acos(suitable_area.iloc[index]['cos']),origin=roofCenter,use_radians=True)

    # Find the initial point
    xs,ys=_boundingBox.exterior.xy
    startX=xs[0]
    startY=ys[0]
    endX=xs[1]
    endY=ys[2]

    # Panel Size
    panelW=w*conversionFactor
    panelH=h*np.cos(np.deg2rad(suitable_area.iloc[index]['slopemean']))*conversionFactor

    actualX=startX
    actualY=startY
    availablePositions=gpd.GeoDataFrame()

    # Step of the movement
    dx=step*conversionFactor
    dy=step*conversionFactor
    panels=[]
    while actualX+panelW<endX:
        while actualY+panelH<endY:
            # Find the new panel position
            _panel=Polygon([(actualX,actualY),(actualX,actualY+panelH),(actualX+panelW,actualY+panelH),(actualX+panelW,actualY)])
            panel=shapely.affinity.rotate(_panel,2*math.pi-math.acos(suitable_area.iloc[index]['cos']),origin=roofCenter,use_radians=True)
            # Check if it is inside the suitable area
            if panel.within(roof):
                panels.append(panel)
            actualY+=dy
        actualX+=dx
        actualY=startY
    return panels

def detectAllSpots(suitable_area):
    print("Detecting all the possible panels spots for the given surfaces")
    all_panels=[]
    finish=len(suitable_area)
    for index,roof in suitable_area.iterrows():
        roof=suitable_area.iloc[index]['geometry']
        roofID=suitable_area.iloc[index]["FID"]
        roofH=suitable_area.iloc[index]["ALTEZZA"]
        panels=detectRoofSpots(suitable_area,roof,index)
        for p in panels:
            p.h=roofH
            p.uid=roofID
            all_panels.append(p)
        print(f"{(index+1)*100/finish:.2f}",end='\r')
    return all_panels

def sortedZonalStats(all_panels,threshold):
    panel_stats=[]
    startTime=time.time()
    print("Starting zonal stats")
    for i,p in enumerate(all_panels):
        s=zonal_stats(p,"data/percentile.tiff",stats=['min'])[0]
        s["index"]=i
        s['h']=p.h
        s['uid']=p.uid
        if s["min"]>threshold:
            panel_stats.append(s)
        print(f"{i*100/len(all_panels):.2f}",end='\r')
    print(f"Finished zonal stats  {time.time()-startTime:.2f}")
    startTime=time.time()
    print("Started sorting")
    panels_sorted=sorted(panel_stats,key=lambda x: x["min"],reverse=True)
    print(f"Finished sorting  {time.time()-startTime:.2f}")
    return panels_sorted
