from .dataPath import dataPath
from .getRoutes import allRouteInfo, allRouteStopSeq, walkDistance, walkSpeed, dwellTime
from .hcmcRegion import inHcmc
from .multiProc import multiProcFunc

from turfpy import measurement
from geojson import Feature, Point

import json
import time
from threading import Thread

path = dataPath()

class topoNode:
    def __init__(self, name, address, pos, id):
        self.name = name
        self.address = address
        self.pos = pos
        self.id = id

    def pyout(self):
        print("Name: " + str(self.name) + " | Address: " + str(self.address))# + " | Pos: " + str(self.pos))

class topoEdge:
    def __init__(self, destination, distance, travelTime):
        self.destination = destination
        self.distance = distance
        self.travelTime = travelTime


def buildNodes(mimicPaper=False):
    O = Feature(geometry=Point((0, 0)))
    nodes = [topoNode("This is not a real node!", "Created so that the id starts at 1.", O, 0)]
    id = [0]
    compactedId = [0] * 7620 #The maximum id is 7617

    for route in allRouteInfo:
        if route['RouteNo'] in ["DL01", "72-1", "70-5", "61-4", "61-7"]: continue
        
        for seq in ['InboundSeq', 'OutboundSeq']:
            for station in route[seq]:
                #remove end nodes outside hcmc
                pos = Feature(geometry=Point((station['Lng'], station['Lat'])))
                if station == route[seq][0] or station == route[seq][-1]:
                    if (not mimicPaper or station['StationId'] > 7000) and not inHcmc(pos): continue
                
                #if is a new node
                if not compactedId[station['StationId']]:
                    newNode = topoNode(station['StationName'], station['Address'], pos, station['StationId'])
                    nodes.append(newNode)
                    compactedId[station['StationId']] = len(id)
                    id.append(station['StationId'])

    return (nodes, id, compactedId)

def buildLGraph(mimicPaper=False):
    nodes, id, compactedId = buildNodes(mimicPaper)

    N = len(nodes) - 1
    edges = {i: [] for i in range(1, N + 1)}
    # minAdjMat = [{} for i in range(N + 1)]
    meanAdjMat = [{} for i in range(N + 1)]

    edgeSet = set()

    for route in allRouteInfo:
        if route['RouteNo'] in ["DL01", "72-1", "70-5", "61-4", "61-7"]: continue

        for sequence in ['InboundSeq', 'OutboundSeq']:
            origin = 0
            for station in route[sequence]:
                #The first station of the route
                if station['StationOrder'] == 0:
                    origin = compactedId[station['StationId']]
                    continue

                #Add edges (consecutive stops) to the graph
                destination = compactedId[station['StationId']]
                newEdge = topoEdge(destination, station['dist'], station['time'])

                #Check if end points are in hcmc and if the edge has been added
                if min(origin, destination) != 0: #and not (origin, destination) in edgeSet:
                    edgeSet.add((origin, destination))
                    #Adding a new edge
                    if meanAdjMat[origin].get(destination) == None:
                        # minAdjMat[origin][destination] = (newEdge.distance, newEdge.travelTime)
                        meanAdjMat[origin][destination] = (newEdge.distance, newEdge.travelTime, 1)
                    else:
                        # if newEdge.travelTime < minAdjMat[origin][destination][1]:
                        #     minAdjMat[origin][destination] = (newEdge.distance, newEdge.travelTime)
                        
                        #Averaging the edge weight
                        d, t, cnt = meanAdjMat[origin][destination]
                        meanAdjMat[origin][destination] = (d + newEdge.distance, t + newEdge.travelTime, cnt + 1)
                        

                origin = destination
    
    for origin in range (1, N + 1):
        for destination in meanAdjMat[origin]:
            d, t, cnt = meanAdjMat[origin][destination]
            newEdge = topoEdge(destination, d / cnt, t / cnt)
            edges[origin].append(newEdge)

    print("==== Built L-space graph attributes ====")
    print("Node count:", N)
    sum = 0
    for i in range(1, N + 1):
        sum += len(edges[i])
    print("Edge count:", sum)
    print("========================================")

    return (nodes, edges, meanAdjMat, id, compactedId)
        

def getWalkableNodesWorker(rng):
    l, r = rng

    from .topoDataIO import loadTopoGraph
    nodes = loadTopoGraph()[0]

    N = len(nodes) - 1
    walkableNodes = [{} for i in range(N + 1)]

    for origin in range(l, r + 1):
        originPos = nodes[origin]['pos']

        for destination in range(origin + 1, N + 1):
            destinationPos = nodes[destination]['pos']
            #distance = origin.pos.arcLen(destination.pos)
            distance = measurement.distance(originPos, destinationPos) * 1000
            
            if distance <= walkDistance:
                walkableNodes[origin][destination] = round(distance / walkSpeed)
                walkableNodes[destination][origin] = round(distance / walkSpeed)

    return walkableNodes

def getWalkableNodes(mimicPaper = False):
    from .topoDataIO import loadTopoGraph, saveNLoadTopoGraph
    nodes = loadTopoGraph()[0]
    
    if not len(nodes) or (mimicPaper and len(nodes) < 4350) or (not mimicPaper and len(nodes) > 4343):
        nodes = saveNLoadTopoGraph(buildLGraph(mimicPaper))[0]

    N = len(nodes) - 1
    
    walkableNodes = [{} for i in range(N + 1)]
    
    walkableWorkers = multiProcFunc(getWalkableNodesWorker, N)

    for chunkResult in walkableWorkers:
        for origin in range(1, N + 1):
            for destination, distance in chunkResult[origin].items():
                walkableNodes[origin][destination] = distance

    print("=== getWalkableNodes ===")
    print("Successfully got nodes in walking distances")
    print("========================")
    return walkableNodes

def buildTopoGraph(mimicPaper = False):
    from .topoDataIO import loadWalkableNodes, saveTopoGraph

    nodes, LEdges, adjMat, id, compactedId = buildLGraph(mimicPaper)
    saveTopoGraph((nodes, LEdges))
    walkableNodes = loadWalkableNodes()

    N = len(nodes) - 1
    edges = {i: [] for i in range(1, N + 1)}

    #Function to update the adjMat so that the graph is a single graph
    def updateEdge(origin, destination, distance, travelTime):
        e = adjMat[origin].get(destination)
        if e is None or travelTime < e[1]:
            adjMat[origin][destination] = (distance, travelTime)

    #============================================
    #Add edges between stops within walking distance to the graph
    for origin in range(1, N + 1):
        for destination, distance in walkableNodes[origin].items():
            destination = int(destination)
            updateEdge(origin, destination, distance, distance / walkSpeed)
            updateEdge(destination, origin, distance, distance / walkSpeed)
    
    for origin in range(1, N + 1):
        for destination, weight in adjMat[origin].items():
            distance = weight[0]
            travelTime = weight[1]
            newEdge = topoEdge(destination, distance, travelTime)
            edges[origin].append(newEdge)
            
    print("==== Built topological graph attributes ====")
    print("Node count:", N)
    sum = 0
    for i in range(1, N + 1):
        sum += len(edges[i])
    print("Edge count:", sum)
    print("============================================")

    return (nodes, edges) #(nodes, edges, id, compactedId)