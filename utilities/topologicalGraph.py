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

            '''
            if data[0]['RouteId'] == 110: continue #Route 70-5
            if data[0]['RouteId'] == 335: continue #Route 72-1 
            if data[0]['RouteId'] == 87: continue  #Route 61-4
            if data[0]['RouteId'] == 89: continue #Route 61-7 
            '''
            if data[0]['RouteId'] in {110, 335, 87, 89}: continue;

            for station in data:
                newNode = station['Address']
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
    adj = [{} for i in range (N)] #Dictionary to take the minimum weight edge

    #============================================
    #Add consecutive edges in a route to the graph
    tmp = set()

    for route in allRouteInfo:
        preId = 0

        if route['RouteNo'] in {"DL01", "72-1", "70-5", "61-4", "61-7"}: continue

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
                #edges[preId].append(newEdge)
                adj[preId][cId] = (station['dist'], station['time'] + dwellTime)  

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
                #edges[preId].append(newEdge)
                adj[preId][cId] = (station['dist'], station['time'] + dwellTime)    
            
            preId = cId
    #============================================

    #============================================
    #Add edges between stops within walking distance to the graph
    def relax(u, v, dist_m, time_s):
        #Create or update u->v with a smaller travel time.
        cur = adj[u].get(v)
        if cur is None or time_s < cur[1]:
            adj[u][v] = [dist_m, time_s]
    
    for u in range(1, N - 2):
        origin = nodes[0][u]

        for v in range(u + 1, N - 1):
            destination = nodes[0][v]
            distance = origin.pos.arcLen(destination.pos)
            
            if distance <= walkDistance:
                #tmpEdge = topoEdge(v, distance, distance / walkSpeed)
                relax(u, v, distance, distance / walkSpeed)
                #edges[u].append(tmpEdge)
                #tmpEdge = topoEdge(u, distance, distance / walkSpeed) 
                relax(v, u, distance, distance / walkSpeed)
                #edges[v].append(tmpEdge)
            
            #Add edge to the return list
            if adj[u].get(v) != None: #If the edge exists
                tmpEdge = topoEdge(v, adj[u][v][0], adj[u][v][1])
                edges[u].append(tmpEdge)
            if adj[v].get(u) != None:
                tmpEdge = topoEdge(u, adj[v][u][0], adj[v][u][1])
                edges[v].append(tmpEdge)
    #Add edges between stops that are in walk distance to the graph
    
    print(len(nodes[0]))
    sum = 0
    for i in range(1, len(nodes[0]) - 1):
        sum += len(edges[i])
    print(sum)
    return (nodes[0], edges) #(nodes, edges, id, compactedId)