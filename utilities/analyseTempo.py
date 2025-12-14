from .temporalGraph import buildTempoGraph
from .tempoDataIO import saveAnalysingGraph, loadAnalysingGraph, saveNLoadAnalysingGraph
from .dataPath import saves
from .multiProc import multiProcFunc

from collections import deque
import json
import time
import bisect

INT_MAX = 2147483647

stations, nodes, nodesById, edges = ([], [], [], [])
nStation = len(stations) - 1
nNode = len(nodes)
isMimic = None

#==== var to run dijkstra
#nodes
dNodes, dEdges = loadAnalysingGraph()
dStations = []
dNodesByStationId = ([[] for i in range(4350 + 1)], [[] for j in range(4350 + 1)])

def bfs01(source, dest): #special case of dijkstra & bfs: 0/1 bfs
    global dEdges

    transfer = [INT_MAX] * (len(dNodes) + 1)
    transfer[source] = 0
    trace = [0] * (len(dNodes) + 1)

    optimised = set()
    dq = deque([source])

    while dq:
        u = dq.popleft()
        
        if u == dest: #shortest path found
            path = [dest]
            tmp = trace[dest]

            while trace[tmp] != tmp:
                path.append(tmp)
                tmp = trace[tmp]

            return path

        if u in optimised: continue
        optimised.add(u)

        for v, w in dEdges[str(u)]:
            newCost = transfer[u] + w

            if newCost < transfer[v]:
                transfer[v] = newCost
                trace[v] = u
                if w == 0:
                    dq.appendleft(v)
                else:
                    dq.append(v)

    return []

def ensureGraphBuilt(mimicPaper = False):
    global stations, nodes, nodesById, edges, nStation, nNode, isMimic

    if isMimic != mimicPaper:
        stations, nodes, nodesById, edges = buildTempoGraph(mimicPaper)
        nStation = len(stations) - 1
        nNode = len(nodes)
        isMimic = mimicPaper

def graphInTime(tDesiredDep, tEnd = None, mimicPaper = False):
    ensureGraphBuilt(mimicPaper)
    global stations, nodes, nodesById, edges, nStation, nNode, isMimic

    if tEnd == None: #default: 3 hours
        tEnd = tDesiredDep + 3 * 3600

    toFind = (tDesiredDep, 0, 0, 0)
    l = bisect.bisect_left(nodes, tDesiredDep, key = lambda node: node[0])
    toFind = (tEnd, 0, 0, 0)
    r = bisect.bisect_right(nodes, tEnd, key = lambda node: node[0]) - 1

    newNodes = {}
    for i in range(l, r + 1):
        newNodes[i - l + 1] = nodes[i]

    newEdges = {}
    for u in range(l, r + 1):
        for v, w in edges[u]:
            if v < l or v > r: continue
            if not newEdges.get(u - l + 1): newEdges[u - l + 1] = []
            newEdges[u - l + 1].append((v - l + 1, w))

    print("Built graph in time window!")

    return (newNodes, newEdges)
        
    
def earliestADShortestPath(sourceStation, disStation): # 5-step algorithm mentioned in the paper
    for arrival in dNodesByStationId[0][sourceStation]: #step 1
        aTime, aRouteId, aNodeId = arrival

        for departure in dNodesByStationId[1][disStation]: #step 2
            if departure[0] > arrival[0]: break
            dTime, dRouteId, dNodeId = departure

            shortestPath = bfs01(dNodeId, aNodeId) #step 3

            if len(shortestPath) == 0: continue #step 4

            return shortestPath #step 5:D


def shortestPathPassCountWorker(rng):
    l, r = rng
    global stations, dStations, dNodes

    passes = [0] * len(stations)

    for sId in range(l, r + 1):
        s = dStations[sId]
        for d in dStations:
            if d == s: continue

            shortestPath = earliestADShortestPath(s, d)

            if shortestPath is not None:
                for i in shortestPath: passes[dNodes[i][2]] += 1

    return passes

def allPairShortestPathPassCount():
    global dStations

    totalPasses = [0] * (nStation + 1)

    workerPasses = multiProcFunc(shortestPathPassCountWorker, 0, len(dStations) - 1)

    for workerResult in workerPasses:
        for i in range(1, nStation + 1):
            totalPasses[i] += workerResult[i]

    return totalPasses

def exportTempoTable(tDesiredDep, tEnd = None, mimicPaper = False):
    global stations, nodes, nodesById, edges, nStation, nNode, isMimic
    ensureGraphBuilt(mimicPaper)

    if tEnd == None: #default: 3 hours
        tEnd = tDesiredDep + 3 * 3600

    global dNodes, dEdges, dStations
    dNodes, dEdges = saveNLoadAnalysingGraph(graphInTime(tDesiredDep, tEnd, mimicPaper))
    print("Graph saved for analysation!")
    
    dStations = set()
    for iNode, (time, routeId, stationId, event) in dNodes.items():
        dNodesByStationId[event][stationId].append((time, routeId, int(iNode)))
        dStations.add(stationId)
    
    dStations = list(dStations)

    print(dNodes)
    allPairShortestPathPassCount()

    return None
