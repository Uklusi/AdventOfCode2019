from AoCUtils import *
from collections import defaultdict
from queue import Queue
from math import ceil


result = 0
partNumber = "1"

writeToLog = False
if writeToLog:
    logFile = open("log" + partNumber + ".txt", "w")
else:
    logFile = "stdout"
printLog = printLogFactory(logFile)

dependencies: dict[str, tuple[int, list[tuple[int, str]]]] = {}

with open("input.txt", "r") as inputFile:
    lines = inputFile.read().strip().split("\n")
    for line in lines:
        (requirements, target) = line.strip().split(" => ")
        (tnumStr, target) = target.split()
        tnum = int(tnumStr)
        requirements = requirements.split(", ")
        requirements = [r.split() for r in requirements]
        requirements = [ (int(r[0]), r[1]) for r in requirements ]
        dependencies[target] = (tnum, requirements)

missingChemicals: defaultdict[str, int] = defaultdict(lambda: 0)
missingChemicals["FUEL"] = 1

chemicalsQueue: Queue[str] = Queue()
chemicalsQueue.put("FUEL")

def solve(chemical: str) -> None:
    if chemical == "ORE":
        return
    missing = missingChemicals[chemical]
    if missing <= 0:
        return
    targetDependencies = dependencies[chemical]
    productionQuant = targetDependencies[0]
    targetDependencies = targetDependencies[1]
    productionNum = ceil(missing / productionQuant)
    missingChemicals[chemical] -= productionQuant * productionNum
    for (depQuant, dep) in targetDependencies:
        missingChemicals[dep] += depQuant * productionNum
        chemicalsQueue.put(dep)

while not chemicalsQueue.empty():
    chemical = chemicalsQueue.get()
    solve(chemical)

result = missingChemicals["ORE"]










with open("output" + partNumber + ".txt", "w") as outputFile:
    outputFile.write(str(result))
    print(str(result))

if writeToLog:
    cast(TextIOWrapper, logFile).close()

