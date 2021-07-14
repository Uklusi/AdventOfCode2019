from __future__ import annotations
import hashlib
from typing import *
from collections.abc import Iterable
from io import StringIO
from copy import copy, deepcopy
from math import gcd
from functools import partial
from itertools import product
from queue import PriorityQueue
import re

import numpy as np

# Type aliases (for type hinting)
Numeric = Union[int, float]
MaybeSlice = Union[slice, int]
DirectionType = Union[str, int]
LogFileType = Union[str, StringIO]
DoubleSlice = Union[tuple[MaybeSlice, MaybeSlice], MaybeSlice]

T = TypeVar('T')

# Utility functions (debug, logging, prettify, etc...)

def rotations(l: Iterable[T]) -> list[Iterable[T]]:
    cycled = list(l) + list(l)
    n = len(l)
    return [cycled[i:i+n] for i in range(n)]

def stringify(l: Iterable[Any]) -> list[str]:
    return [str(o) for o in l]

def prettify(l: Iterable[Any]) -> str:
    return "\n".join( stringify(l) )

def sign(x: Numeric) -> int:
    return 1 if x > 0 else 0 if x == 0 else -1

def docstring(s: str) -> str:
    slist = s.strip().split("\n")
    slist = [l.strip() for l in slist]
    return prettify(s)

def printLogFactory(logFile: LogFileType) -> Callable[..., None]:

    def printLog(*t) -> None:
        """
        printLog function.
        Takes an arbitrary number of inputs and writes them to a log file
        If logFile is stdout, writes to stdout
        """

        if isinstance(logFile, str):
            print(*t)
        else:
            s = " ".join( stringify(t) )
            logFile.write(s)
            logFile.write("\n")

    return printLog

# Useful variables
inf = float("inf")
false = False
true = True
# maze characters
solid = "\u2588"
empty = " "
path = "·"


# Positioning classes

class _XY(NamedTuple):
    x: int
    y: int

def dirToNum(direction: DirectionType) -> int:
    """
    A function to read various direction inputs and return a standardized version
    (a number from 0 to 3, with up as 0 and proceeding clockwise)
    """

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

def dirToName(direction: DirectionType) -> str:
    """
    A function to read a direction and returning a standardized version
    (the letters U, R, D, L for up, right, down, left)
    """
    direction = dirToNum(direction)
    if direction == 0:
        return "U"
    elif direction == 1:
        return "R"
    elif direction == 2:
        return "D"
    elif direction == 3:
        return "L"

def dirToArrow(direction: DirectionType) -> str:
    """
    A function to read a direction and returning a standardized version
    (the arrows ^ > v < for up, right, down, left)
    """
    direction = dirToNum(direction)
    if direction == 0:
        return "^"
    elif direction == 1:
        return ">"
    elif direction == 2:
        return "v"
    elif direction == 3:
        return "<"


class _BaseR2Class():
    """
    Class used to implement common methods between Vector and Position.
    Implements hash, eq, gt (reading order: smaller y, greater x), ge,
    coords (using stdcoords method) copy, repr (using str method)
    Assuming stdcoords and __str__ methods and reverseY and upVertSign properties

    All classes deriving from _BaseR2Class can be compared, returning equal if they have the same coordinates
    """
    def __init__(self) -> None:
        self.reverseY = False
        self.upVertSign = False
    
    def __hash__(self) -> int:
        return hash(self.stdcoords())
    
    def __eq__(self: T, other: T) -> bool:
        return self.stdcoords() == other.stdcoords()

    def __gt__(self: T, other: T) -> bool:
        (sx, sy, *_) = self.stdcoords()
        (ox, oy, *_) = other.stdcoords()
        sign = -self.upVertSign
        s = (sign * sy, sx)
        o = (sign * oy, ox)
        return s > o

    def __ge__(self: T, other: T) -> bool:
        return self > other or self == other

    def stdcoords(self, inverted: bool = False) -> tuple[int, int]:
        return (self.x, self.y)

    def coords(self, inverted: bool = False) -> tuple[int, int]:
        inverted = inverted ^ self.reverseY
        return self.stdcoords(inverted=inverted)

    def __str__(self) -> str:
        return str(self.stdcoords())
        
    def __repr__(self) -> str:
        return str(self)
      
    def copy(self: T) -> T:
        return copy(self)
    

