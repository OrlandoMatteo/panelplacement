import geopandas as gpd
import numpy as np
import shapely
import math
from shapely.geometry import Point,Polygon

def classicPlacement(roofRow,panelW=0.8,panelH=1.2,conversionFactor=0.032/3600):
    roof=roofRow["geometry"]
    panelW=panelW*conversionFactor
    panelH=panelH*np.cos(np.deg2rad(roofRow['slopemean']))*conversionFactor
    roofCenter=roof.centroid
    rotatedRoof=shapely.affinity.rotate(roof,math.acos(roofRow['cos']),origin=roofCenter,use_radians=True)
    _boundingBox=rotatedRoof.envelope
    axis_coords=list(_boundingBox.exterior.coords)
    axis1=Point(axis_coords[0]).distance(Point(axis_coords[1]))
    axis2=Point(axis_coords[1]).distance(Point(axis_coords[2]))
    numW=int(axis1/panelW)
    numH=int(axis2/panelH)
    nums=[numH+1,numW+1]
    startX=list(_boundingBox.exterior.coords)[0][0]
    startY=list(_boundingBox.exterior.coords)[0][1]
    panels=[]
    actualX=list(_boundingBox.exterior.coords)[0][0]
    actualY=list(_boundingBox.exterior.coords)[0][1]
    for i in range(nums[0]):
        for j in range(nums[1]):
            p=Polygon([(actualX,actualY),(actualX,actualY+panelH),(actualX+panelW,actualY+panelH),(actualX+panelW,actualY)])
            actualX+=panelW
            panels.append(p)
        actualY+=panelH
        actualX=startX
    _panels=[]
    for p in panels:
        _p=panel=shapely.affinity.rotate(p,2*math.pi-math.acos(roofRow['cos']),origin=roofCenter,use_radians=True)
        _panels.append(_p)
    final_panels=[p for p in _panels if p.within(roof)==True]
    return final_panels

def getClassic(areaSuitSHP,output):
    print("Placing panel with classic method")
    df=gpd.read_file(areaSuitSHP)
    roofdf=gpd.read_file(output)
    usedRoofs=list(set(roofdf["roofID"].values))
    classicRoofs=[]
    groups=[]
    roofIDs=[]
    end=len(usedRoofs)
    c=1
    for elem in usedRoofs:
        roofRow=df.iloc[df[df["FID"]==elem]["surface"].idxmax()]
        n_of_panels=sum(roofdf["roofID"]==elem)
        temp=classicPlacement(roofRow)[:n_of_panels]
        classicRoofs+=[x for x in temp]
        groups+=[c for i in range(len(temp))]
        roofIDs+=[elem for i in range(len(temp))]
        print(f"{c} of {end} roofs",end="\r")
        c+=1
    return gpd.GeoDataFrame({"geometry":[p for p in classicRoofs],
                             "group":[x for x in groups],
                             "roofID":[x for x in roofIDs]}).set_geometry("geometry")

