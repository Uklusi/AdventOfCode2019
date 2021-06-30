result = 0


def fuelRequest(mass):
    value = mass // 3 - 2
    return value if value > 0 else 0


with open("input.txt", "r") as input:
    for line in input:
        mass = int(line.strip())
        result += fuelRequest(mass)


with open("output1.txt", "w") as output:
    output.write(str(result))
    print(str(result))
