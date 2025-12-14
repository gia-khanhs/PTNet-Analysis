from temporalGraph import buildTempoGraph
from utilities.dataPath import saves
from utilities.multiProc import multiProcFunc

import heapq
import json
import time

stations, nodes, nodesById, edges = ([], [], [], [])
nStation = len(stations) - 1
nNode = len(nodes)

def dijkstra(s):
    

    return 0

def exportTable(mimicPaper = False):
    global stations, nodes, nodesById, edges, nStation, nNode
    stations, nodes, nodesById, edges = buildTempoGraph(mimicPaper)
    nStation = len(stations) - 1
    nNode = len(nodes)
