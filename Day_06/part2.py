from collections import defaultdict
result = 0

orbits = defaultdict(lambda: [])
numorbits = {"COM": 0}
orbited = {}

with open("input.txt", "r") as input:
    for line in input:
        line = line.strip().split(")")
        orbits[line[0]].append(line[1])
        orbited[line[1]] = line[0]

processing = ["COM"]
while len(processing) > 0:
    c = processing.pop()
    n = numorbits[c]
    for new in orbits[c]:
        processing.append(new)
        numorbits[new] = n + 1

def commonAncestor(c1, c2):
    n1 = numorbits[c1]
    n2 = numorbits[c2]
    if n1 > n2:
        for _ in range(n1 - n2):
            c1 = orbited[c1]
    elif n1 < n2:
        for _ in range(n2 - n1):
            c2 = orbited[c2]
    while c1 != c2:
        c1 = orbited[c1]
        c2 = orbited[c2]
    return c1

start = "YOU"
target = "SAN"
ancestor = commonAncestor(start, target)

result = numorbits[start] - 1 + numorbits[target] - 1 - 2 * numorbits[ancestor]

with open("output2.txt", "w") as output:
    output.write(str(result))
    print(str(result))