class Vector(_BaseR2Class):
    """
    Vector class: used to indicate offsets.
    Inherits from _BaseR2Class

    As a mathematician,I wanted to separate the affine plane Z^2 (class Position)
    and the vectorial space Z^2 underneath (class Vector)
    (Yes, I know Z is not a field and Position is technically a module, but let it slide)

    Syntax is Vector(x, y, reverseY=False). [Hashable]

    Vector has properties vx and vy, in orded to distinguish them from Position's x and y
    reverseY=True means that going down increases the y coordinate.
    It also makes the coordinates display as <y, x>, as if the coordinates are from a matrix.
    This way it is easier to find points when debugging.

    A vector has a distance() (Manhattan/L1 distance from <0,0>)
    and a length() (Euclidean/L2 distance from <0,0>)
    A vector can be standardized to a direction with the direction() method,
    returning a new vector with gcd(vx, vy) = 1.
    This is the preferred method for getting directions, as floating point comparisons are not perfect.
    However, in case a direction in the unit circle is needed,
    the direction method has a normalized parameter (default False)
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        reverseY: bool = False
    ) -> None:
        self.upVertSign = -1 if reverseY else 1
        self.reverseY = reverseY

        self.vx = x
        self.vy = y
                
    def __add__(self, other: Vector) -> Vector:
        return Vector(
            self.vx + other.vx,
            self.vy + other.vy,
            reverseY = self.reverseY
        )
      
    def __sub__(self, other: Vector) -> Vector:
        return Vector(
            self.vx - other.vx,
            self.vy - other.vy,
            reverseY = self.reverseY
        )
    
    def __neg__(self) -> Vector:
        return Vector(
            -self.vx,
            -self.vy,
            reverseY=self.reverseY
        )

    def __rmul__(self, n: int) -> Vector:
        return Vector(n*self.vx, n*self.vy, reverseY=self.reverseY)
    
    def __mul__(self, n: int) -> Vector:
        return n * self
    
    def __str__(self) -> str:
        (x, y) = self.coords()
        return f"<{x}, {y}>"

    def stdcoords(self, inverted: bool = False) -> tuple[int, int]:
        if inverted:
            return (self.vy, self.vx)
        return (self.vx, self.vy)

    def distance(self) -> int:
        return abs(self.vx) + abs(self.vy)

    def length(self) -> float:
        return ( (self.vx) ** 2 + (self.vy) ** 2 ) ** (1/2)

    def direction(self, normalized: bool = False) -> Vector:
        if self == Vector(0,0):
            return self
        elif normalized:
            d = self.length()
            return Vector(self.vx / d, self.vy / d)
        else:
            d = gcd(self.vx, self.vy)
            return Vector(self.vx // d, self.vy // d)

def VectorDir(direction: DirectionType, n: int = 1, reverseY: bool = False) -> Vector:
    """
    Helper function for class Vector
    Used to construct Vectors starting with a direction and the number of steps
    """
    upVertSign = -1 if reverseY else 1
    x = 0
    y = 0
    direction = dirToNum(direction)
    if direction % 2 == 0:
        y = n * upVertSign * (1 - direction)
    else:
        x = n * (2 - direction)
    return Vector(x, y, reverseY=reverseY)


class Position(_BaseR2Class):
    """
    Position class: used to indicate positions in the affine plane Z^2.
    Inherits from _BaseR2Class

    This class is complemented by the Vector class, which is a prerequisite for this class.

    Syntax is Position(x, y, reverseY=False). [Hashable]

    Position has properties x and y (the coordinates)
    reverseY=True means that going down increases the y coordinate.
    It also makes the coordinates display as (y, x), as if the coordinates are from a matrix.
    This way it is easier to find points when debugging.

    A Position can only be added with a Vector, not with other Positions.
    However, two Positions can be subtracted: p1 - p2 is the Vector v such that p2 + v == p1.

    A Position has a method adjacent(includeCorners=False), to return all adjacent Positions.
    If includeCorners is False, only the four positions sharing an edge are returned,
    while if it is True, the list also includes the 4 Positions sharing a vertex.
    A Position p has a distance(q=Position(0,0)) and a length(q=Position(0,0)),
    implemented as the corresponding method for the Vector (p - q)
    """
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        reverseY: bool = False
    ) -> None:
        self.x = x
        self.y = y
        self.reverseY = reverseY
        self.upVertSign = -1 if reverseY else 1

    def __add__(self, vector: Vector) -> Position:
        return Position(
            self.x + vector.vx,
            self.y + vector.vy,
            reverseY = self.reverseY
        )
    
    @overload
    def __sub__(self, other: Vector) -> Position:
        ...
    def __sub__(self, other: Position) -> Vector:
        ...
    def __sub__(self, other):
        if isinstance(other, Vector):
            return self + (-other)

        return Vector(
            self.x - other.x,
            self.y - other.y,
            reverseY = self.reverseY
        )

    def __str__(self) -> str:
        return str(self.coords())

    def stdcoords(self, inverted: bool = False) -> tuple[int, int]:
        if inverted:
            return (self.y, self.x)
        return (self.x, self.y)

    def adjacent(self: T, includeCorners: bool = False) -> list[T]:
        if includeCorners:
            return [self + Vector(i, j) for (i,j) in product([-1,0,1], repeat=2) if (i,j) != (0,0)]

        return [self + VectorDir(direction=d) for d in [0,1,2,3] ]
    
    def distance(self, other: Optional[Position] = None) -> int:
        if other is None:
            other = Position(0,0)
        return (self - other).distance()

    def length(self, other: Optional[Position] = None) -> float:
        if other is None:
            other = Position(0,0)
        return (self - other).length()


class Agent(Position):
    """
    Agent class: represents a movable entity in a 2D grid.
    Inherits from Position

    Syntax is Agent(x, y, direction=0, reverseY=False) [not hashable]

    Agent is mutable, so hash is not implemented.
    An agent can turnRight, turnLeft, turnReverse or turn(numOfRightTurns)
    An agent can also move, both in the direction he is currently facing and in another direction
    It also has a moveTo method, moving it to the position specified,
    and a position method, returning the Position correspondig to the agent's current position
    """
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        direction: DirectionType = 0,
        reverseY: bool = False
    ) -> None:
        super().__init__(x, y, reverseY=reverseY)
        self.direction = dirToNum(direction)
    
    def __add__(self, vector: Vector) -> Agent:
        return Agent(
            self.x + vector.vx,
            self.y + vector.vy,
            direction = self.direction,
            reverseY = self.reverseY
        )
    
    def __hash__(self) -> NoReturn:
        raise(Exception("Class not hashable"))

    def turn(self, direction: Optional[DirectionType] = 1) -> None:
        if direction is None:
            return
        
        dirNum = dirToNum(direction)

        self.direction = (self.direction + dirNum) % 4
    
    def turnRight(self) -> None:
        self.turn(1)
    
    def turnLeft(self) -> None:
        self.turn(-1)
    
    def turnReverse(self) -> None:
        self.turn(2)
    
    def moveTo(self, target: Position) -> None:
        self.x = target.x
        self.y = target.y
    
    def move(self, n: int = 1, direction: Optional[DirectionType] = None) -> None:
        if direction is None:
            direction = self.direction
        
        self.moveTo( self + VectorDir(n=n, direction=direction, reverseY=self.reverseY) )

    def position(self) -> Position:
        return Position(self.x, self.y, reverseY=self.reverseY)


def _inbound(n: int, nmin: Numeric, nmax: Numeric) -> int:
    """
    Helper function for MapPosition class
    """
    return max(min(n, nmax), nmin)

class MapPosition(Position):
    """
    MapPosition class: represents a Position on a possibly limited, possibly not fully traversable 2D plane.
    Inherits from Position

    Syntax is MapPosition(x, y, reverseY=True, frame=None, xmin=-inf, xmax=inf, ymin=-inf, xmax=inf, occupied=lambda p: False) [Hashable]

    A MapPosition assumes reverseY, contrary to the Position class, because usually a map is limited.
    The limits can be specified via frame (a view of the observable portion of the map),
    setting min to 0 and max to the effective max coordinate in the frame,
    or via the parameters. Occupied is a function that takes a MapPosition as input
    and returns whether or not that position is free (i.e an agent can move there).

    A MapPosition has a method isValid checking for validity, and also separate methods
    for the two ways a position can be invalid.
    MapPosition.adjacent only returns valid positions.
    """
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        reverseY: bool = True,
        frame: Optional[Iterable[Iterable[Any]]] = None,
        xmin: Numeric = -inf,
        xmax: Numeric = inf,
        ymin: Numeric = -inf,
        ymax: Numeric = inf,
        occupied: Callable[[Position], bool] = lambda p: False
    ) -> None:
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

    def __add__(self, vector: Vector) -> MapPosition:
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
        
    def isOccupied(self) -> bool:
        return self._occupiedFunction(self)
    
    def isEmpty(self) -> bool:
        return not self.isOccupied()

    def isInLimits(self) -> bool:
        return (
            self.x == _inbound(self.x, self.xmin, self.xmax) and
            self.y == _inbound(self.y, self.ymin, self.ymax)
        )
    
    def isValid(self) -> bool:
        return self.isEmpty() and self.isInLimits()
    
    def adjacent(self: T, includeCorners: bool = False) -> list[T]:
        ret = super().adjacent(includeCorners=includeCorners)
        return [p for p in ret if p.isValid()]


class MapAgent(MapPosition, Agent):
    """
    MapAgent class: represents an agent on a MapPosition.
    Inherits from MapPosition, Agent

    Syntax is MapAgent(x, y, direction=0, reverseY=True, frame=None, xmin=-inf, xmax=inf, ymin=-inf, xmax=inf, occupied=lambda p: False) [Not hashable]

    MapAgent inherits both from MapPosition and Agent, with the following changes:
    - A MapAgent has a mapPosition method returning the corresponding MapPosition
    - The move method now proceeds one step at a time and check for validity before moving.
    """
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        direction: DirectionType = 0,
        reverseY: bool = True,
        frame: Optional[Iterable[Iterable[Any]]] = None,
        xmin: Numeric = -inf,
        xmax: Numeric = inf,
        ymin: Numeric = -inf,
        ymax: Numeric = inf,
        occupied: Callable[[Position], bool] = lambda p: False
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
    
    def __add__(self, vector: Vector) -> MapAgent:
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
    
    def __hash__(self) -> NoReturn:
        raise(Exception("Class not hashable"))

    def move(self, n: int = 1, direction: Optional[DirectionType] = None) -> None:
        if direction is None:
            direction = self.direction
        if n != 1:
            for _ in range(n):
                self.move(n=1, direction=direction)
            return

        v = VectorDir(direction=direction, reverseY=self.reverseY)
        newpos = (self + v)
        if newpos.isValid():
            super().move(n=1, direction=direction)

    def mapPosition(self) -> MapPosition:
        return MapPosition(
            self.x,
            self.y,
            reverseY = self.reverseY,
            xmin = self.xmin,
            xmax = self.xmax,
            ymin = self.ymin,
            ymax = self.ymax,
            occupied = self._occupiedFunction
        )


def breakHexDirections(tape: str) -> list[str]:
    """
    Helper method to HexGrid: breaks a tape containing directions into a list of directions
    """
    directionsRE = re.compile("NE|NW|N|SE|SW|S|UL|UR|U|DL|DR|D")
    return directionsRE.findall(tape.upper())

class HexGrid(_BaseR2Class):
    """
    HexGrid class: a coordinate system for an hexagonal grid.
    Inherits from _BaseR2Class (except gt)

    Syntax: HexGrid(x, y) [Hashable]

    HexGrid is hashable while mutable: pay attention at what you do.
    
    HexGrid is basically an unholy union of Agent and Vector, but on an hex grid.
    This means that a position is represented as a 2d coordinate, but not all coordinates are acceptable.
    I am using a system like in figure, with axis NE and SW, with N and S as third axis.
    ·    |
    ·+y    +x
    ·    O
    ·-x    -y
    ·    |
    HexGrids can be summed and subtracted.
    They can also move using the directions above, or move to a specific position.
    HexGrids have an adjacent() method, returning six HexGrids,
    and a distance(other=HexGrid(0,0)) method, returning the minimum number of steps
    required to go from self to other
    """
    def __init__(self, x: int = 0, y: int = 0) -> None:
        super().__init__()
        self.x = x
        self.y = y

    def __add__(self, other: HexGrid) -> HexGrid:
        return HexGrid(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: HexGrid) -> HexGrid:
        return HexGrid(self.x - other.x, self.y - other.y)

    def __rmul__(self, n: int) -> HexGrid:
        return HexGrid(n*self.x, n*self.y)
        
    def __mul__(self, n: int) -> HexGrid:
        return n * self
    
    def __str__(self) -> str:
        return "Hex" + str(self.coords())
        
    def __gt__(self) -> NoReturn:
        raise(Exception("Class not ordered"))

    def move(self, n: int = 1, direction: Optional[str] = None) -> None:
        if direction is None:
            raise(Exception("DirectionError: None"))
        for _ in range(n):
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
    
    def moveFromTape(self, tape: list[str] = []) -> None:
        for direction in tape:
            self.move(direction=direction)

    def moveTo(self, target: HexGrid) -> None:
        self.x = target.x
        self.y = target.y

    def adjacent(self) -> list[HexGrid]:
        return [self + HexGrid(i,j) for (i,j) in [(1,0), (0,1), (1,1), (-1,0), (0,-1), (-1,-1)]]
    
    def distance(self, other: Optional[HexGrid] = None) -> int:
        if other is None:
            other = HexGrid(0,0)
        x = self.x - other.x
        y = self.y - other.y
        if x * y <= 0:
            return abs(x) + abs(y)
        else:
            return max(abs(x), abs(y))


class PositionNDim():
    """
    PositionNDim function: a n-dimensional Position-like class (n >= 3)

    Syntax: PositionNDim(x, y, z, ...) / PositionNDim([x, y, z, ...])

    PositionNDim is the translation of Vector and Position in a multidimensional environment.
    If self.numDimensions = 3 or 4 the class has the properties x, y, z (w). These are not to be modified.
    """
    def __init__(self, coordOrList: Union[int, Iterable[int]], *otherCoords: int) -> None:
        if isinstance(coordOrList, int):
            coords = (coordOrList, ) + otherCoords
            self.coordinates = tuple(coords)
        else:
            self.coordinates = tuple(coordOrList)
            
        self.numDimensions = len(self.coordinates)
        if self.numDimensions <= 4:
            self.x = self.coordinates[0]
            self.y = self.coordinates[1]
            self.z = self.coordinates[2]
            if self.numDimensions == 4:
                self.w = self.coordinates[3]


    def __add__(self, other: PositionNDim) -> PositionNDim:
        return PositionNDim(
            [self.coordinates[i] + other.coordinates[i] for i in range(self.numDimensions)]
        )
    
    def __sub__(self, other: PositionNDim) -> PositionNDim:
        return PositionNDim(
            [self.coordinates[i] - other.coordinates[i] for i in range(self.numDimensions)]
        )
        
    def __rmul__(self, n: int) -> PositionNDim:
        return PositionNDim( [n*c for c in self.coordinates] )
    
    def __hash__(self) -> int:
        return hash(self.coords())
    
    def __eq__(self, other: PositionNDim) -> bool:
        return self.coords() == other.coords()

    def __str__(self) -> str:
        return str(self.coords())

    def __repr__(self) -> str:
        return str(self)

    def stdcoords(self) -> tuple[int, ...]:
        return tuple(self.coordinates)

    def coords(self) -> tuple[int, ...]:
        return self.stdcoords()

    def copy(self) -> PositionNDim:
        return copy(self)
    
    def adjacent(self, includeCorners: bool = False) -> list[PositionNDim]:
        if includeCorners:
            return [
                self + PositionNDim(vals) for vals in product([-1,0,1], repeat=self.numDimensions) \
                if vals != (0,) * self.numDimensions
            ]

        return [
            self + PositionNDim(vals) for vals in \
            rotations([1] + [0] * (self.numDimensions - 1)) + \
            rotations([-1] + [0] * (self.numDimensions - 1))
        ]

    def distance(self, other: Optional[PositionNDim] = None) -> int:
        if other is None:
            other = PositionNDim( ([0] * self.numDimensions) )
        s = self - other
        return sum(map(abs, s.coordinates))
        
    def length(self, other: Optional[PositionNDim] = None) -> float:
        if other is None:
            other = PositionNDim( ([0] * self.numDimensions) )
        s = self - other
        return sum(map(lambda n: n**2, s.coordinates)) ** (1/2)


class GameOfLife():
    """
    GameOfLife class: a naive implementation of Conway's Game of Life in a limited space

    Syntax: GameOfLife(data, on="#", off=".") [Not hashable]

    GameOfLife is a representation of a set rectangular portion of the 2D plane as a Game of Life automaton.
    state is an iterable of fixed length iterables, representing a rectangle in the plane.
    It is assumed that the elements of state are either on or off,
    and that the positions outside the state are off and will always remain off.

    The step method progresses the automaton by a cycle,
    while the image(origChars=False) method returns a Image object representing the current state.
    If origChars is True, the characters used to init the object are used;
    Otherwise, the solid and empty characters are used 
    """
    def __init__(self, data: Iterable[Iterable[T]], on: T = "#", off: T =".") -> None:
        self.on = on
        self.off = off
        self.state = [[1 if c is on else 0 for c in s] for s in data]

    def __str__(self) -> str:
        return "\n".join(["".join([solid if bit else empty for bit in s]) for s in self.state])

    def __repr__(self) -> str:
        return str(self)

    def _neighs(self, p: Position) -> list[MapPosition]:
        q = MapPosition(p.x, p.y, frame=self.state)
        return q.adjacent(includeCorners=True)
    
    def step(self) -> None:
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

    def image(self, origChars: bool = False) -> Image:
        on = str(self.on) if origChars else solid
        off = str(self.off) if origChars else empty

        return Image([[on if n == 1 else off for n in l] for l in self.state])


# Image-based classes

def _setDoubleSlice(key:DoubleSlice) -> tuple[slice, slice]:
    """
    Helper method for overloading getitem with two dimensions
    """
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

def _sliceToRange(item:slice, minRange:Optional[int]=None, maxRange:Optional[int]=None) -> range:
    """
    Helper method to transform a slice object into a range object
    """
    return range(item.start or minRange, item.stop or maxRange, item.step or 1)

class Image():
    """
    Image class: Used to represent a 2D image using numpy arrays

    Syntax: Image(imageAsIter) [Hashable]

    Image takes an iterable of iterables (assumed rectangular)
    and uses it to construct a 2D numpy array called pixels.
    This array has shape image.shape = (y, x), having y rows and x columns.
    Properties image.ishape = (x, y) and image.nshape = {x: x, y: y} are also available.
    
    Images can be concatenated horizontally with + and vertically with &.
    Since this rebuilds the array every time, if in need to concatenate an entire row or column,
    please use the apposite helper function.

    str(image), and image.image() return a string, having newlines separating the lines
    and are thus ideal for printing to the terminal (or file)

    Slicing an image returns the corresponding part of the image as an Image object,
    selecting the rows first and the columns second.
    For example, image[0] is the first row, while image[:,0] is the first column.
    You can also use negative-based ranges.

    Images can be copied with image.copy(),
    rotated with image.rotate(n=1, clockwise=False, copy=False)
    and flipped with image.flip(ud=False, copy=False)

    The four rotations of an image are available using image.rotations(),
    while all the variations (rotated and flipped) are available using image.variations()
    """
    def __init__(self, image: Iterable[Iterable[Any]]) -> None:
        self.pixels: np.ndarray = np.array([r if isinstance(r, list) else list(r) for r in image])
    
    def __eq__(self, other: Image) -> bool:
        if self.shape != other.shape:
            return False
        return (self.pixels == other.pixels).all()

    def __add__(self, other: Image) -> Image:
        return Image(np.concatenate((self.pixels, other.pixels), axis=1))

    def __and__(self, other: Image) -> Image:
        return Image(np.concatenate((self.pixels, other.pixels), axis=0))
    
    def __getitem__(self, key: DoubleSlice) -> Image:
        (yslice, xslice) = _setDoubleSlice(key)
        return Image(self.pixels[yslice, xslice])

    def __str__(self) -> str:
        return self.image()

    def __repr__(self) -> str:
        return self.image()

    def __hash__(self) -> int:
        return hash(self.image())

    @property
    def shape(self) -> tuple[int, int]:
        return self.pixels.shape
    
    @property
    def ishape(self) -> tuple[int, int]:
        s = self.shape
        return (s[1], s[0])
        
    @property
    def nshape(self) -> _XY:
        return _XY(*self.ishape)
        
    def copy(self) -> Image:
        return Image(self.pixels)

    def image(self) -> str:
        return "\n".join(["".join(stringify(row)) for row in self.pixels])
    
    def rotate(self, n: int = 1, clockwise: bool = False, copy: bool = False) -> Optional[Image]:
        if clockwise:
            k = -n
        else:
            k = n
        i = np.rot90(self.pixels, k)
        if copy:
            return Image(i)
        else:
            self.pixels = i
    
    def flip(self, ud: bool = False, copy: bool = False) -> Optional[Image]:
        if ud:
            i = np.flipud(self.pixels)
        else:
            i = np.fliplr(self.pixels)
        if copy:
            return Image(i)
        else:
            self.pixels = i

    def rotations(self) -> list[Image]:
        i1 = self.rotate(0, copy=True)
        i2 = self.rotate(1, copy=True)
        i3 = self.rotate(2, copy=True)
        i4 = self.rotate(3, copy=True)
        return [i1, i2, i3, i4]

    def variations(self) -> list[Image]:
        i1 = self.flip(copy=True)
        return self.rotations() + i1.rotations()

def imageConcat(imageIter: Iterable[Union[Image, np.ndarray]], vertical: bool = False) -> Image:
    """
    This is an helper function in order to concatenate several images in one passage.
    """
    for i in range(len(imageIter)):
        if isinstance(imageIter[i], Image):
            imageIter[i] = imageIter[i].pixels

    imageIter = cast(Iterable[np.ndarray], imageIter)
    if vertical:
        axis = 0
    else:
        axis = 1
    return Image(np.concatenate(imageIter, axis=axis))


class Map():
    """
    Map class: a window on the state of a Position-based 2D plane representation.

    Syntax: Map(visual, frame=None, xmin, ymin, xmax, ymax) [not hashable]

    Map uses the frame, if available, or the min and max parameters otherwise,
    to determine the looking zone (default 10×10, starting from (0,0)).
    If frame is not None, xmin and ymin are assumed 0 and the max come from frame.
    visual is the key of the Map: visual takes a Position
    and returns the character to display in that position.
    visual is called once for each position in the frame when requesting an image.
    The image is requested via slicing or the image() method (returning an Image object) or via str (returning str(map.image()))
    """
    def __init__(
            self,
            visual: Callable[[Position], str] = lambda p: ".",
            frame: Optional[Iterable[Iterable[Any]]] = None,
            xmin: int = 0,
            xmax: int = 9,
            ymin: int = 0,
            ymax: int = 9
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

    def __getitem__(self, key: DoubleSlice) -> Image:
        (yslice, xslice) = _setDoubleSlice(key)
        yrange = _sliceToRange(yslice, self.ymin, self.ymax)
        xrange = _sliceToRange(xslice, self.xmin, self.xmax)

        visualRepr = [[self._visualFunction(Position(x,y)) for x in xrange] for y in yrange]
        
        return Image(visualRepr) 

    def image(self) -> Image:
        return self[:,:]
    
    def __str__(self) -> str:
        return str(self.image())

    def __repr__(self) -> str:
        return str(self)


# Random classes and functions

class LinkedList():
    """
    LinkedList class: an implementation of a circular double linked list

    Syntax: LinkedList(data) [not hashable]

    LinkedList is the starting node in a linked list.
    It starts with linked.data = data, linked.next = linked.prev = linked.
    linked.add(data) adds the specified data AFTER the node pointed by linked, and returns the new node
    linked.delete() removes the pointed node, and returns the node BEFORE the deleted one, if any.
    If the deleted node was the only one, returns None.
    Note that linked.add(data).delete() is idempotent.
    The list can be traversed by using linked.next, linked.prev or linked.move(n=1)
    linked.move() requires the number of steps to move forward: if negative moves backward
    """
    def __init__(self, data: Any) -> None:
        self.data = data
        self.next = self
        self.prev = self
    
    def add(self, othData: Any) -> LinkedList:
        other = LinkedList(othData)
        other.prev = self
        other.next = self.next
        self.next.prev = other
        self.next = other
        return other

    def delete(self) -> Optional[LinkedList]:
        if self.next == self:
            del(self)
            return None
        else:
            self.next.prev = self.prev
            self.prev.next = self.next
            ret = self.prev
            del(self)
            return ret

    def move(self, n: int = 1) -> LinkedList:
        ret = self
        if n > 0:
            for _ in range(n):
                ret = ret.next
        elif n < 0:
            for _ in range(-n):
                ret = ret.prev
        return ret

    def __eq__(self, other: LinkedList) -> bool:
        return self is other


# Easier md5
def md5(string: str) -> str:
    return hashlib.md5(string.encode()).hexdigest()


def aStar(
    start: Position,
    goal: Position,
    distanceFunction: Callable[[Position, Position], Numeric] = lambda p, q: p.distance(q),
    includeCorners: bool = False
) -> Numeric:
    """
    A* Traversing algorithm.

    Usage: aStar(start, goal, *distanceFunction, *includeCorners)

    Assuming start and goal as instances of class Position
    or at least assuming that they are ordered, hashable and
    with a method called adjacent with parameter includeCorners.
    If called without specifiyng a distance fuction,
    it also assumes that there is a method called distance(otherPosition)
    """

    estimate = partial(distanceFunction, goal)
    openSet: PriorityQueue[tuple[Numeric, Position]] = PriorityQueue()
    distance = {start: 0}
    openSet.put((estimate(start) + distance[start], start))

    while not openSet.empty():
        if goal in distance:
            return distance[goal]
        
        (_, current) = openSet.get()
        for p in current.adjacent(includeCorners=includeCorners):
            tentativeDistance = distance[current] + distanceFunction(current, p)
            if p not in distance or distance[p] > tentativeDistance:
                distance[p] = tentativeDistance
                openSet.put((estimate(p) + distance[p], p))
    return -1


