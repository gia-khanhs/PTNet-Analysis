from .dataPath import dataPath
import json
import geojson
from geojson import Feature, MultiPolygon, Point
from turfpy.measurement import boolean_point_in_polygon

hcmcPath = dataPath.data + "hcmc.geojson"

with open(hcmcPath, 'r', encoding = 'utf-8') as file:
    data = geojson.load(file)
    file.close()

data = data.geometries[0].coordinates
hcmcRegion = Feature(geometry=MultiPolygon(data))

def inHcmc(point):
    return boolean_point_in_polygon(point, hcmcRegion)
