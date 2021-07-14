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
for asteroid in asteroidList:
    for other in asteroidList:
        if other != asteroid:
            directions[asteroid].add((asteroid - other).direction())

result = max([len(directions[a]) for a in directions])

with open("output1.txt", "w") as output:
    output.write(str(result))
    print(str(result))

