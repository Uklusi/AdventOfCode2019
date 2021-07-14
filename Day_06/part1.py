from collections import defaultdict
result = 0

orbits = defaultdict(lambda: [])
numorbits = {"COM": 0}

with open("input.txt", "r") as input:
    for line in input:
        line = line.strip().split(")")
        orbits[line[0]].append(line[1])

processing = ["COM"]
while len(processing) > 0:
    c = processing.pop()
    n = numorbits[c]
    for new in orbits[c]:
        processing.append(new)
        numorbits[new] = n + 1
        result += n + 1

with open("output1.txt", "w") as output:
    output.write(str(result))
    print(str(result))

