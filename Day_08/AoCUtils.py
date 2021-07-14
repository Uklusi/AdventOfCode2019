from copy import copy, deepcopy
import hashlib
from itertools import product, permutations
from collections import namedtuple
import numpy as np
from functools import partial, cache
from queue import PriorityQueue

inf = float("inf")
_XY = namedtuple("_XY", ["x", "y"])

def dirToNum(direction):

    if isinstance(direction, int):
        return direction % 4
    
    direction = direction.upper()
    if direction in ["N", "U", "^", "0"]:
        return 0
    elif direction in ["E", "R", ">", "1"]:
        return 1
    elif direction in ["S", "D", "V", "2"]:
        return 2
    elif direction in ["W", "L", "<", "3", "-1"]:
        return 3
    else:
        raise(Exception(f"DirectionError: {direction}"))

# Vector class: used to indicate offsets  
class Vector():
    def __init__(
        self,
        x = 0,
        y = 0,
        reverseY = False
    ):
        self.upVertSign = -1 if reverseY else 1
        self.reverseY = reverseY

        self.vx = x
        self.vy = y
                
    def __add__(self, other):
        return Vector(
            self.vx + other.vx,
            self.vy + other.vy,
            reverseY = self.reverseY
        )
      
    def __sub__(self, other):
        return Vector(
            self.vx - other.vx,
            self.vy - other.vy,
            reverseY = self.reverseY
        )
    
    def __neg__(self):
        return Vector(
            -self.vx,
            -self.vy,
            reverseY=self.reverseY
        )

    def __rmul__(self, n):
        return Vector(n*self.vx, n*self.vy, reverseY=self.reverseY)
    
    def __mul__(self, n):
        return n * self
    
    def __hash__(self):
        return hash(self.stdcoords())
    
    def __eq__(self, other):
        return self.stdcoords() == other.stdcoords()

    def __gt__(self, other):
        (sx, sy, *_) = self.stdcoords()
        (ox, oy, *_) = other.stdcoords()
        sign = -self.upVertSign
        s = (sign * sy, sx)
        o = (sign * oy, ox)
        return s > o

    def __ge__(self, other):
        return self > other or self == other

    def __str__(self):
        (x, y) = self.coords()
        return f"<{x}, {y}>"

    def __repr__(self):
        return str(self)
      
    def stdcoords(self, inverted=False):
        if inverted:
            return (self.vy, self.vx)
        return (self.vx, self.vy)

    def coords(self, inverted=False):
        inverted = inverted ^ self.reverseY
        return self.stdcoords(inverted=inverted)

    def copy(self):
        return copy(self)
    
    def distance(self):
        return abs(self.vx) + abs(self.vy)

    def length(self):
        return ( (self.vx) ** 2 + (self.vy) ** 2 ) ** (1/2)

def VectorDir(direction, n=1, reverseY=False):
    upVertSign = -1 if reverseY else 1
    x = 0
    y = 0
    direction = dirToNum(direction)
    if direction % 2 == 0:
        y = n * upVertSign * (1 - direction)
    else:
        x = n * (2 - direction)
    return Vector(x, y, reverseY=reverseY)


# Position class
class Position():
    def __init__(
        self,
        x = 0,
        y = 0,
        reverseY = False
    ):
        self.x = x
        self.y = y
        self.reverseY = reverseY
        self.upVertSign = -1 if reverseY else 1

    def __add__(self, vector):
        return Position(
            self.x + vector.vx,
            self.y + vector.vy,
            reverseY = self.reverseY
        )
      
    def __sub__(self, other):
        if isinstance(other, Vector):
            return self + (-other)

        return Vector(
            self.x - other.x,
            self.y - other.y,
            reverseY = self.reverseY
        )

    # def __rmul__(self, n):
    #     return Position(n*self.x, n*self.y, reverseY = self.reverseY)
    
    # def __mul__(self, n):
    #     return n * self
    
    def __hash__(self):
        return hash(self.stdcoords())
    
    def __eq__(self, other):
        return self.stdcoords() == other.stdcoords()

    def __gt__(self, other):
        (sx, sy, *_) = self.stdcoords()
        (ox, oy, *_) = other.stdcoords()
        sign = -self.upVertSign
        s = (sign * sy, sx)
        o = (sign * oy, ox)
        return s > o

    def __ge__(self, other):
        return self > other or self == other

    def __str__(self):
        return str(self.coords())

    def __repr__(self):
        return str(self)

    def stdcoords(self, inverted=False):
        if inverted:
            return (self.y, self.x)
        return (self.x, self.y)

    def coords(self, inverted=False):
        inverted = inverted ^ self.reverseY
        return self.stdcoords(inverted=inverted)

    def copy(self):
        return copy(self)
    
    def adjacent(self, includeCorners=False):
        if includeCorners:
            return [self + Vector(i, j) for (i,j) in product([-1,0,1], repeat=2) if (i,j) != (0,0)]

        return [self + VectorDir(direction=d) for d in [0,1,2,3] ]
    
    def distance(self, other=None):
        if other is None:
            other = Position(0,0)
        return (self - other).distance()

    def length(self, other=None):
        if other is None:
            other = Position(0,0)
        return (self - other).length()

