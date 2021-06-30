result = 0

with open("input.txt", "r") as input:
    [line1, line2] = [ l.split(",") for l in input.read().strip().split('\n') ]

def readInstruction(instruction):
    letter = instruction[0]
    value = int(instruction[1:])
    return (letter, value)

def setPositions(instructionList):
    pos = (0,0)
    positions = set()
    for instruction in instructionList:
        (letter, value) = readInstruction(instruction)
        for i in range(0, value):
            if letter == "U":
                pos = (pos[0], pos[1] + 1)
            elif letter == "D":
                pos = (pos[0], pos[1] - 1)
            elif letter == "L":
                pos = (pos[0] - 1, pos[1])
            elif letter == "R":
                pos = (pos[0] + 1, pos[1])
            positions.add(pos)
    return positions


posSet1 = setPositions(line1)
posSet2 = setPositions(line2)

intersection = posSet1 & posSet2

for pos in intersection:
    d = abs(pos[0]) + abs(pos[1])
    if d < result or result == 0:
        result = d

with open("output1.txt", "w") as output:
    output.write(str(result))
    print(str(result))
