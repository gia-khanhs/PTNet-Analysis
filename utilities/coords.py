import math

EARTH_RADIUS = 6371000
PI = math.pi
EARTH_CIRCUMFRENCE = 2 * PI * EARTH_RADIUS

class point3D:
    def __init__(self, x, y, z):
        self.pos = (x, y, z)

    def distance(self, B):
        dx = self.pos[0] - B.pos[0]
        dy = self.pos[1] - B.pos[1]
        dz = self.pos[2] - B.pos[2]

        return math.sqrt(dx * dx + dy * dy + dz * dz)
    
    def angleAtOrigin(self, B):
        lenAB = self.distance(B)
        #c^2 = a^2 + b^2 - 2ab * cos
        #cos = (a^2 + b^2 - c^2) / 2ab
        cosine = (2 * EARTH_RADIUS * EARTH_RADIUS - lenAB * lenAB) / (2 * EARTH_RADIUS * EARTH_RADIUS)
        return math.acos(cosine)
        
class geoPos:
    def __init__(self, lat, lng):
        self.pos = (lat, lng)
    
    def toRadian(self):
        return geoPos(math.radians(self.pos[0]), math.radians(self.pos[1]))

    def toDegree(self):
        return geoPos(math.degrees(self.pos[0]), math.degrees(self.pos[1]))

    def geoPosTo3D(self): #the input is supposed to be a pair (lat, lng)
        lat = self.pos[0]
        lng = self.pos[1]

        x = 0
        y = 0
        z = math.sin(lat) * EARTH_RADIUS #the length of the secant line OA projected on Oz

        projLen = math.sqrt(EARTH_RADIUS * EARTH_RADIUS - z * z) #the length of the secant line OA when projected on the equatorial plane
        x = projLen * math.cos(lng)
        y = projLen * math.sin(lng)

        return point3D(x, y, z)
    
    def arcLen(self, B):
        pos1 = self.toRadian()
        pos1 = pos1.geoPosTo3D()

        pos2 = B.toRadian()
        pos2 = pos2.geoPosTo3D()

        angle = pos1.angleAtOrigin(pos2)
        len = EARTH_CIRCUMFRENCE * angle / (2 * PI)
        return len
    

'''
pos1 = geoPos(10.751253128051758,106.6525650024414)
pos2 = geoPos(10.75125313,106.65222168)

print(pos1.arcLen(pos2))
'''