def dirToName(direction):
    direction = dirToNum(direction)
    if direction == 0:
        return "U"
    elif direction == 1:
        return "R"
    elif direction == 2:
        return "D"
    elif direction == 3:
        return "L"

def dirToArrow(direction):
    direction = dirToNum(direction)
    if direction == 0:
        return "^"
    elif direction == 1:
        return ">"
    elif direction == 2:
        return "v"
    elif direction == 3:
        return "<"


class Agent(Position):
    def __init__(
        self,
        x = 0,
        y = 0,
        direction = 0,
        reverseY = False
    ):
        super().__init__(x, y, reverseY=reverseY)
        self.direction = dirToNum(direction)
    
    def __add__(self, vector):
        return Agent(
            self.x + vector.vx,
            self.y + vector.vy,
            direction = self.direction,
            reverseY = self.reverseY
        )
    
    def __hash__(self):
        raise(Exception("Class not hashable"))

    def turn(self, direction=1):
        if direction is None:
            return
        
        dirNum = dirToNum(direction)

        self.direction = (self.direction + dirNum) % 4
    
    def turnRight(self):
        self.turn(1)
    
    def turnLeft(self):
        self.turn(-1)
    
    def turnReverse(self):
        self.turn(2)
    
    def moveTo(self, target):
        self.x = target.x
        self.y = target.y
    
    def move(self, n=1, direction=None):
        if direction is None:
            direction = self.direction
        
        self.moveTo( self + VectorDir(n=n, direction=direction, reverseY=self.reverseY) )

    def position(self):
        return Position(self.x, self.y, reverseY=self.reverseY)


def _inbound(n, nmin, nmax):
    return max(min(n, nmax), nmin)

# maze characters
solid = "\u2588"
empty = " "
path = "·"

class MapPosition(Position):
    def __init__(
        self,
        x = 0,
        y = 0,
        reverseY = True,
        frame = None,
        xmin = -inf,
        xmax = inf,
        ymin = -inf,
        ymax = inf,
        occupied = lambda p: False
    ):
        super().__init__(
            x,
            y,
            reverseY = reverseY
        )
        if frame is not None:
            self.xmin = 0
            self.xmax = len(frame[0]) - 1
            self.ymin = 0
            self.ymax = len(frame) - 1 
        else:
            self.xmin = xmin
            self.xmax = xmax
            self.ymin = ymin
            self.ymax = ymax
        
        self._occupiedFunction = occupied

    def isOccupied(self):
        return self._occupiedFunction(self)
    
    def isEmpty(self):
        return not self.isOccupied()

    def __add__(self, vector):
        return MapPosition(
            self.x + vector.vx,
            self.y + vector.vy,
            reverseY = self.reverseY,
            xmin = self.xmin,
            xmax = self.xmax,
            ymin = self.ymin,
            ymax = self.ymax,
            occupied = self._occupiedFunction
        )
        
    def isInLimits(self):
        return (
            self.x == _inbound(self.x, self.xmin, self.xmax) and
            self.y == _inbound(self.y, self.ymin, self.ymax)
        )
    
    def adjacent(self, includeCorners=False):
        ret = super().adjacent(includeCorners=includeCorners)
        return [p for p in ret if p.isInLimits() and p.isEmpty()]


class MapAgent(MapPosition, Agent):
    def __init__(
        self,
        x = 0,
        y = 0,
        direction = 0,
        reverseY = True,
        frame = None,
        xmin = -inf,
        xmax = inf,
        ymin = -inf,
        ymax = inf,
        occupied = lambda p: False
    ):
        Agent.__init__(
            self,
            x,
            y,
            direction = direction,
            reverseY = reverseY
        )
        MapPosition.__init__(
            self,
            x,
            y,
            reverseY = reverseY,
            frame = frame,
            xmin = xmin,
            xmax = xmax,
            ymin = ymin,
            ymax = ymax,
            occupied = occupied
        )
        self.direction = dirToNum(direction)
    
    def __add__(self, vector):
        return MapAgent(
            self.x + vector.vx,
            self.y + vector.vy,
            reverseY = self.reverseY,
            direction = self.direction,
            xmin = self.xmin,
            xmax = self.xmax,
            ymin = self.ymin,
            ymax = self.ymax,
            occupied = self._occupiedFunction
        )
    
    def __hash__(self):
        raise(Exception("Class not hashable"))

    def move(self, n=1, direction=None):
        if direction is None:
            direction = self.direction
        if n != 1:
            for _ in range(n):
                self.move(n=1, direction=direction)
            return

        v = VectorDir(direction=direction, reverseY=self.reverseY)
        newpos = (self + v)
        if newpos.isEmpty() and newpos.isInLimits():
            super().move(n=1, direction=direction)

    def mapPosition(self):
        return MapPosition(
            self.x + vector.vx,
            self.y + vector.vy,
            reverseY = self.reverseY,
            xmin = self.xmin,
            xmax = self.xmax,
            ymin = self.ymin,
            ymax = self.ymax,
            occupied = self._occupiedFunction
        )
    

