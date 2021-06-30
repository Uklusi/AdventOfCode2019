result = 0

with open("input.txt", "r") as input:
    [line1, line2] = [ l.split(",") for l in input.read().strip().split('\n') ]


def readInstruction(instruction):
    letter = instruction[0]
    value = int(instruction[1:])
    return (letter, value)


def move(direction, pos):
    if direction == "U":
        pos = (pos[0], pos[1] + 1)
    elif direction == "D":
        pos = (pos[0], pos[1] - 1)
    elif direction == "L":
        pos = (pos[0] - 1, pos[1])
    elif direction == "R":
        pos = (pos[0] + 1, pos[1])
    return pos


def setPositions(instructionList):
    pos = (0, 0)
    positions = set()
    for instruction in instructionList:
        (letter, value) = readInstruction(instruction)
        for i in range(0, value):
            pos = move(letter, pos)
            positions.add(pos)
    return positions


def checkDistance(instructionList, targetPos):
    pos = (0, 0)
    d = 0
    for instruction in instructionList:
        (letter, value) = readInstruction(instruction)
        for i in range(0, value):
            pos = move(letter, pos)
            d += 1
            if pos == targetPos:
                return d


posSet1 = setPositions(line1)
posSet2 = setPositions(line2)

intersection = posSet1 & posSet2

for pos in intersection:
    d = checkDistance(line1, pos) + checkDistance(line2, pos)
    if d < result or result == 0:
        result = d

with open("output2.txt", "w") as output:
    output.write(str(result))
    print(str(result))
