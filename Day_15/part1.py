from AoCUtils import *
from intcode import *

result = 0
partNumber = "1"

writeToLog = True
if writeToLog:
    logFile = open("log" + partNumber + ".txt", "w")
else:
    logFile = "stdout"
printLog = printLogFactory(logFile)


intCodeTape = readTape("input.txt")

interpreter = Interpreter(intCodeTape=intCodeTape)


def findClosestUnknown(p: MapAgent) -> Position:
    global unknownPositions
    closest = min(unknownPositions, key=lambda q: (p.distance(q), q))
    return closest

def createMovementSequence(robot: MapAgent, goal: Position) -> list[Literal[1,2,3,4]]:
    seq = aStar(robot.mapPosition(), goal, returnPath=True)
    # breakpoint()
    return [ convertDirToInput((b-a).directionIndicator()) for (a, b) in zip(seq, seq[1:]) ]

def convertDirToInput(d: Literal[0,1,2,3]) -> Literal[1,2,3,4]:
    if d == 0:
        return 1
    elif d == 1:
        return 4
    else:
        return d

def convertInputToDir(d: Literal[1,2,3,4]) -> Literal[0,1,2,3]:
    if d == 1:
        return 0
    elif d == 4:
        return 1
    else:
        return d

start = Position(0,0, reverseY=True)
knownPositions = {start: 1}
unknownPositions = set( start.adjacent() )

def isSolid(p: Position) -> bool:
    if isinstance(p, Agent):
        p = p.position()
    if p in knownPositions:
        return knownPositions[p] == 0
    return True

robot = MapAgent(0, 0, occupied=isSolid)
target = Position(0, 0) # Just a placeholder
movement: Literal[1,2,3,4] = 1

def inputCallBack() -> None:
    global robot
    global interpreter
    global target
    global movement
    if len(unknownPositions) == 0:
        interpreter.stop()
        interpreter.addInput(1)
        return
    target = findClosestUnknown(robot)
    movement = createMovementSequence(robot, target)[0]
    interpreter.addInput(movement)

def visualFunction(p: Position) -> str:
    if isinstance(p, Agent):
        p = p.position()
    if p == robot:
        return "O"
    if p in knownPositions:
        if p == Position(0,0):
            return "+"
        elif knownPositions[p] == 0:
            return solid
        elif knownPositions[p] == 1:
            return empty
        else:
            return "X"
    else:
        return path

newMap = Map(visual=visualFunction, xmin=-21, xmax = 19, ymin=-21, ymax = 19)

def outputCallback(n: int) -> None:
    global robot
    global target
    global movement
    global unknownPositions
    mov = movement
    newRobPos = robot.position() + VectorDir(direction=convertInputToDir(mov), reverseY=True)
    knownPositions[newRobPos] = n
    unknownPositions.discard(newRobPos)
    if n != 0:
        robot.moveTo(newRobPos)
        # printLog(newRobPos.stdcoords())
        # printLog([p.stdcoords() for p in newRobPos.adjacent()])
        unknownPositions |= {p for p in newRobPos.adjacent() if p not in knownPositions}
        # printLog(unknownPositions)
    printLog(newMap)
    printLog()



interpreter.setInputCallback(callback=inputCallBack)
interpreter.setOutputCallback(callback=outputCallback)
interpreter.start()
interpreter.join()

target = [p for p in knownPositions if knownPositions[p] == 2 ][0]
result = aStar(MapPosition(0, 0, occupied=isSolid), target)




with open("output" + partNumber + ".txt", "w") as outputFile:
    outputFile.write(str(result))
    print(str(result))

if writeToLog:
    cast(TextIOWrapper, logFile).close()

