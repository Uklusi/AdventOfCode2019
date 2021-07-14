from AoCUtils import *
from intcode import Interpreter, readTape


result = 0
partNumber = "1"

writeToLog = False
if writeToLog:
    logFile = open("log" + partNumber + ".txt", "w")
else:
    logFile = "stdout"
printLog = printLogFactory(logFile)


intCodeTape = readTape("input.txt")

interpreter = Interpreter(intCodeTape, interactive=False)

outputs = interpreter.runOutput()

block = "\u25A1"
paddle = "_"
ball = "o"

idDictionary = {
    0: empty,
    1: solid,
    2: block,
    3: paddle,
    4: ball
}

xl: list[int] = []
yl: list[int] = []

for tileDataIndex in range(0, len(outputs), 3):
    x = outputs[tileDataIndex]
    y = outputs[tileDataIndex + 1]
    xl.append(x)
    yl.append(y)
    tileId = outputs[tileDataIndex + 2]

    if idDictionary[tileId] == block:
        result += 1

print(max(xl), max(yl))




with open("output" + partNumber + ".txt", "w") as outputFile:
    outputFile.write(str(result))
    print(str(result))

if writeToLog:
    cast(TextIOWrapper, logFile).close()

