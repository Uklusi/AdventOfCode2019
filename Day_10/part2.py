from collections import defaultdict
from AoCUtils import *
result = 0

frame = []
with open("input.txt", "r") as input:
    frame = input.read().strip().split("\n")

asteroidList = []
for (y,l) in enumerate(frame):
    for (x, c) in enumerate(l):
        if c == "#":
            asteroidList.append(Position(x,y, reverseY=True))

directions = defaultdict(lambda: set())
visibleAll = defaultdict(lambda: defaultdict(lambda: Position(9999, 9999)))
for asteroid in asteroidList:
    for other in asteroidList:
        if other != asteroid:
            vector = (other - asteroid)
            direction = vector.direction()
            directions[asteroid].add(direction)
            otherP = visibleAll[asteroid][direction]
            visibleAll[asteroid][direction] = otherP if (otherP - asteroid).length() <= vector.length() else other


base = max(directions, key=lambda a: len(directions[a]))
visibleDirections = [ vector for vector in directions[base] ]

def keyForVectors(vector):
    vector = vector.direction(normalized=True)
    x = vector.vx
    y = vector.vy
    if x >= 0:
        return y
    else:
        return 2 - y

visibleDirections.sort(key=keyForVectors)
result = visibleDirections[199]
result = visibleAll[base][result]
result = f"{result.x}{result.y:02d}"

with open("output2.txt", "w") as output:
    output.write(str(result))
    print(str(result))

