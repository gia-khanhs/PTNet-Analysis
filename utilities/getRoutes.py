from .dataPath import dataPath
#from .coords import *
from pathlib import Path
from turfpy import measurement
from geojson import Feature, Point
import json

path = dataPath()

def getRouteJson(folderPath):
    folderPath = Path(folderPath)
    filePattern = "route*.json"
    matchingFiles = list(folderPath.glob(filePattern))
    return matchingFiles

def getRouteTimetable():
    return getRouteJson(path.routeTimetable)

def getStopSeq():
    return getRouteJson(path.stopSeq)



routeTimetable = getRouteTimetable()
allRouteStopSeq = getStopSeq()
allRouteInfo = []
routeCnt = 0
'''
The structure of allRouteInfo:
allRouteInfo:
    [route]:
        RouteId
        RouteNo
        avgTravelTime
        InboundDist
        [InboundSeq]:
            [dist]    #Weight
            [time]    #Weight
        [OutboundSeq]:
            [dist]
            [time]
        OutboundDist
'''
#Get information about all routes
with open(path.allRouteJson, 'r', encoding = 'utf-8') as file:
    allRouteInfo = file.read();
    allRouteInfo = json.loads(allRouteInfo)
    file.close()
    
#Add relevant missing information to the routes
for route in allRouteInfo:
    route['RouteNo'] = route['RouteNo'].lstrip('0')

    if route['RouteNo'] in {"DL01", "72-1", "70-5", "61-4", "61-7"}: continue

    tmpPath = path.stopSeq + "route" + route['RouteNo'] + ".json"
    with open(tmpPath, 'r', encoding = "utf-8") as file:
        routeSeq = file.read()
        routeSeq = json.loads(routeSeq)
        file.close()

        route['InboundSeq'] = []
        route['OutboundSeq'] = []
        curSeq = 'InboundSeq'
        #pathPoints format: lng1, lat1, lng2, lat2, lng3, lat3, ... lng_n, lat_n

        #Calculating distance to travel between stations in a route
        #prePoint = geoPos(routeSeq[0]['Lat'], routeSeq[0]['Lng'])
        prePoint = Feature(geometry=Point((routeSeq[0]['Lng'], routeSeq[0]['Lat'])))
        
        for station in routeSeq:
            #Reversed direction
            if station['StationDirection']:
                curSeq = 'OutboundSeq'
                dist = 0
                prePoint = Feature(geometry=Point((station['Lng'], station['Lat'])))

            route[curSeq].append(station)
            #Initialising dist: the distance to traverse from the previous station to the current
            dist = 0
            #Calculate distance between consecutive pathpoints
            pathPoints = station['pathPoints'].split()
            for point in pathPoints:
                point = point.split(',')
                point[0] = float(point[0])
                point[1] = float(point[1])
                #point = geoPos(point[1], point[0])
                point = Feature(geometry=Point((point[0], point[1])))

                #dist = dist + prePoint.arcLen(point)
                dist = dist + measurement.distance(prePoint, point) * 1000
                prePoint = point
            #dist: the distance to traverse from the previous station to the current
            route[curSeq][-1]['dist'] = dist
    
    #Estimating the whole traveling distance of both directions (1 of the two weight of the graph's edge)
    dist = 0
    for weight in route['InboundSeq']: dist = dist + weight['dist']
    route['InboundDist'] = dist

    dist = 0
    for weight in route['OutboundSeq']: dist = dist + weight['dist']
    route['OutboundDist'] = dist

    #Calculate average travel time in seconds
    tripTime = route['TimeOfTrip']
    tripTime = tripTime.split('-')
    tripTime = 60 * (int(tripTime[0]) + int(tripTime[-1])) / 2
    route['avgTripTime'] = tripTime
    
    #Calculate the average time to travel from station to station (the second weight of the edeg)
    for weight in route['InboundSeq']:
        weight['time'] = route['avgTripTime'] * (weight['dist'] / route['InboundDist'])
    
    for weight in route['OutboundSeq']:
        weight['time'] = route['avgTripTime'] * (weight['dist'] / route['OutboundDist'])
    #print(routeSeq)

#Count the number of directed routes
for route in allRouteInfo:
    if route['RouteNo'] in {"DL01", "72-1", "70-5", "61-4", "61-7"}: continue
    if(len(route['InboundSeq'])): routeCnt += 1
    if(len(route['OutboundSeq'])): routeCnt += 1