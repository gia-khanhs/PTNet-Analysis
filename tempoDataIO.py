from temporalGraph import buildTempoGraph
from utilities.dataPath import savesTempo

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