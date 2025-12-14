from temporalGraph import buildTempoGraph
from utilities.dataPath import saves
from utilities.multiProc import multiProcFunc

import heapq
import json
import time

stations, nodes, nodesById, edges = ([], [], [], [])

