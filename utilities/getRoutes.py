from .dataPath import dataPath
#from .coords import *
from pathlib import Path
from turfpy import measurement
from geojson import Feature, Point
import json

path = dataPath()

walkDistance = 300
walkSpeed = 1.3
dwellTime = 6

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
            dist    #Weight
            time    #Weight
        [OutboundSeq]:
            dist
            time
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

    seqPath = path.stopSeq + "route" + route['RouteNo'] + ".json"
    timePath = path.routeTimetable + "route" + route['RouteNo'] + ".json"
    with open(seqPath, 'r', encoding = "utf-8") as file:
        routeSeq = file.read()
        routeSeq = json.loads(routeSeq)
        file.close()
    with open(timePath, 'r', encoding = "utf-8") as file:
        timetable = file.read()
        timetable = json.loads(timetable)
        file.close()
    timeIn = timetable["timeTableIn"].split(',')
    for i, t in enumerate(timeIn): timeIn[i] = int(t)
    timeOut = timetable["timeTableOut"].split(',')
    for i, t in enumerate(timeOut): timeOut[i] = int(t)

    #Route 120 is a special one. Its path (either inbound or outbound) makes a loop.
    #The timetable for this route is available for both directions.
    #But the sequence only contains 1 of the two (because they are similar)
    if route['RouteNo'] != '120': route['timeTableIn'] = timeIn
    route['InboundSeq'] = []
        
    route['OutboundSeq'] = []
    route['timeTableOut'] = timeOut
    
    curSeq = 'InboundSeq'
    #pathPoints format: lng1, lat1, lng2, lat2, lng3, lat3, ... lng_n, lat_n

    #Calculating distance to travel between stations in a route
    #prePoint = geoPos(routeSeq[0]['Lat'], routeSeq[0]['Lng'])
    
    for station in routeSeq:
        #Reversed direction
        if station['StationDirection']:
            curSeq = 'OutboundSeq'
            dist = 0

        route[curSeq].append(station)
        #Initialising dist: the distance to traverse from the previous station to the current
        dist = 0
        #Calculate distance between consecutive pathpoints
        pathPoints = station['pathPoints'].split()
        prePoint = Feature(geometry=Point(()))
        for i, point in enumerate(pathPoints):
            point = point.split(',')
            point[0] = float(point[0])
            point[1] = float(point[1])
            #point = geoPos(point[1], point[0])
            point = Feature(geometry=Point((point[0], point[1])))

            #dist = dist + prePoint.arcLen(point)
            if i: dist = dist + measurement.distance(prePoint, point) * 1000
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
    inboundTime = tripTime - (len(route['InboundSeq']) - 1) * dwellTime
    for weight in route['InboundSeq']:
        weight['time'] = inboundTime * (weight['dist'] / route['InboundDist'])
    
    outboundTime = tripTime - (len(route['OutboundSeq']) - 1) * dwellTime
    for weight in route['OutboundSeq']:
        weight['time'] = outboundTime * (weight['dist'] / route['OutboundDist'])
    #print(routeSeq)

#Count the number of directed routes
for route in allRouteInfo:
    if route['RouteNo'] in {"DL01", "72-1", "70-5", "61-4", "61-7"}: continue
    if(len(route['InboundSeq'])): routeCnt += 1
    if(len(route['OutboundSeq'])): routeCnt += 1