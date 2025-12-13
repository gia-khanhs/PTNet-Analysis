from utilities.getRoutes import allRouteInfo
from utilities.dataPath import saves
from utilities.topoDataIO import saveTopoGraph, buildLGraph
from utilities.getRoutes import dwellTime

import json
import time

maxWaitTime = 60 * 60

def getDeparture():
    depart = {}
    departKey = set()

    for i, route in enumerate(allRouteInfo):
        if route.get('timeTableIn') != None:
            for time in route['timeTableIn']:
                newDeparture = (i, 'InboundSeq')

                departKey.add(time)
                if depart.get(time) == None: depart[time] = [newDeparture]
                else: depart[time].append(newDeparture)
        
        if route.get('timeTableOut') != None:
            for time in route['timeTableOut']:
                newDeparture = (i, 'OutboundSeq')

                departKey.add(time)
                if depart.get(time) == None: depart[time] = [newDeparture]
                else: depart[time].append(newDeparture)

    departKey = sorted(departKey)
    return (departKey, depart)

def getStations(mimicPaper = False):
    stations = []
    try:
        with open(saves + "stations.json", 'r', encoding = 'utf-8') as file:
            stations = file.read()
            stations = json.loads(stations)
            file.close()

        if (mimicPaper and len(stations) < 4350) or (not mimicPaper and len(stations) > 4343):
            saveTopoGraph(buildLGraph(mimicPaper))
            time.sleep(0.1)
            with open(saves + "stations.json", 'r', encoding = 'utf-8') as file:
                stations = file.read()
                stations = json.loads(stations)
                file.close()
    except IOError:
        saveTopoGraph(buildLGraph(mimicPaper))
        time.sleep(0.1)
        with open(saves + "stations.json", 'r', encoding = 'utf-8') as file:
            stations = file.read()
            stations = json.loads(stations)
            file.close()
    
    return stations

def buildTransitGraph(mimicPaper = False):
    departTime, departRoute = getDeparture()
    stations = getStations(mimicPaper)
    compactedId = [0] * 7620 #The maximum id is 7617
    nStation = len(stations) - 1
    
    for i in range(1, nStation + 1): 
        compactedId[stations[i]['id']] = i
    
    nodes = []
    nodeIds = []
    sortedIds = []
    transitEdges = []

    for _departTime in departTime:
        for routeId, seq in departRoute[_departTime]:
            if allRouteInfo[routeId].get(seq) == None: continue

            time = _departTime
            firstStation = allRouteInfo[routeId][seq][0]
            if not compactedId[firstStation['StationId']]: firstStation = allRouteInfo[routeId][seq][1]
            lastStation = allRouteInfo[routeId][seq][-1]
            if not compactedId[lastStation['StationId']]: lastStation = allRouteInfo[routeId][seq][-2]

            isNewFirst = True
            for station in allRouteInfo[routeId][seq]:
                time += station['time']

                #End stops outside of HCMC are skipped (not added to the graph)
                if not compactedId[station['StationId']]: continue
                
                if not isNewFirst: #only add arrivals of intermediate and last stations
                    newNode = (time, (routeId, seq), compactedId[station['StationId']], 0)
                    #time, (compactedRouteId, inbound/outbound), compactedStationId, 0/1: arrival/departure
                    nodes.append(newNode) #arrival node
                    curN = len(nodes) - 1
                    nodeIds.append(curN)
                    #=============================
                    transitEdges.append((curN - 1, curN))
                    #=============================
                else: isNewFirst = False

                if station != lastStation: #only add departures of intermediate and first stations
                    time += dwellTime
                    newNode = (time, (routeId, seq), compactedId[station['StationId']], 1)
                    #===================================
                    nodes.append(newNode) #departure node
                    curN = len(nodes) - 1
                    nodeIds.append(curN)
                    #===================================
                    if station != firstStation: transitEdges.append((curN - 1, curN))
                    #===================================
                else: break
                    
    
    sortedPairs = sorted(zip(nodes, nodeIds))
    nodes, nodeIds = zip(*sortedPairs)
    nodes = list(nodes)
    nodeIds = list(nodeIds)

    sortedIds = [0] * len(nodeIds)
    for i, x in enumerate(nodeIds): sortedIds[x] = i

    for i in range(len(transitEdges)):
        transitEdges[i] = (sortedIds[transitEdges[i][0]], sortedIds[transitEdges[i][1]])

    print("==== Built temporal transit graph  ====")
    print("Node count:", len(nodes))
    print("Transit edge count:", len(transitEdges))
    print("========================================")

    return (stations, nodes, transitEdges)

def getNodesById(mimicPaper = False): #Get nodes by compactedStationId
    stations, nodes, transitEdges = buildTransitGraph(mimicPaper)
    nNode = len(nodes) - 1
    nodesById = ([[] for i in range(nNode + 1)], [[] for j in range(nNode + 1)])
    #nodesById[0/1 = arrival/departure][compactedStationId]

    for iNode, node in enumerate(nodes):
        time, (routeId, seq), stationId, type = node
        nodesById[type][stationId].append((time, (routeId, seq), iNode))

    return (stations, nodes, nodesById, transitEdges)

def buildWaitingEdge(mimicPaper = False):
    stations, nodes, nodesById, transitEdges = getNodesById(mimicPaper)
    waitingEdges = []
    
    for stationId in range(len(stations)):
        arrivals = nodesById[0][stationId]
        departures = nodesById[1][stationId]
        maxI = len(arrivals) - 1
        maxJ = len(departures) - 1

        firstLarger = 0
        if min(maxI, maxJ) < 0: continue
        while firstLarger < maxJ and departures[firstLarger][0] <= arrivals[0][0]: firstLarger += 1

        for i, arriveNode in enumerate(arrivals): #looping through arrival nodes
            arriveTime, (arriveRouteId, arriveSeq), arriveNodeId = arriveNode  

            nextLarger = None
            #firstLarger is always the id of the departure node with time > current arrive node
            for j in range(firstLarger, maxJ + 1):
                if nextLarger is None and i != maxI and \
                    arrivals[i + 1][0] < departures[j][0]:\
                    nextLarger = j #To update firstLarger

                departTime, (departRouteId, departSeq), departNodeId = departures[j]

                if departTime > arriveTime + maxWaitTime:
                    if nextLarger is not None: break
                    else: continue #continue loop to find dep node with id > next arrival node
                    
                if (arriveRouteId, arriveSeq) != (departRouteId, departSeq):
                    waitingEdges.append((arriveNodeId, departNodeId))

            if nextLarger is not None: firstLarger = nextLarger
            else: break #if the next arrival node is larger than every departure node, break
        
    print("==== Built temporal graph waiting edges ====")
    print("Waiting edge count: ", len(waitingEdges))
    print("===========================================")
    return (nodes, nodesById, stations, transitEdges, waitingEdges)