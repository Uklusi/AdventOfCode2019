from AoCUtils import *
from math import lcm


result = 0
partNumber = "2"

writeToLog = False
if writeToLog:
    logFile = open("log" + partNumber + ".txt", "w")
else:
    logFile = "stdout"
printLog = printLogFactory(logFile)

"""<x=-1, y=0, z=2>
<x=2, y=-10, z=-7>
<x=4, y=-8, z=8>
<x=3, y=5, z=-1>"""

Position3D = PositionNDim

positions: list[Position3D] = []
velocities = [Position3D(0,0,0) for _ in range(4)]
 
with open("input.txt", "r") as inputFile:
    lines = inputFile.read().strip().split("\n")
    for line in lines:
        line = line.strip().strip("<>").split(", ")
        line = [int(s.split("=")[1]) for s in line]
        positions.append(Position3D( line ))

def gravity(p: Position3D, q: Position3D) -> Position3D:
    return Position3D( [sign(q.coordinates[i] - p.coordinates[i]) for i in range(3)] )

def applyGravity():
    for (i, moon) in enumerate(positions):
        for otherMoon in positions:
            velocities[i] += gravity(moon, otherMoon)

def move():
    for i in range(len(positions)):
        positions[i] += velocities[i]

def step():
    applyGravity()
    move()

def extractCoordinates(coordToExtract: int) -> tuple[int, ...]:
    return tuple(p.coordinates[coordToExtract] for p in positions) + tuple(v.coordinates[coordToExtract] for v in velocities)

earliestOccurrence = {i: {extractCoordinates(i): 0} for i in range(3)}
antiperiods = [0, 0, 0]
periods = [-1, -1, -1]

stepNum = 0
while any([p == -1 for p in periods]):
    step()
    stepNum += 1
    for i in range(3):
        coordsI = extractCoordinates(i)
        if periods[i] == -1:
            if coordsI in earliestOccurrence[i]:
                antiperiods[i] = earliestOccurrence[i][coordsI]
                periods[i] = stepNum - earliestOccurrence[i][coordsI]
            else:
                earliestOccurrence[i][coordsI] = stepNum

result = max(antiperiods) + lcm( *periods )







with open("output" + partNumber + ".txt", "w") as output:
    output.write(str(result))
    print(str(result))

if writeToLog:
    logFile.close()