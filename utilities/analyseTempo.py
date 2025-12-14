from .topoDataIO import loadStation
from .temporalGraph import buildTempoGraph
from .tempoDataIO import saveAnalysingGraph, loadAnalysingGraph, saveNLoadAnalysingGraph, loadFromFile, saveNLoadFile
from .dataPath import saves, savesTempo
from .multiProc import multiProcFunc

from collections import deque
import multiprocessing
import json
import time
import bisect

INT_MAX = 2147483647

stations = loadStation()
dummyStations, nodes, nodesById, edges = ([], [], [], [])
nStation = len(stations) - 1
nNode = len(nodes)
isMimic = None

#==== var to run dijkstra
#nodes
dNodes, dEdges = loadAnalysingGraph()
dStations = loadFromFile("analysingStations")
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

        for v, w in dEdges.get(str(u), []):
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
        
    
def earliestADShortestPath(sourceStation, desStation): # 5-step algorithm mentioned in the paper
    for arrival in dNodesByStationId[0][desStation]: #step 1
        aTime, aRouteId, aNodeId = arrival

        for departure in dNodesByStationId[1][sourceStation]: #step 2
            if departure[0] > arrival[0]: break
            dTime, dRouteId, dNodeId = departure

            shortestPath = bfs01(dNodeId, aNodeId) #step 3

            if len(shortestPath) == 0: continue #step 4

            return shortestPath #step 5:D


def shortestPathPassCountWorker(rng):
    l, r = rng

    global stations, dStations, dNodes, dNodesByStationId

    for iNode, (time, routeId, stationId, event) in dNodes.items():
        dNodesByStationId[event][stationId].append((time, routeId, int(iNode)))
    
    passes = [0] * len(stations)

    for sId in range(l, r + 1):
        s = dStations[sId]
        for d in dStations:
            if d == s: continue

            shortestPath = earliestADShortestPath(s, d)

            if shortestPath is not None:
                for i in shortestPath:
                    passes[dNodes[str(i)][2]] += 1


    return passes

def allPairShortestPathPassCount():
    global dStations

    totalPasses = [0] * (nStation + 1)

    workerPasses = multiProcFunc(shortestPathPassCountWorker, 0, len(dStations) - 1, int(3 * multiprocessing.cpu_count() / 4 + 1))

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
    dStations = saveNLoadFile(dStations, "analysingStations")

    totalPasses = allPairShortestPathPassCount()

    sortedPass = []
    N = len(dStations)

    for strI in range(len(stations)):
        i = int(strI)
        if totalPasses[i] == 0: continue
        sortedPass.append((totalPasses[i], round(100 * totalPasses[i] / ((N - 1) * (N - 2)), 2), stations[i]['name'], stations[i]['address'], stations[i]['id']))
        
    sortedPass = sorted(sortedPass, key=lambda x:(-x[0], x[2]))

    msg = "====Reproduced table in " + str(tDesiredDep) + "-" + str(tEnd) + "===="
    print(msg)
    toPrint = []
    for stations in sortedPass[:10]:
        toPrint.append(str(round(100 * stations[0] / ((N - 1) * (N - 2)), 2)) + "% - " + stations[2] + " - " + stations[3] + " (stop ID " + str(stations[4]) + ")")
    
    table = ""
    for info in toPrint:
        print(info)
        table = table + info + "\n"
    print('=' * len(msg))

    fileName = str(tDesiredDep) + "-" + str(tEnd) + (" - mimicPaper" if mimicPaper else "")

    with open(savesTempo + "passCount - " + fileName + ".json", 'w', encoding = 'utf-8') as file:
        json.dump(sortedPass, file, indent = 4, ensure_ascii = False)
        file.close()
    with open(savesTempo + "table - " + fileName + ".txt", 'w', encoding = 'utf-8') as file:
        file.write(table)
        file.close()