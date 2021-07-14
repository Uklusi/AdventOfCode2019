from AoCUtils import *

result = 0

w = 25
h = 6

layersStr = []
with open("input.txt", "r") as input:
    for line in input:
        line = line.strip()
        for i in range(0, len(line), w*h):
            layerStr = line[i:i+w*h]
            layersStr.append(layerStr)

imageStr = ""
for i in range(w*h):
    j = 0
    while len(imageStr) == i:
        if layersStr[j][i] == "0":
            imageStr += solid
        elif layersStr[j][i] == "1":
            imageStr += empty
        else:
            j += 1

image = Image([imageStr[j*w : (j+1)*w] for j in range(h)])

print(image)


with open("output2.txt", "w") as output:
    output.write(str(result))
    print(str(result))

