from utilities.topologicalGraph import buildTopoGraph
from utilities.topologicalGraph import topoEdge
import json
import tracemalloc, time

def buildAndSave():
    topoGraph = buildTopoGraph()

    nodes = []
    edges = []

    #Create nodes data to save
    for node in topoGraph[0]:
        tmpNode = {"name": node.name, "address": node.address}
        if tmpNode == {"name": 0, "address": 0}: continue
        nodes.append(tmpNode)

    #Create edges data to save
    for origin in range(1, len(nodes) - 1):
        if not origin: continue
        
        for edge in topoGraph[1][origin]:
            tmpEdge = {"origin": origin, "destination": edge.destination, "distance": edge.distance, "travelTime": edge.travelTime}
            edges.append(tmpEdge)

    #Save the data of the graph
    graph = {"nodes": nodes, "edges": edges}
    with open("topoGraph.json", 'w', encoding = 'utf-8') as file:
        json.dump(graph, file, indent = 4, ensure_ascii = False)

def loadGraph():
    with open("topoGraph.json", 'r', encoding = 'utf-8') as file:
        data = file.read()
        data = json.loads(data)
        file.close()

    nodes = data["nodes"]
    adj = {i: [] for i in range(len(nodes))}

    for edge in data["edges"]:
        newEdge = topoEdge(edge["destination"], edge["distance"], edge["travelTime"])
        adj[edge["origin"]].append(newEdge)

    return (nodes, adj)

tracemalloc.start()
start_time = time.time()

#=================================================================
# Start the main code
'''
graph = loadGraph()
'''
# End the main code
#=================================================================

end_time = time.time()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Time elapsed: {end_time - start_time:.3f} s")
print(f"Current memory usage: {current / 10**6:.2f} MB; Peak: {peak / 10**6:.2f} MB")