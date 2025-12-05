from utilities.topoDataIO import saveGraph, loadGraph, saveWalkableNodes, loadWalkableNodes
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


# tracemalloc.start()
start_time = time.time()

#=================================================================
# Start the main code

#==========Topological Graph========
mimicPaper = True
# LGraph = buildLGraph()
# saveGraph(buildLGraph())
# LGraph = buildLGraph(mimicPaper)
saveGraph(buildLGraph(mimicPaper))
# topoGraph = buildTopoGraph()
# saveGraph(buildTopoGraph())
# nodes, edges = loadGraph()
exportTable4()
#===================================


# ============Temporal Graph==========
# buildTransitGraph()
# buildWaitingEdge()
#====================================


# End the main code
#=================================================================

end_time = time.time()

print("Time elapsed:", round(end_time - start_time, 2), "s")
process = psutil.Process(os.getpid())
print("Process memory used:", round(process.memory_info().rss / 1024**2, 2), "MB")