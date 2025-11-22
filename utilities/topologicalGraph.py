import json
from .dataPath import dataPath
from .getRoutes import allRouteInfo, allRouteStopSeq
from .hcmcRegion import inHcmc
#from .coords import geoPos
from turfpy import measurement
from geojson import Feature, Point

path = dataPath()

walkDistance = 300
walkSpeed = 1.3
dwellTime = 6

class topoNode:
    def __init__(self, name, address, pos, id):
        self.name = name
        self.address = address
        self.pos = pos
        self.id = id

    def pyout(self):
        print("Name: " + str(self.name) + " | Address: " + str(self.address))# + " | Pos: " + str(self.pos))

class topoEdge:
    def __init__(self, destination, distance, travelTime):
        self.destination = destination
        self.distance = distance
        self.travelTime = travelTime


def buildNodes():
    tmp = set()
    nodes = [topoNode("This is not a real node!", "Created so that the id starts at 1.", (0, 0), 0)]
    id = [0]
    compactedId = [0] * 7620 #The maximum id is 7617

    for route in allRouteStopSeq:
        #print(route)
        with open(route, 'r', encoding = 'utf-8') as file:
            data = file.read()
            data = json.loads(data)

            '''
            if data[0]['RouteId'] == 110: continue #Route 70-5
            if data[0]['RouteId'] == 335: continue #Route 72-1 
            if data[0]['RouteId'] == 87: continue  #Route 61-4
            if data[0]['RouteId'] == 89: continue #Route 61-7 
            '''
            if data[0]['RouteId'] in {110, 335, 87, 89}: continue;

            for i, station in enumerate(data): 
                newNode = station['StationId']

                if newNode in tmp: continue

                pos = Feature(geometry=Point((station['Lng'], station['Lat'])))

                if i == 0 or i == len(data) - 1\
                or station['StationDirection'] != data[i + 1]['StationDirection']\
                or station['StationDirection'] != data[i - 1]['StationDirection']:
                    if not inHcmc(pos): continue

                tmp.add(newNode)
                newNode = topoNode(station['StationName'], station['Address'], pos, station['StationId'])
                nodes.append(newNode)
                compactedId[station['StationId']] = len(id)
                id.append(station['StationId'])
            file.close()

    return (nodes, id, compactedId)

def buildLGraph():
    nodes, id, compactedId = buildNodes()

    N = len(nodes) - 1
    edges = {i: [] for i in range(1, N + 1)}
    adjMat = [{} for i in range(N + 1)]

    edgeSet = set()

    for route in allRouteInfo:
        if route['RouteNo'] in {"DL01", "72-1", "70-5", "61-4", "61-7"}: continue

        for sequence in ['InboundSeq', 'OutboundSeq']:
            origin = 0
            for station in route[sequence]:
                #The first station of the route
                if station['StationOrder'] == 0:
                    origin = compactedId[station['StationId']]
                    continue

                #Add edges (consecutive stops) to the graph
                destination = compactedId[station['StationId']]
                newEdge = topoEdge(destination, station['dist'], station['time'] + dwellTime)
                if not (origin, destination) in edgeSet and min(origin, destination) != 0:
                    edgeSet.add((origin, destination))
                    edges[origin].append(newEdge)
                    adjMat[origin][destination] = (newEdge.distance, newEdge.travelTime)

                origin = destination

    print("==== Built L-space graph attributes ====")
    print("Node count: " + str(N))
    sum = 0
    for i in range(1, N + 1):
        sum += len(edges[i])
    print("Edge count: " + str(sum))
    print("========================================")
    return (nodes, edges, adjMat, id, compactedId)
        



def buildTopoGraph():
    nodes, LEdges, adjMat, id, compactedId = buildLGraph()

    N = len(nodes) - 1
    edges = {i: [] for i in range(1, N + 1)}

    #Function to update the adjMat so that the graph is a single graph
    def updateEdge(origin, destination, distance, travelTime):
        e = adjMat[origin].get(destination)
        if e is None or travelTime < e[1]:
            adjMat[origin][destination] = [distance, travelTime]

    #============================================
    #Add edges between stops within walking distance to the graph
    for origin in range(1, N):
        originPos = nodes[origin].pos

        for destination in range(origin + 1, N + 1):
            destinationPos = nodes[destination].pos
            #distance = origin.pos.arcLen(destination.pos)
            distance = measurement.distance(originPos, destinationPos) * 1000
            
            if distance <= walkDistance:
                updateEdge(origin, destination, distance, distance / walkSpeed)
                updateEdge(destination, origin, distance, distance / walkSpeed)

            #Add edges to the graph
            if adjMat[origin].get(destination) != None: #If the edge exists
                newEdge = topoEdge(destination, adjMat[origin][destination][0], adjMat[origin][destination][1])
                edges[origin].append(newEdge)
            
            if adjMat[destination].get(origin) != None:
                newEdge = topoEdge(origin, adjMat[destination][origin][0], adjMat[destination][origin][1])
                edges[destination].append(newEdge)
            

            
    
    print("==== Built topological graph attributes ====")
    print("Node count: " + str(N))
    sum = 0
    for i in range(1, N + 1):
        sum += len(edges[i])
    print("Edge count: " + str(sum))
    print("============================================")
    return (nodes, edges) #(nodes, edges, id, compactedId)