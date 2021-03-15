from utils.tiff import *
from utils.spots import *
from utils.placer import *
from utils.classic import *
from utils.tiff import *
from traces.mem_zonal_15 import *
#from traces.mem_zonal_v2 import *
from traces import *
import geopandas as gpd


def greedyAlgorithm(gh_t):
    suitable_area=gpd.read_file('data/areasuit_w_height_roofID.shp')
    all_panels=detectAllSpots(suitable_area)
    for t in gh_t:
        print (f"GHI threshold :{t}")
        panels_sorted=sortedZonalStats(all_panels,t)
        output=findBestPlaces(all_panels, panels_sorted)
        output.to_file("resultv2/greedy_"+str(t)+".shp")

def classicAlgorithm(gh_t):
    suitable_area='data/areasuit_w_height_roofID.shp'
    for t in gh_t:
        output="resultv2/greedy_"+str(t)+".shp"
        gdf=getClassic(suitable_area,output).to_file("resultv2/classic_"+str(t)+".shp")


def evaluateTraces(filename):
    shapefile="points2_shp/"+filename+"_points.shp"
    radiation  = evaluate(shapefile)
    radiation.to_csv("traces2/"+filename+'.csv')  

def evaluateTracesv2(filename):
    shapefile="points2_shp/"+filename+"_points.shp"
    radiation  = evaluate(shapefile)
    radiation.to_csv("traces2/"+filename+'.csv')      

if __name__=="__main__":
    #gh_t=[i for i in range(400,600,50)]
    gh_t=[600]
    #createPercentileTiff()
    #greedyAlgorithm(gh_t)
    #classicAlgorithm(gh_t)
    #evaluateTracesv2("classic_500")
    #evaluateTracesv2("output_500")
    evaluateTraces("classic_600")
    #evaluateTraces("greedy_600")

