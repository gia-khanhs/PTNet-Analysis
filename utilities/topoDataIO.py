from .topologicalGraph import buildLGraph, buildNodes, getWalkableNodes
from .topologicalGraph import topoEdge
from .dataPath import saves
from geojson import Feature, Point
import json
import time

def saveTopoGraph(topoGraph): #topoGraph = buildLGraph()/buildTopoGraph()

    nodes = []
    edges = []
    #Create nodes data to save
    for node in topoGraph[0]:
        lng, lat  = node.pos.geometry.coordinates
        tmpNode = {"name": node.name, "address": node.address, "id": node.id, "pos": (lng, lat)}
        nodes.append(tmpNode)

    #Create edges data to save
    for origin in range(1, len(nodes)):
        if not origin: continue
        
        for edge in topoGraph[1][origin]:
            tmpEdge = {"origin": origin, "destination": edge.destination, "distance": edge.distance, "travelTime": edge.travelTime}
            edges.append(tmpEdge)

    #Save the data of the graph
    graph = {"nodes": nodes, "edges": edges}
    with open(saves + "stations.json", 'w', encoding = 'utf-8') as file:
        json.dump(nodes, file, indent = 4, ensure_ascii = False)
        file.close()
    with open(saves + "topoGraph.json", 'w', encoding = 'utf-8') as file:
        json.dump(graph, file, indent = 4, ensure_ascii = False)
        file.close()

def loadTopoGraph():
    try:
        with open(saves + "topoGraph.json", 'r', encoding = 'utf-8') as file:
            data = file.read()
            data = json.loads(data)
            file.close()
    except IOError:
        print("ERROR: Cannot find topoGraph.json, make sure the graph is saved!")
        return ([], [])

    nodes = data["nodes"]
    for node in nodes:
        node["pos"] = Feature(geometry=Point((node["pos"][0], node["pos"][1])))
        
    adj = {i: {} for i in range(len(nodes))}

    for edge in data["edges"]:
        newEdge = topoEdge(edge["destination"], edge["distance"], edge["travelTime"])
        adj[edge["origin"]][edge["destination"]] = newEdge

    return (nodes, adj)

def saveNLoadTopoGraph(mimicPaper = False):
    saveTopoGraph(buildLGraph(mimicPaper))
    time.sleep(0.1)
    return loadTopoGraph()


def saveWalkableNodes(walkableNode):
    # walkableNode = getWalkableNodes(mimicPaper)
    with open(saves + "walkableNodes.json", 'w', encoding = 'utf-8') as file:
        json.dump(walkableNode, file, indent = 4, ensure_ascii = False)
        file.close()

def loadWalkableNodes():
    try:
        with open(saves + "walkableNodes.json", 'r', encoding = 'utf-8') as file:
            walkableNodes = file.read()
            walkableNodes = json.loads(walkableNodes)
            file.close()
    except IOError:
        print("ERROR: Cannot find walkableNodes.json, make sure the file is saved!")
        return []
    
    return walkableNodes

def saveNLoadWalkableNodes(mimicPaper = False):
    saveWalkableNodes(getWalkableNodes(mimicPaper))
    time.sleep(0.1)
    return loadWalkableNodes