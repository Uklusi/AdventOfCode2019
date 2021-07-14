result = 0

w = 25
h = 6

layers = []
layersStr = []
with open("input.txt", "r") as input:
    for line in input:
        line = line.strip()
        for i in range(0, len(line), w*h):
            layerStr = line[i:i+w*h]
            layer = []
            for j in range(h):
                layer.append(layerStr[j*w: (j+1)*w])
            layers.append(layer)
            layersStr.append(layerStr)

maxStr = min(layersStr, key=lambda s: s.count("0"))
result = maxStr.count("1") * maxStr.count("2")
                


with open("output1.txt", "w") as output:
    output.write(str(result))
    print(str(result))

