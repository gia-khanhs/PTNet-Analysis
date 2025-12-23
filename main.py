from utilities.topoDataIO import saveTopoGraph, loadTopoGraph, saveNLoadTopoGraph, saveWalkableNodes, loadWalkableNodes, saveNLoadWalkableNodes
from utilities.topologicalGraph import buildLGraph, buildTopoGraph, getWalkableNodes
from utilities.analyseTopo import exportTable4

from utilities.tempoDataIO import saveTempoGraph
from utilities.temporalGraph import buildTransitGraph, buildWaitingEdge, buildWalkAndWaitEdge, buildTempoGraph
from utilities.analyseTempo import graphInTime, exportTempoTable

import time
import psutil, os

if __name__ == "__main__": #multiprocessing guard
    # tracemalloc.start()
    start_time = time.time()


    '''================================================================='''
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

    '''================================================================='''

    # ============Temporal Graph==========
    #=====Built from the topograph with 4342 nodes
    # tempoGraph = buildTempoGraph()

    #=====Built from the topograph matching paper's
    # tempoGraph = buildTempoGraph(mimicPaper)
    # exportTempoTable(25200, 25200 + 10 * 60, mimicPaper) #25200 = 7:00 am => 7:00-7:10
    # exportTempoTable(25200, 25200 + 20 * 60, mimicPaper) # 7:00 => 7:20

    from utilities.analyseTempo import revGraphInTime, multisrcBfs01
    multisrcBfs01()

    # End the main code
    '''================================================================='''

    end_time = time.time()

    print("Time elapsed:", round(end_time - start_time, 2), "s")
    process = psutil.Process(os.getpid())
    print("Process memory used:", round(process.memory_info().rss / 1024**2, 2), "MB")