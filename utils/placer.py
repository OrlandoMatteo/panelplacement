import geopandas as gpd
import sys
import copy
import time
import numpy as np
import shapely
from shapely.geometry import Polygon
import math
from rasterstats import zonal_stats

def findBestPlaces(all_panels,panels_sorted,conversionFactor=0.032/3600,series_len=8,height_thresh=0.5,dist_thresh=6):
    """findBestPlaces.

    :param all_panels    -- unsorted list with the panel geometries:
    :param panels_sorted -- sorted list of the index corresponding to the best panels spots:
    :param ghi_threshold -- threshold for the ghi:
    :param series_len    -- len of the series of panel:
    :param height_thresh -- maximum difference of height among two consecutive panels:
    :param dist_thresh   -- maximum distance among two consecutive panels:
    """
    # Set counter for the cycle to 0
    c=0
    # Create a sorted list of panels with their geometry and their properties
    _panels=[{"geometry":all_panels[i["index"]],"properties":i} for i in panels_sorted]
    # Create empty list for the output
    top_panels=[]
    # Create empty list for that is filled at each cycle
    batch=[]
    # Index for batch
    counter=1
    # Start from the best panel
    batch.append(_panels[c])
    # Remove the best panel from the list
    _panels.pop(c)
    # Start the series of panel at 1
    series=1
    # id that identifies each group of panles
    group=0
    # list of the ids of the group
    groupList=[]
    # list of panel that during the search are not considered because too far from the last one
    discarded_panels=[]
    # List of roof that have been already used
    discardedRoof=[]
    print("Starting placement")
    try:
        # Keep placing paanels until the minimum ghi is less than a user definedtreshold
        while len(_panels)>0:
            # Keep looking for a possible panel to be added to a series until the list is empty
            while c<len(_panels):
                # panel geometry object
                p=_panels[c]["geometry"]
                # height of the roof for that panel position
                p_height=_panels[c]["properties"]['h']
                # check if the position does not itersect the ones selected previously (nor this batch nor the previous) and check the roof was not already used
                if not any([p.intersects(j["geometry"]) for j in top_panels]) and not any([p.intersects(k["geometry"]) for k in batch]) and not _panels[c]["properties"]["uid"] in discardedRoof:
                    # difference in height between the last selected panel and the current inspected one
                    height_diff=abs(p_height-batch[-1]["properties"]['h'])
                    # if the panel is not the last one of the series check if its distance from the last one is lessa the threshold and the height diff is less than a threshold
                    if series<series_len and p.distance(batch[-1]["geometry"])<dist_thresh*conversionFactor and height_diff<height_thresh:
                        batch.append(_panels[c])
                        _panels.pop(c)
                        counter+=1
                        series+=1
                        c=0
                    # if the panel is the last one of the series do the control as the previous case but reset the series id
                    elif series==series_len and p.distance(batch[-1]["geometry"])<dist_thresh*conversionFactor and height_diff<height_thresh:
                        batch.append(_panels[c])
                        _panels.pop(c)
                        counter+=1
                        series=1
                        c=0
                    # if the panel cannot be placed discarded from the moment being
                    else:
                        discarded_panels.append(_panels.pop(c))
                        c+=1
                # if the panel overlaps the previous ones or is on a roof already used completely remove it
                else:
                    _panels.pop(c)
                    c+=1
            # for each panels of group store the id of the roof to avoid to use it again
            for p in batch:
                discardedRoof.append(p["properties"]["uid"])
            # if the batch obtained contains too few panels discard it and restart reinserting the panels discarded at line 72 
            if len(batch)<series_len:
                _panels=discarded_panels+batch+_panels
                discarded_panels=[]
                c=0
                counter=1
                batch=[]
                batch.append(_panels[c])
                _panels.pop(c)
            # if the bactch obtained is long enough add the panels to the optimal configuration and store the id of the group they belong to
            else:
                # add only the panels in a number multiple of the selected length of the series
                for i in batch[:-(counter%series_len)]:
                    groupList.append(group)
                    top_panels.append(i)
                # increase the group counter
                group+=1
                # reinsert the panels discarded at line 72
                _panels=[x for x in discarded_panels+_panels]
                # reset the list of discarded panels
                discarded_panels=[]
                # reset the counter for the cycle to 0
                c=0
                # reset the batch
                batch=[]
                # reset the countere for the number of panel in the batch
                counter=1
                # restart from the best panel
                batch.append(_panels[c])
                _panels.pop(c)
            print(f'{len(top_panels)} panels placed  ({len(_panels)})',end='\r')
    # in case of errors or at the end of the cycle create a dataframe with all the info needed
    except:
        print("Unexpected error:", sys.exc_info()[0])
        output=gpd.GeoDataFrame({"geometry":[x["geometry"] for x in top_panels],
                                 "group":[x for x in groupList],
                                 "min_ghi":[x["properties"]["min"] for x in top_panels],
                                 "roofID":[x["properties"]["uid"] for x in top_panels]}).set_geometry('geometry')
    for i in batch[:-(counter%8)]:
        top_panels.append(i)
    output=gpd.GeoDataFrame({"geometry":[x["geometry"] for x in top_panels],
                                 "group":[x for x in groupList],
                                 "min_ghi":[x["properties"]["min"] for x in top_panels],
                                 "roofID":[x["properties"]["uid"] for x in top_panels]}).set_geometry('geometry')
    print("Finished placing")
    return output
