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
import tracemalloc, time

tracemalloc.start()
start_time = time.time()

#=================================================================
# Start the main code

#==========Topological Graph========
# LGraph = buildLGraph()
# saveGraph(buildLGraph())
# topoGraph = buildTopoGraph()
# saveGraph(buildTopoGraph())
# nodes, edges = loadGraph()
# exportTable4()
#===================================


# ============Temporal Graph==========
buildTransitGraph()
# buildWaitingEdge()
#====================================


# End the main code
#=================================================================

end_time = time.time()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Time elapsed: {end_time - start_time:.3f} s")
print(f"Current memory usage: {current / 10**6:.2f} MB; Peak: {peak / 10**6:.2f} MB")