from topoDataIO import loadGraph
from utilities.topologicalGraph import topoEdge
from utilities.dataPath import saves
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
    totalPasses = [0] * (N + 1)
    for s in range(1, N + 1):
        shortest, trace = dijkstra(s)
    
        topoSort = [(shortest[i], i) for i in range(1, N + 1) if shortest[i] != INT_MAX]
        topoSort.sort()
        passes = [0] * (N + 1)

        for i in range(len(topoSort) - 1, -1, -1):
            nodeId = topoSort[i][1]
            parent = trace[nodeId]
            passes[nodeId] += 1
            totalPasses[nodeId] += passes[nodeId]
            passes[parent] += passes[nodeId]

    table4 = []
    for i in range(1, N + 1):
        table4.append((totalPasses[i], nodes[i]['name'], nodes[i]['address'], nodes[i]['id']))
        
    table4.sort(reverse = True)
    with open(saves + "table4.json", 'w', encoding = 'utf-8') as file:
        json.dump(table4, file, indent = 4, ensure_ascii = False)
