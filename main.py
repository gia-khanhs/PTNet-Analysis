from topoDataIO import buildAndSave, loadGraph
from utilities.hcmcRegion import inHcmc
from turfpy import measurement
from geojson import Feature, Point

pt = Feature(geometry=Point((106.78744506835938,10.868183135986328)))
end = Feature(geometry=Point((106.65222168,10.75125313)))
print(inHcmc(pt))

#graph = loadGraph()

# graph[0] = node list
# graph[0][i].name/address = Attributes of the node ith

# graph[1] = graph's adjacency list
# graph[1][u] = a list of edges that connect u and graph[1][u][i]
# graph[1][u][i].destination/distance/travelTime = self-explainatory