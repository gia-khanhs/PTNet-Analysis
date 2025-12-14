from .temporalGraph import buildTempoGraph, getStations
from .dataPath import savesTempo

from geojson import Feature, Point

import json
import time

def saveTempoGraph(tempoGraph):
    stations, nodes, nodesById, edges = tempoGraph

    with open(savesTempo + "stations.json", 'w', encoding = 'utf-8') as file:
        json.dump(stations, file, indent = 4, ensure_ascii = False)
        file.close()

    with open(savesTempo + "nodes.json", 'w', encoding = 'utf-8') as file:
        json.dump(nodes, file, indent = 4, ensure_ascii = False)
        file.close()
    
    with open(savesTempo + "nodesById.json", 'w', encoding = 'utf-8') as file:
        json.dump(nodesById, file, indent = 4, ensure_ascii = False)
        file.close()
    
    with open(savesTempo + "edges.json", 'w', encoding = 'utf-8') as file:
        json.dump(edges, file, indent = 4, ensure_ascii = False)
        file.close()

def loadTempoGraph():
    stations = []
    nodes = []
    nodesById = []
    edges = []

    try:
        with open(savesTempo + "stations.json", 'r', encoding = 'utf-8') as file:
            stations = file.read()
            stations = json.loads(stations)
            file.close()
    except IOError:
        print("ERROR: Cannot find stations.json, make sure the graph is saved!")
        return ([], [], [], [])
    
    try:
        with open(savesTempo + "nodes.json", 'r', encoding = 'utf-8') as file:
            nodes = file.read()
            nodes = json.loads(nodes)
            file.close()
    except IOError:
        print("ERROR: Cannot find nodes.json, make sure the graph is saved!")
        return ([], [], [], [])
    
    try:
        with open(savesTempo + "nodesById.json", 'r', encoding = 'utf-8') as file:
            nodesById = file.read()
            nodesById = json.loads(nodesById)
            file.close()
    except IOError:
        print("ERROR: Cannot find nodesById.json, make sure the graph is saved!")
        return ([], [], [], [])
    
    try:
        with open(savesTempo + "edges.json", 'r', encoding = 'utf-8') as file:
            edges = file.read()
            edges = json.loads(edges)
            file.close()
    except IOError:
        print("ERROR: Cannot find edges.json, make sure the graph is saved!")
        return ([], [], [], [])
    
    return (stations, nodes, nodesById, edges)

def saveAnalysingGraph(analysingGraph):
    nodes, edges = analysingGraph
    toSave = {"nodes": nodes, "edges": edges}

    with open(savesTempo + "analysingGraph.json", 'w', encoding = 'utf-8') as file:
        json.dump(toSave, file, indent = 4, ensure_ascii = False)
        file.close()

def loadAnalysingGraph():
    nodes = []
    edges = []

    try:
        with open(savesTempo + "analysingGraph.json", 'r', encoding = 'utf-8') as file:
            data = file.read()
            data = json.loads(data)
            nodes = data["nodes"]
            edges = data["edges"]
            file.close()
        
        return (nodes, edges)
    except IOError:
        print("ERROR: Cannot find analysingGraph.json, make sure the graph is saved!")
        return ([], [])
    
def saveNLoadAnalysingGraph(analysingGraph):
    saveAnalysingGraph(analysingGraph)
    time.sleep(0.1)
    return loadAnalysingGraph()

def saveToFile(data, name):
    with open(savesTempo + name + ".json", 'w', encoding = 'utf-8') as file:
        json.dump(data, file, indent = 4, ensure_ascii = False)
        file.close()

def loadFromFile(name):
    try:
        with open(savesTempo + name + ".json", 'r', encoding = 'utf-8') as file:
            data = file.read()
            data = json.loads(data)
            file.close()
        
        return data
    except IOError:
        print("ERROR: Cannot find " + name + ".json!")
        return ([], [])
    
def saveNLoadFile(data, name):
    saveToFile(data, name)
    time.sleep(0.1)
    return loadFromFile(name)