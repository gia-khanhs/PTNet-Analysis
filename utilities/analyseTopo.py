from .topoDataIO import loadGraph, loadWalkableNodes
from .topologicalGraph import topoEdge
from .dataPath import saves
from .getRoutes import walkDistance
from threading import Thread
import heapq
import json

nodes, adj = loadGraph()
N = len(nodes) - 1

INT_MAX = 2147483647

def dijkstra(s):
    shortest = [INT_MAX] * (N + 1)
    trace = [0] * (N + 1)

    shortest[s] = 0
    trace[s] = s
    pq = []
    heapq.heappush(pq, (shortest[s], s))

    while len(pq):
        d, u = heapq.heappop(pq)
        if d > shortest[u]: continue

        for edge in adj[u]:
            v = edge.destination
            w = edge.travelTime
            
            if d + w < shortest[v]:
                shortest[v] = d + w
                trace[v] = u
                heapq.heappush(pq, (shortest[v], v))

    return (shortest, trace)

def exportTable4():
    #Building shortest-path tree
    global N, nodes, adj
    if not N:
        nodes, adj = loadGraph()
        N = len(nodes) - 1
    walkableNodes = loadWalkableNodes()

    totalPasses = [0] * (N + 1)
    geoDis = [{} for i in range (N + 1)]

    def runChunk(l, r):
        for s in range(l, r):
            shortest, trace = dijkstra(s)
        
            topoSort = [(shortest[i], i) for i in range(1, N + 1) if shortest[i] != INT_MAX]
            topoSort.sort()
            passes = [0] * (N + 1)

            for i in range(len(topoSort) - 1, -1, -1):
                nodeId = topoSort[i][1]
                parent = trace[nodeId]

                #the path is only counted when the distance between the stop pair is longer than walking distance
                if walkableNodes[parent].get(nodeId) == None: passes[nodeId] += 1
                totalPasses[nodeId] += passes[nodeId]
                passes[parent] += passes[nodeId]

            #add shortest paths between nodes within walking distance
            for destination in walkableNodes[s]:
                totalPasses[s] += 1
                totalPasses[int(destination)] += 1

    runChunk(1, N + 1)
     #======Multi-threading=====
    '''
    nThreads = 4
    chunkSize = int(N / nThreads)
    chunk = []
    preR = 0
    for i in range(nThreads):
        if i == nThreads - 1: chunk.append((preR + 1, N + 1))
        else: 
            chunk.append((preR + 1, preR + 1 + chunkSize))
            preR = preR + 1 + chunkSize

    threads = []
    for i in range(nThreads):
        l, r = chunk[i]
        thread = Thread(target=runChunk, args=(l, r))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    #==================================
    '''

    passCnt = []
    for i in range(1, N + 1):
        passCnt.append((totalPasses[i], nodes[i]['name'], nodes[i]['address'], nodes[i]['id']))
        
    passCnt.sort(reverse = True)

    print("====Reproduced table 4====")
    toPrint = []
    for node in passCnt[:10]:
        toPrint.append(str(round(100 * node[0] / ((N - 1) * (N - 2)), 2)) + "% - " + node[1] + " - " + node[2] + " (stop ID " + str(node[3]) + ")")
    
    table4 = ""
    for info in toPrint:
        print(info)
        table4 = table4 + info + "\n"
    print("==========================")

    # with open(saves + "passCount.json", 'w', encoding = 'utf-8') as file:
    #     json.dump(passCnt, file, indent = 4, ensure_ascii = False)
    #     file.close()
    with open(saves + "table4.txt", 'w', encoding = 'utf-8') as file:
        file.write(table4)
        file.close()
