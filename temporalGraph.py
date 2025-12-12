from utilities.getRoutes import allRouteInfo
from utilities.dataPath import saves
from utilities.topoDataIO import saveGraph, buildLGraph
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

def getStops(mimicPaper = False):
    stops = []
    try:
        with open(saves + "stops.json", 'r', encoding = 'utf-8') as file:
            stops = file.read()
            stops = json.loads(stops)
            file.close()
        if (mimicPaper and len(stops)) < 4350 or (not mimicPaper and len(stops) > 4343):
            saveGraph(buildLGraph(mimicPaper))
            time.sleep(0.1)
            with open(saves + "stops.json", 'r', encoding = 'utf-8') as file:
                stops = file.read()
                stops = json.loads(stops)
                file.close()
    except IOError:
        saveGraph(buildLGraph(mimicPaper))
        time.sleep(0.1)
        with open(saves + "stops.json", 'r', encoding = 'utf-8') as file:
            stops = file.read()
            stops = json.loads(stops)
            file.close()
    
    return stops

def buildTransitGraph(mimicPaper = False):
    departTime, departRoute = getDeparture()
    stops = getStops(mimicPaper)
    compactedId = [0] * 7620 #The maximum id is 7617
    nStop = len(stops) - 1
    
    for i in range(1, nStop + 1): 
        compactedId[stops[i]['id']] = i
    
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
                    nodeIds.append(curN + 1)
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
    #CURRENT PROBLEM: ADD TRANSIST EDGES AND SORT => DISORTED EDGES
    #CURRENT PROBLEM: ADD TRANSIST EDGES AND SORT => DISORTED EDGES
    #CURRENT PROBLEM: ADD TRANSIST EDGES AND SORT => DISORTED EDGES
    #CURRENT PROBLEM: ADD TRANSIST EDGES AND SORT => DISORTED EDGES
    print("==== Built temporal transit graph  ====")
    print("Node count:", len(nodes))
    print("Transit edge count:", len(transitEdges))
    print("========================================")

    return (stops, nodes, transitEdges)

def getNodesById(): #Get nodes by compactedStationId
    stops, nodes, transitEdges = buildTransitGraph()
    nNode = len(nodes) - 1
    nodesById = ([[] for i in range(nNode + 1)], [[] for j in range(nNode + 1)])
    #nodesById[0/1 = arrival/departure][compactedStationId]

    for iNode, node in enumerate(nodes):
        time, (routeId, seq), stationId, type = node
        nodesById[type][stationId].append((time, (routeId, seq), iNode))

    return (stops, nodes, nodesById, transitEdges)

def buildWaitingEdge():
    stops, nodes, nodesById, transitEdges = getNodesById()
    waitingEdges = []
    
    for stationId in range(len(stops)):
        maxI = len(nodesById[0][stationId]) - 1
        for i, arriveNode in enumerate(nodesById[0][stationId]):
            arriveTime, (arriveRouteId, arriveSeq), arriveNodeId = arriveNode
            firstLarger = 0
            
            maxJ = len(nodesById[1][stationId]) - 1
            for j in range(firstLarger, maxJ + 1):
                departTime, (departRouteId, departSeq), departNodeId = nodesById[1][stationId][j]

                if departTime > arriveTime + maxWaitTime: break
                if arriveRouteId != departRouteId and arriveSeq != departSeq:
                    waitingEdges.append((arriveNodeId, departNodeId))

                nextLarger = 0
                if not nextLarger and i != maxI and \
                    nodesById[0][stationId][i + 1][0] < nodesById[1][stationId][j][0]:\
                    nextLarger = j
                if nextLarger: firstLarger = nextLarger
        
    print("==== Built temporal graph walking edges ====")
    print("Waiting edge count: ", len(waitingEdges))
    print("===========================================")
    return (nodes, nodesById, stops, transitEdges, waitingEdges)