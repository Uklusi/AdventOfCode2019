result = 0


def fuelRequest(mass):
    value = mass // 3 - 2
    return value if value > 0 else 0


def fuelRequestTotal(startingMass):
    tot = 0
    currentMass = startingMass
    while currentMass > 0:
        currentFuel = fuelRequest(currentMass)
        tot += currentFuel
        currentMass = currentFuel
    return tot


with open("input.txt", "r") as input:
    for line in input:
        mass = int(line.strip())
        result += fuelRequestTotal(mass)


with open("output2.txt", "w") as output:
    output.write(str(result))
    print(str(result))
