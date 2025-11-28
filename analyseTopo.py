from topoDataIO import loadGraph
from utilities.topologicalGraph import topoEdge
from utilities.dataPath import saves
from utilities.getRoutes import walkDistance
from geojson import Feature, Point
from turfpy import measurement
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
    totalPasses = [0] * (N + 1)
    geoDis = [{} for i in range (N + 1)]
    for s in range(1, N + 1):
        shortest, trace = dijkstra(s)
    
        topoSort = [(shortest[i], i) for i in range(1, N + 1) if i != s and shortest[i] != INT_MAX]
        topoSort.sort()
        passes = [0] * (N + 1)

        srcNode = nodes[s]

        for i in range(len(topoSort) - 1, -1, -1):
            nodeId = topoSort[i][1]
            destNode = nodes[nodeId]
            parent = trace[nodeId]

            sNode, lNode = min(nodeId, parent), max(nodeId, parent)
            if geoDis[sNode].get(lNode): tmpDis = geoDis[sNode][lNode] 
            else:
                tmpDis = measurement.distance(srcNode["pos"], destNode["pos"]) * 1000
                geoDis[sNode][lNode] = tmpDis
            
            #the path is only counted when the distance between the stop pair is longer than walking distance
            totalPasses[nodeId] += passes[nodeId]
            if tmpDis > walkDistance: passes[nodeId] += 1
            passes[parent] += passes[nodeId]

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

    with open(saves + "passCount.json", 'w', encoding = 'utf-8') as file:
        json.dump(passCnt, file, indent = 4, ensure_ascii = False)
    with open(saves + "table4.txt", 'w', encoding = 'utf-8') as file:
        file.write(table4)
