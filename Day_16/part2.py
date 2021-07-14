from AoCUtils import *
from math import ceil


result = 0
partNumber = "2"

writeToLog = False
if writeToLog:
    logFile = open("log" + partNumber + ".txt", "w")
else:
    logFile = "stdout"
printLog = printLogFactory(logFile)

inputSequence: list[int] = []

# For how the problem is, position i depends only from positions i:end
# Also the number of integers to skip at the beginning is so high that
# after that point, the only number in the pattern is 1 (so we just sum
# the numbers from there to the end)
with open("input.txt", "r") as inputFile:
    inputSequence = [int(n) for n in inputFile.read().strip()]
    l = len(inputSequence)
    numsToSkip = int(join(inputSequence[:7]))
    inputSequence = (inputSequence[numsToSkip % l:] + inputSequence * (10000 - ceil(numsToSkip / l)))

# This is the assertion telling us that we can sum the numbers instead of
# devising the pattern
assert numsToSkip * 2 > 10000 * l

def applyPattern(sequence: list[int]) -> list[int]:
    tot = sum(sequence)
    ret = []
    for n in sequence:
        ret.append(int(str(tot)[-1]))
        tot -= n
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

