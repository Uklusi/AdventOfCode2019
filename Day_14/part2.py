from AoCUtils import *
from collections import defaultdict
from queue import Queue
from math import ceil


result = 0
partNumber = "2"

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

def check(chemical: str, missingChemicals: defaultdict[str, int], chemicalsQueue: Queue[str]) -> tuple[defaultdict[str, int], Queue[str]]:
    if chemical == "ORE":
        return (missingChemicals, chemicalsQueue)
    missing = missingChemicals[chemical]
    if missing <= 0:
        return (missingChemicals, chemicalsQueue)
    targetDependencies = dependencies[chemical]
    productionQuant = targetDependencies[0]
    targetDependencies = targetDependencies[1]
    productionNum = ceil(missing / productionQuant)
    missingChemicals[chemical] -= productionQuant * productionNum
    for (depQuant, dep) in targetDependencies:
        missingChemicals[dep] += depQuant * productionNum
        chemicalsQueue.put(dep)
    return (missingChemicals, chemicalsQueue)

chemicalsQueue: Queue[str] = Queue()

def solve(fuelNum: int) -> int:
    missingChemicals: defaultdict[str, int] = defaultdict(lambda: 0)
    missingChemicals["FUEL"] = fuelNum

    chemicalsQueue: Queue[str] = Queue()
    chemicalsQueue.put("FUEL")
    while not chemicalsQueue.empty():
        chemical = chemicalsQueue.get()
        (missingChemicals, chemicalsQueue) = check(chemical, missingChemicals, chemicalsQueue)
    
    return missingChemicals["ORE"]

orePer1Fuel = solve(1)

oreQuantity = cast(int, 10 ** 12)

minFuelProduction = oreQuantity // orePer1Fuel

result = binSearch(minFuelProduction, 4 * minFuelProduction, lambda n: solve(n) <= oreQuantity)






with open("output" + partNumber + ".txt", "w") as outputFile:
    outputFile.write(str(result))
    print(str(result))

if writeToLog:
    cast(TextIOWrapper, logFile).close()

