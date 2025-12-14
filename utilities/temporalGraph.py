from .getRoutes import allRouteInfo
from .dataPath import saves
from .topoDataIO import saveTopoGraph, buildLGraph, saveNLoadTopoGraph, loadWalkableNodes, saveNLoadWalkableNodes
from .getRoutes import dwellTime

import json
import time

maxWaitTime = 60 * 60
nRoute = 0

def getDeparture():
    depart = {}
    departKey = set()

    global nRoute
    for i, route in enumerate(allRouteInfo[:20]):
        if route['RouteNo'] in {"DL01", "72-1", "70-5", "61-4", "61-7"}: continue

        if route.get('timeTableIn') != None:
            for time in route['timeTableIn']:
                newDeparture = (i, 'InboundSeq')

                departKey.add(time)
                if depart.get(time) == None: depart[time] = [newDeparture]
                else: depart[time].append(newDeparture)
            nRoute += 1
        
        if route.get('timeTableOut') != None:
            for time in route['timeTableOut']:
                newDeparture = (i, 'OutboundSeq')

                departKey.add(time)
                if depart.get(time) == None: depart[time] = [newDeparture]
                else: depart[time].append(newDeparture)
            nRoute += 1

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
    routeSet = set()
    newRouteId = [{} for i in range(nRoute)]

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
                
                if not (routeId, seq) in routeSet:
                    newRouteId[routeId][seq] = len(routeSet)
                    routeSet.add((routeId, seq))

                newRId = newRouteId[routeId][seq] 

                if not isNewFirst: #only add arrivals of intermediate and last stations
                    newNode = (time, newRId, compactedId[station['StationId']], 0)
                    #time, (compactedRouteId, inbound/outbound), compactedStationId, 0/1: arrival/departure
                    #time, newRouteId, compactedStationId, 0/1: arrival/departure
                    nodes.append(newNode) #arrival node
                    curN = len(nodes) - 1
                    nodeIds.append(curN)
                    #=============================
                    transitEdges.append((curN - 1, curN))
                    #=============================
                else: isNewFirst = False

                if station != lastStation: #only add departures of intermediate and first stations
                    time += dwellTime
                    newNode = (time, newRId, compactedId[station['StationId']], 1)
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

def getNodesByStationId(mimicPaper = False): #Get nodes by compactedStationId
    stations, nodes, transitEdges = buildTransitGraph(mimicPaper)
    nNode = len(nodes) - 1
    nodesById = ([[] for i in range(nNode + 1)], [[] for j in range(nNode + 1)])
    #nodesById[0/1 = arrival/departure][compactedStationId]

    for iNode, node in enumerate(nodes):
        time, routeId, stationId, type = node
        nodesById[type][stationId].append((time, routeId, iNode))

    return (stations, nodes, nodesById, transitEdges)

def buildWaitingEdge(mimicPaper = False):
    stations, nodes, nodesById, transitEdges = getNodesByStationId(mimicPaper)
    waitingEdges = []
    nStations = len(stations)
    
    for stationId in range(1, nStations + 1): 
        arrivals = nodesById[0][stationId]
        departures = nodesById[1][stationId]
        maxI = len(arrivals) - 1
        maxJ = len(departures) - 1

        firstLarger = 0
        if min(maxI, maxJ) < 0: continue
        while firstLarger < maxJ and departures[firstLarger][0] <= arrivals[0][0]: firstLarger += 1

        for i, arriveNode in enumerate(arrivals): #looping through arrival nodes
            arriveTime, arriveRouteId, arriveNodeId = arriveNode  

            nextLarger = None
            #firstLarger is always the id of the departure node with time > current arrive node
            for j in range(firstLarger, maxJ + 1):
                if nextLarger is None and i != maxI and \
                    arrivals[i + 1][0] < departures[j][0]:\
                    nextLarger = j #To update firstLarger

                departTime, departRouteId, departNodeId = departures[j]

                if departTime > arriveTime + maxWaitTime:
                    if nextLarger is not None: break
                    else: continue #continue loop to find dep node with id > next arrival node
                    
                if arriveRouteId != departRouteId:
                    waitingEdges.append((arriveNodeId, departNodeId))

            if nextLarger is not None: firstLarger = nextLarger
            else: break #if the next arrival node is larger than every departure node, break
        
    print("==== Built temporal graph waiting edges ====")
    print("Waiting edge count: ", len(waitingEdges))
    print("============================================")
    return (stations, nodes, nodesById, transitEdges, waitingEdges)
    

def buildWalkAndWaitEdge(mimicPaper = False):
    stations, nodes, nodesById, transitEdges, waitingEdges = buildWaitingEdge(mimicPaper)

    walkNWaitEdges = []

    nStation = len(stations) - 1
    walkableNodes = loadWalkableNodes()

    if (mimicPaper and len(walkableNodes) < 4350) or (not mimicPaper and len(walkableNodes) > 4343):
        print("Trying to save nodes within walking distance!")
        walkableNodes = saveNLoadWalkableNodes(mimicPaper)

    for stationId in range(1, nStation + 1):
        arrivals = nodesById[0][stationId]
        maxI = len(arrivals) - 1

        for sDestStation in walkableNodes[stationId]:
            destStation = int(sDestStation)
            departures = nodesById[1][destStation]
            maxJ = len(departures) - 1
            
            tWalk = walkableNodes[stationId][sDestStation] 

            firstLarger = 0
            if min(maxI, maxJ) < 0: continue
            while firstLarger < maxJ and departures[firstLarger][0] < arrivals[0][0] + tWalk: firstLarger += 1

            for i, arriveNode in enumerate(arrivals): #looping through arrival nodes
                arriveTime, arriveRouteId, arriveNodeId = arriveNode  

                nextLarger = None
                #firstLarger is always the id of the departure node with time > current arrive node + walking time
                for j in range(firstLarger, maxJ + 1):
                    if nextLarger is None and i != maxI and \
                        arrivals[i + 1][0] < departures[j][0]:\
                        nextLarger = j #To update firstLarger

                    departTime, departRouteId, departNodeId = departures[j]

                    if departTime > arriveTime + maxWaitTime + tWalk:
                        if nextLarger is not None: break
                        else: continue #continue loop to find dep node with id > next arrival node
                        
                    if arriveRouteId != departRouteId:
                        walkNWaitEdges.append((arriveNodeId, departNodeId))

                if nextLarger is not None: firstLarger = nextLarger
                else: break #if the next arrival node is larger than every departure node, break

    print("==== Built temporal graph walking and waiting edges ====")
    print("Walking and waiting edge count: ", len(walkNWaitEdges))
    print("========================================================")

    return stations, nodes, nodesById, transitEdges, waitingEdges, walkNWaitEdges

def buildTempoGraph(mimicPaper = False):
    stations, nodes, nodesById, transitEdges, waitingEdges, walkNWaitEdges = buildWalkAndWaitEdge(mimicPaper)

    nNodes = len(nodes)
    edges = {}

    for u, v in transitEdges:
        if not edges.get(u): edges[u] = []
        edges[u].append((v, 0))
    
    #Transfer edge
    for u, v in waitingEdges:
        if not edges.get(u): edges[u] = []
        edges[u].append((v, 1))

    for u, v in walkNWaitEdges:
        if not edges.get(u): edges[u] = []
        edges[u].append((v, 1))

    return stations, nodes, nodesById, edges