def _setDoubleSlice(key):
    if isinstance(key, tuple):
        y = key[0]
        x = key[1]
    else:
        y = key
        x = slice(None)
    if not isinstance(x, slice):
        x = slice(x, x+1 or None)
    if not isinstance(y, slice):
        y = slice(y, y+1 or None)
    return (y,x)

def _sliceToRange(item, minRange=None, maxRange=None):
    return range(item.start or minRange, item.stop or maxRange, item.step or 1)

class Map():
    def __init__(
            self,
            visual = lambda p: ".",
            frame = None,
            xmin = 0,
            xmax = 10,
            ymin = 0,
            ymax = 10
        ):
        self._visualFunction = visual

        if frame is not None:
            self.xmin = 0
            self.xmax = len(frame[0])
            self.ymin = 0
            self.ymax = len(frame) 
        else:
            self.xmin = xmin
            self.xmax = xmax + 1
            self.ymin = ymin
            self.ymax = ymax + 1

    def __getitem__(self, key):
        (yslice, xslice) = _setDoubleSlice(key)
        yrange = _sliceToRange(yslice, self.ymin, self.ymax)
        xrange = _sliceToRange(xslice, self.xmin, self.xmax)

        visualRepr = [[self._visualFunction(Position(x,y)) for x in xrange] for y in yrange]
        
        return Image(visualRepr) 

    def image(self):
        return self[:,:]
    
    def __str__(self):
        return str(self.image())

    def __repr__(self):
        return str(self)


class GameOfLife():
    def __init__(self, data, on="#", off="."):
        self.on = on
        self.off = off
        self.state = [[1 if c is on else 0 for c in s] for s in data]

    def __repr__(self):
        return "\n".join(["".join([solid if bit else empty for bit in s]) for s in self.state])

    def __str__(self):
        return self.__repr__()

    def _neighs(self, p):
        q = MapPosition(p.x, p.y, frame=self.state)
        return q.adjacent(includeCorners=True)
    
    def step(self):
        n = len(self.state)
        m = len(self.state[0])
        newstate = deepcopy(self.state)
        for i in range(n):
            for j in range(m):
                onNeighs = 0
                for p in self._neighs(Position(i,j)):
                    onNeighs += self.state[p.x][p.y]
                if self.state[i][j] and onNeighs in [2,3]:
                    newstate[i][j] = 1
                elif not self.state[i][j] and onNeighs == 3:
                    newstate[i][j] = 1
                else:
                    newstate[i][j] = 0
        self.state = newstate


