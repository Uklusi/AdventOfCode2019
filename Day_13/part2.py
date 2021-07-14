from AoCUtils import *
from intcode import Interpreter, readTape
from collections import defaultdict


result = 0
partNumber = "2"

writeToLog = False
if writeToLog:
    logFile = open("log" + partNumber + ".txt", "w")
else:
    logFile = "stdout"
printLog = printLogFactory(logFile)


intCodeTape = readTape("input.txt")
intCodeTape[0] = 2

interpreter = Interpreter(intCodeTape, interactive=False)

block = "\u25A1"
paddle = "-"
ball = "o"

idDictionary = {
    0: empty,
    1: solid,
    2: block,
    3: paddle,
    4: ball
}

tileData: defaultdict[Position, str] = defaultdict(lambda: empty)
ballAndPaddle = {ball: Position(0,0), paddle: Position(0,0)}

def updateScreen(updateData: list[int]):
    global tileData
    global result
    for tileDataIndex in range(0, len(updateData), 3):
        x = updateData[tileDataIndex]
        y = updateData[tileDataIndex + 1]
        tileId = updateData[tileDataIndex + 2]

        if x == -1:
            result = tileId
        else:
            tile = idDictionary[tileId]
            pos = Position(x,y)
            tileData[pos] = tile
            if tile in ballAndPaddle:
                ballAndPaddle[tile] = pos

screen = Map(visual = lambda p: tileData[p], xmax=42, ymax = 23)

outputValuesForCallback: list[int] = []

def outputCallback(output: int):
    global outputValuesForCallback
    outputValuesForCallback.append(output)
    if len(outputValuesForCallback) == 3:
        updateScreen(outputValuesForCallback)
        outputValuesForCallback = []

interpreter.setOutputCallback(outputCallback)

def inputCallback():
    # printLog(screen)
    interpreter.addInput(sign(ballAndPaddle[ball].x - ballAndPaddle[paddle].x))

interpreter.setInputCallback(inputCallback)

interpreter.run()



with open("output" + partNumber + ".txt", "w") as outputFile:
    outputFile.write(str(result))
    print(str(result))

if writeToLog:
    cast(TextIOWrapper, logFile).close()

