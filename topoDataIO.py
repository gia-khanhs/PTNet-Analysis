from utilities.topologicalGraph import buildTopoGraph
import json

import tracemalloc, time

tracemalloc.start()
start_time = time.time()

# Start the main code
topoGraph = buildTopoGraph()
'''
nodes = []
edges = []

#Create nodes data to save
for node in topoGraph[0]:
    tmpNode = {"name": node.name, "address": node.address}
    if tmpNode == {"name": 0, "address": 0}: continue
    nodes.append(tmpNode)

#Create edges data to save
for origin in range(1, 4362):
    if not origin: continue
    
    for edge in topoGraph[1][origin]:
        tmpEdge = {"origin": origin, "destination": edge.destination, "distance": edge.distance, "travelTime": edge.travelTime}
        edges.append(tmpEdge)
    break

#Save the data of the graph
graph = {"nodes": nodes, "edges": edges}
with open("topoGraph.json", 'w', encoding = 'utf-8') as file:
    json.dump(graph, file, indent = 4, ensure_ascii = False)
'''
# End the main code

end_time = time.time()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Time elapsed: {end_time - start_time:.3f} s")
print(f"Current memory usage: {current / 10**6:.2f} MB; Peak: {peak / 10**6:.2f} MB")