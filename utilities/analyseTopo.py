from .topoDataIO import loadTopoGraph, saveTopoGraph, saveNLoadTopoGraph
from .dataPath import saves, savesTopo
from .multiProc import multiProcFunc

import heapq
import json
import time

nodes, adj = loadTopoGraph()
N = len(nodes) - 1

INT_MAX = 2147483647

def dijkstra(s):
    shortest = [INT_MAX] * (N + 1)
    trace = [0] * (N + 1)

    shortest[s] = 0
    trace[s] = 0
    pq = []
    heapq.heappush(pq, (shortest[s], s))

    while len(pq):
        d, u = heapq.heappop(pq)
        if d != shortest[u]: continue

        for edge in adj[u].values():
            v = edge.destination
            w = edge.travelTime
            
            if shortest[u] + w < shortest[v]:
                shortest[v] = shortest[u] + w
                trace[v] = u
                heapq.heappush(pq, (shortest[v], v))

    return (shortest, trace)


def exportTable4Worker(rng):
    l, r = rng

    chunkPasses = [0] * (N + 1)
    for s in range(l, r + 1):
        shortest, trace = dijkstra(s)
    
        topoSort = [(shortest[i], i) for i in range(1, N + 1) if shortest[i] != INT_MAX]
        topoSort.sort()
        passes = [0] * (N + 1)

        for i in range(len(topoSort) - 1, -1, -1):
            nodeId = topoSort[i][1]
            parent = trace[nodeId]

            passes[nodeId] += 1
            passes[parent] += passes[nodeId]
            chunkPasses[nodeId] += passes[nodeId]

    return chunkPasses

def exportTable4(mimicPaper = False):
    from .topologicalGraph import buildLGraph
    #Building shortest-path tree
    global N, nodes, adj
    if not N or (mimicPaper and len(nodes) < 4350) or (not mimicPaper and len(nodes) > 4343):
            nodes, adj = saveNLoadTopoGraph(mimicPaper)
            N = len(nodes) - 1
    # walkableNodes = loadWalkableNodes()

    totalPasses = [0] * (N + 1)
    geoDis = [{} for i in range (N + 1)]

    passesWorkers = multiProcFunc(exportTable4Worker, 1, N)
    for passes in passesWorkers:
        for id, cnt in enumerate(passes): totalPasses[id] += cnt

    sortedPass = []
    for i in range(1, N + 1):
        sortedPass.append((totalPasses[i], round(100 * totalPasses[i] / ((N - 1) * (N - 2)), 2), nodes[i]['name'], nodes[i]['address'], nodes[i]['id']))
        
    sortedPass = sorted(sortedPass, key=lambda x:(-x[0], x[2]))

    print("====Reproduced table 4====")
    toPrint = []
    for node in sortedPass[:10]:
        toPrint.append(str(round(100 * node[0] / ((N - 1) * (N - 2)), 2)) + "% - " + node[2] + " - " + node[3] + " (stop ID " + str(node[4]) + ")")
    
    table4 = ""
    for info in toPrint:
        print(info)
        table4 = table4 + info + "\n"
    print("==========================")

    with open(savesTopo + "passCount - " + str(len(nodes) - 1) + " nodes.json", 'w', encoding = 'utf-8') as file:
        json.dump(sortedPass, file, indent = 4, ensure_ascii = False)
        file.close()
    with open(savesTopo + "table4 - " + str(len(nodes) - 1) + " nodes.txt", 'w', encoding = 'utf-8') as file:
        file.write(table4)
        file.close()
