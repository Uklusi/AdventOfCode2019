from AoCUtils import *
from itertools import cycle
from operator import mul, concat
from functools import reduce


result = 0
partNumber = "1"

writeToLog = False
if writeToLog:
    logFile = open("log" + partNumber + ".txt", "w")
else:
    logFile = "stdout"
printLog = printLogFactory(logFile)

inputSequence: list[int] = []

with open("input.txt", "r") as inputFile:
    inputSequence = [int(n) for n in inputFile.read().strip()]

basePattern = [0, 1, 0, -1]

def createPattern(position: int) -> Iterable:
    tempPattern = reduce(concat, [[i] * (position + 1) for i in basePattern], [])
    cycledPattern = cycle(tempPattern)
    cycledPattern.__next__()
    return cycledPattern

def applyPattern(sequence: list[int]) -> list[int]:
    ret = []
    for i in range(len(sequence)):
        res = sum(map(mul, createPattern(i), sequence))
        ret.append(int(str(res)[-1]))
    return ret

sequence = inputSequence

for _ in range(100):
    sequence = applyPattern(sequence)

result = join(sequence[:8])

with open("output" + partNumber + ".txt", "w") as outputFile:
    outputFile.write(str(result))
    print(str(result))

if writeToLog:
    cast(TextIOWrapper, logFile).close()

