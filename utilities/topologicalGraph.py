import json
from .dataPath import dataPath
from .getRoutes import allRouteInfo, allRouteStopSeq
from .coords import geoPos

path = dataPath()

walkDistance = 300
walkSpeed = 1.3
dwellTime = 6

class topoNode:
    def __init__(self, name, address, pos):
        self.name = name
        self.address = address
        self.pos = pos

    def pyout(self):
        print("Name: " + str(self.name) + " | Address: " + str(self.address))# + " | Pos: " + str(self.pos))

class topoEdge:
    def __init__(self, destination, distance, travelTime):
        self.destination = destination
        self.distance = distance
        self.travelTime = travelTime


def buildNodes():
    tmp = set()
    nodes = [topoNode("This is not a real node!", "Created so that the id starts at 1.", (0, 0))]
    id = [0]
    compactedId = [0] * 7620 #The maximum id is 7617

    for route in allRouteStopSeq:
        #print(route)
        with open(route, 'r', encoding = 'utf-8') as file:
            data = file.read()
            data = json.loads(data)

            if data[0]['RouteId'] == 110: continue #Route 70-5
            if data[0]['RouteId'] == 335: continue #Route 72-1  

            for station in data:
                newNode = station['StationId']
                if not newNode in tmp:
                    tmp.add(newNode)
                    newNode = topoNode(station['StationName'], station['Address'], geoPos(station['Lat'], station['Lng']))
                    nodes.append(newNode)

                    compactedId[station['StationId']] = len(id)
                    id.append(station['StationId'])

            file.close()

    return (nodes, id, compactedId)

def buildTopoGraph():
    nodes = buildNodes()

    N = len(nodes[0])
    edges = {i: [] for i in range(N)} #Adjacent list to store edges of 4362 nodes
    
    #Add edges to the graph
    tmp = set()

    for route in allRouteInfo:
        #Skipped routes
        if route['RouteNo'] == "DL01": continue
        if route['RouteNo'] == "72-1": continue
        if route['RouteNo'] == "70-5": continue

        preId = 0
        
        for station in route['InboundSeq']:
            #The first station of the route
            if station['dist'] == 0:
                preId = nodes[2][station['StationId']]
                continue

            #Add edges (consecutive stops) to the graph
            cId = nodes[2][station['StationId']]
            newEdge = topoEdge(cId, station['dist'], station['time'] + dwellTime)
            if not (preId, cId) in tmp:
                tmp.add((preId, cId))
                edges[preId].append(newEdge)
            preId = cId

        for station in route['OutboundSeq']:
            #The first station of the route
            if station['dist'] == 0:
                preId = nodes[2][station['StationId']]
                continue

            #Add edges (consecutive stops) to the graph
            cId = nodes[2][station['StationId']]
            newEdge = topoEdge(cId, station['dist'], station['time'] + dwellTime)
            if not (preId, cId) in tmp:
                tmp.add((preId, cId))
                edges[preId].append(newEdge)
            preId = cId
            

    #Add edges between stops that are in walk distance to the graph
    '''
    for u in range(1, len(nodes[0]) - 2):
        origin = nodes[0][u]

        for v in range(u + 1, len(nodes[0]) - 1):
            destination = nodes[0][v]
            distance = origin.pos.arcLen(destination.pos)

            if distance <= walkDistance:
                tmpEdge = topoEdge(v, distance, distance / walkSpeed)
                edges[u].append(tmpEdge)
                tmpEdge = topoEdge(u, distance, distance / walkSpeed)
                edges[v].append(tmpEdge)
    '''
    return (nodes[0], edges) #(nodes, edges, id, compactedId)