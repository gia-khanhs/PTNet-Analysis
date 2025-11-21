from topoDataIO import loadGraph
from utilities.topologicalGraph import topoEdge
import heapq

nodes, adj = loadGraph()
N = len(nodes) - 1

INT_MAX = 2147483647

def dijkstra(s):
    shortest = [INT_MAX] * (N + 1)
    trace = [0] * (N + 1)

    shortest[s] = 0
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

def topoConnectivity():
    cnt = [0] * (N + 1)
    for i in range(1, N + 1):
        shortest, trace = dijkstra(i)
    return 0