class HexGrid():
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return HexGrid(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return HexGrid(self.x - other.x, self.y - other.y)

    def __rmul__(self, n):
        return HexGrid(n*self.x, n*self.y)
        
    def __mul__(self, n):
        return n * self
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __str__(self):
        return "Hex" + str((self.x, self.y))

    def __repr__(self):
        return str(self)
        
    def move(self, n, direction=None):
        if direction is None:
            raise(Exception("DirectionError: None"))
        direction = direction.upper()
        if direction in ["N", "U"]:
            self.x += 1
            self.y += 1
        elif direction in ["NE", "UR"]:
            self.x += 1
        elif direction in ["NW", "UL"]:
            self.y += 1
        elif direction in ["S", "D"]:
            self.x += -1
            self.y += -1
        elif direction in ["SE", "DR"]:
            self.y += -1
        elif direction in ["SW", "DL"]:
            self.x += -1
        else:
            raise(Exception(f"DirectionError: {direction}"))

    def stdcoords(self):
        return (self.x, self.y)
    
    def coords(self):
        return self.stdcoords()

    def copy(self):
        return copy(self)
    
    def adjacent(self):
        return [self + HexGrid(i,j) for (i,j) in [(1,0), (0,1), (1,1), (-1,0), (0,-1),(-1,-1)]]
    
    def distance(self, other=None):
        if other is None:
            other = HexGrid(0,0)
        x = self.x - other.x
        y = self.y - other.y
        if x * y <= 0:
            return abs(x) + abs(y)
        else:
            return max(abs(x), abs(y))


class Position3D():
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Position3D(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )
    
    def __sub__(self, other):
        return Position3D(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )
        
    def __rmul__(self, n):
        return Position3D(n*self.x, n*self.y, n*self.z) 
    
    def __hash__(self):
        return hash(self.coords())
    
    def __eq__(self, other):
        return self.coords() == other.coords()

    def __str__(self):
        return str(self.coords())

    def __repr__(self):
        return str(self)

    def stdcoords(self):
        return (self.x, self.y, self.z)

    def coords(self):
        return self.stdcoords()

    def copy(self):
        return copy(self)
    
    def adjacent(self, includeCorners=False):
        if includeCorners:
            return [self + Position3D(i,j,k) for (i,j,k) in product([-1,0,1], repeat=3) if (i,j,k) != (0,0,0)]

        return [self + Position3D(i,j,k) for (i,j,k) in [(-1,0,0), (1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)] ]

    def distance(self, other=None):
        if other is None:
            other = Position3D(0,0,0)
        s = self - other
        return sum(map(abs, [s.x, s.y, s.z]))


class Image():
    def __init__(self, image):
        self.pixels = np.array([r if isinstance(r, list) else list(r) for r in image])
    
    def __eq__(self, other):
        if self.shape != other.shape:
            return False
        return (self.pixels == other.pixels).all()

    def __add__(self, other):
        return Image(np.concatenate((self.pixels, other.pixels), axis=1))

    def __and__(self, other):
        return Image(np.concatenate((self.pixels, other.pixels), axis=0))
    
    def __getitem__(self, key):
        (yslice, xslice) = _setDoubleSlice(key)
        return Image(self.pixels[yslice, xslice])

    def __str__(self):
        return self.image()

    def __repr__(self):
        return self.image()

    def __hash__(self):
        return hash(self.image())

    @property
    def shape(self):
        return self.pixels.shape
    
    @property
    def ishape(self):
        s = self.shape
        return (s[1], s[0])
        
    @property
    def nshape(self):
        return _XY(*self.ishape)
        
    def copy(self):
        return Image(self.pixels)

    def image(self):
        return "\n".join(["".join([str(pixel) for pixel in row]) for row in self.pixels])
    
    def rotate(self, n=1, clockwise=False, copy=False):
        if clockwise:
            k = -n
        else:
            k = n
        i = np.rot90(self.pixels, k)
        if copy:
            return Image(i)
        else:
            self.pixels = i
    
    def flip(self, ud=False, copy=False):
        if ud:
            i = np.flipud(self.pixels)
        else:
            i = np.fliplr(self.pixels)
        if copy:
            return Image(i)
        else:
            self.pixels = i

    def rotations(self):
        i1 = self.rotate(0, copy=True)
        i2 = self.rotate(1, copy=True)
        i3 = self.rotate(2, copy=True)
        i4 = self.rotate(3, copy=True)
        return [i1, i2, i3, i4]

    def variations(self):
        i1 = self.flip(copy=True)
        return self.rotations() + i1.rotations()

def imageConcat(imageIter, vertical=False):
    if vertical:
        axis = 0
    else:
        axis = 1
    return Image(np.concatenate(imageIter, axis=axis))


class LinkedList():
    def __init__(self, data):
        self.data = data
        self.next = self
        self.prev = self
    
    def add(self, othData):
        other = LinkedList(othData)
        other.prev = self
        other.next = self.next
        self.next.prev = other
        self.next = other
        return other

    def delete(self):
        if self.next == self:
            del(self)
            return None
        else:
            self.next.prev = self.prev
            self.prev.next = self.next
            ret = self.next
            del(self)
            return ret

    def move(self, n=1):
        ret = self
        if n > 0:
            for _ in range(n):
                ret = ret.next
        elif n < 0:
            for _ in range(-n):
                ret = ret.prev
        return ret

    def __eq__(self, other):
        return self is other


# Easier md5
def md5(string):
    return hashlib.md5(string.encode()).hexdigest()


def aStar(start, goal, distanceFunction=lambda p, q: p.distance(q), includeCorners=False):

    estimate = partial(distanceFunction, goal)
    openSet = PriorityQueue()
    distance = {start: 0}
    openSet.put((estimate(start) + distance[start], start))

    while not openSet.empty():
        if goal in distance:
            # print(distance)
            return distance[goal]
        (_, current) = openSet.get()
        for p in current.adjacent(includeCorners=includeCorners):
            tentativeDistance = distance[current] + distanceFunction(current, p)
            if p not in distance or distance[p] > tentativeDistance:
                distance[p] = tentativeDistance
                openSet.put((estimate(p) + distance[p], p))
    return -1
