from temporalGraph import buildTempoGraph
from tempoDataIO import saveAnalysingGraph, loadAnalysingGraph, saveNLoadAnalysingGraph
from utilities.dataPath import saves
from utilities.multiProc import multiProcFunc

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
        
    

def exportTempoTable(tDesiredDep, tEnd = None, mimicPaper = False):
    global stations, nodes, nodesById, edges, nStation, nNode, isMimic
    ensureGraphBuilt(mimicPaper)

    if tEnd == None: #default: 3 hours
        tEnd = tDesiredDep + 3 * 3600

    global dNodes, dEdges
    dNodes, dEdges = saveNLoadAnalysingGraph(graphInTime(tDesiredDep, tEnd, mimicPaper))
    print("Graph saved for analysation!")

    return None
