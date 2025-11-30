from utilities.getRoutes import allRouteInfo
from utilities.dataPath import saves
from utilities.topoDataIO import saveGraph, buildLGraph
from utilities.getRoutes import dwellTime

import json

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

def getStops():
    stops = []
    try:
        with open(saves + "stops.json", 'r', encoding = 'utf-8') as file:
            stops = file.read()
            stops = json.loads(stops)
            file.close()
    except IOError:
        saveGraph(buildLGraph())
        with open(saves + "stops.json", 'r', encoding = 'utf-8') as file:
            stops = file.read()
            stops = json.loads(stops)
            file.close()
    
    return stops


def buildTransitGraph():
    departTime, departRoute = getDeparture()
    stops = getStops()
    compactedId = [0] * 7620 #The maximum id is 7617
    nStop = len(stops) - 1
    
    for i in range(1, nStop + 1): 
        compactedId[stops[i]['id']] = i
    
    nodes = []
    transitEdges = []

    for _departTime in departTime:
        for routeId, seq in departRoute[_departTime]:
            if allRouteInfo[routeId].get(seq) == None: continue

            time = _departTime
            firstStation = allRouteInfo[routeId][seq][0]
            lastStation = allRouteInfo[routeId][seq][-1]
            for station in allRouteInfo[routeId][seq]:
                time += station['time']

                #End stops outside of HCMC are skipped (not added to the graph)
                if not compactedId[station['StationId']] and (station == firstStation or station == lastStation): continue

                newNode = (time, (routeId, seq), compactedId[station['StationId']], 0)
                #time, (compactedRouteId, inbound/outbound), compactedStationId, 0/1: arrival/departure
                curN = len(nodes)
                #=============================
                #if current node is not the first node => Add transit edge
                if station != allRouteInfo[routeId][seq][0]:
                    if station == allRouteInfo[routeId][seq][1]:
                        if compactedId[allRouteInfo[routeId][seq][0]['StationId']]: transitEdges.append((curN - 1, curN))
                    else: transitEdges.append((curN - 1, curN))
                #=============================
                nodes.append(newNode)
                if station != firstStation and station != lastStation:
                    time += dwellTime
                    newNode = (time, (routeId, seq), compactedId[station['StationId']], 1)
                    #===================================
                    curN = len(nodes)
                    if station == allRouteInfo[routeId][seq][1]:
                        if compactedId[allRouteInfo[routeId][seq][0]['StationId']]: transitEdges.append((curN - 1, curN))
                    else: transitEdges.append((curN - 1, curN))
                    #===================================
                    nodes.append(newNode)
    
    nodes.sort()
    #CURRENT PROBLEM: ADD TRANSIST EDGES AND SORT => DISORTED EDGES & TRANSIT EDGE CNT > PAPER'S
    #CURRENT PROBLEM: ADD TRANSIST EDGES AND SORT => DISORTED EDGES & TRANSIT EDGE CNT > PAPER'S
    #CURRENT PROBLEM: ADD TRANSIST EDGES AND SORT => DISORTED EDGES & TRANSIT EDGE CNT > PAPER'S
    #CURRENT PROBLEM: ADD TRANSIST EDGES AND SORT => DISORTED EDGES & TRANSIT EDGE CNT > PAPER'S
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