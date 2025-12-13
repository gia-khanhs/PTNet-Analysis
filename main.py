from utilities.topoDataIO import saveTopoGraph, loadTopoGraph, saveNLoadTopoGraph, saveWalkableNodes, loadWalkableNodes, saveNLoadWalkableNodes
from utilities.topologicalGraph import buildLGraph, buildTopoGraph, getWalkableNodes
from temporalGraph import buildTransitGraph, buildWaitingEdge
#graph = loadGraph()

# graph[0] = node list
# graph[0][i].name/address/id = Attributes of the node ith

# graph[1] = graph's adjacency list
# graph[1][u] = a list of edges that connect u and graph[1][u][i]
# graph[1][u][i].destination/distance/travelTime = self-explainatory
from utilities.analyseTopo import exportTable4

import time
import psutil, os

if __name__ == "__main__": #multiprocessing guard
    # tracemalloc.start()
    start_time = time.time()


    #=================================================================
    # Start the main code

    mimicPaper = True

    #==========Topological Graph========
    #=====Graph with 4342 nodes
    # LGraph = buildLGraph()
    # saveTopoGraph(buildLGraph()) 
    # exportTable4()

    #=====Graph with 4350 nodes (Match paper's)
    # LGraph = buildLGraph(mimicPaper)
    # saveTopoGraph(buildLGraph(mimicPaper))
    # exportTable4(mimicPaper)

    # nodes, edges = loadTopoGraph()
    # ===================================

    # from utilities.test import lol
    # lol()

    # ============Temporal Graph==========
    #=====Built from the topograph with 4342 nodes
    # buildTransitGraph()
    # buildWaitingEdge()
    #=====Built from the topograph matching paper's
    # buildTransitGraph(mimicPaper)
    # buildWaitingEdge()
    # buildWalkingEdge_bf()
    #====================================


    # End the main code
    #=================================================================

    end_time = time.time()

    print("Time elapsed:", round(end_time - start_time, 2), "s")
    process = psutil.Process(os.getpid())
    print("Process memory used:", round(process.memory_info().rss / 1024**2, 2), "MB")