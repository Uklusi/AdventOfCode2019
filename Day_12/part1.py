from AoCUtils import *


result = 0
partNumber = "1"

writeToLog = False
if writeToLog:
    logFile = open("log" + partNumber + ".txt", "w")
else:
    logFile = "stdout"
printLog = printLogFactory(logFile)

"""<x=5, y=13, z=-3>
<x=18, y=-7, z=13>
<x=16, y=3, z=4>
<x=0, y=8, z=8>"""

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

NUMMOVES = 1000

for _ in range(NUMMOVES):
    step()

for i in range(len(positions)):
    potentialEnergy = positions[i].distance()
    kineticEnergy = velocities[i].distance()
    result += potentialEnergy * kineticEnergy









with open("output" + partNumber + ".txt", "w") as output:
    output.write(str(result))
    print(str(result))

if writeToLog:
    logFile.close()