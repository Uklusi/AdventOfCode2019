from intCode.intCodeInterpreter import IntCodeInterpreter
result = 0

with open("input.txt", "r") as input:
    data = input.read().strip()

origIntCodeTape = [int(n) for n in data.split(",")]

expectedResult = 19690720

for i in range(0, 100):
    for j in range(0, 100):
        intCodeTape = origIntCodeTape.copy()
        intCodeTape[1] = i
        intCodeTape[2] = j

        program = IntCodeInterpreter(intCodeTape)

        program.run()
        tentativeResult = program.tape[0]

        if tentativeResult == expectedResult:
            result = 100 * i + j
            break
    else:
        continue
    break

with open("output1.txt", "w") as output:
    output.write(str(result))
    print(str(result))
