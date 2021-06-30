from intCode.intCodeInterpreter import IntCodeInterpreter, readTape

result = 0

intCodeTape = readTape("input.txt")

program = IntCodeInterpreter(intCodeTape, interactive=False, inputs=[2])
result, = program.run()

with open("output2.txt", "w") as output:
    output.write(str(result))
    print(str(result))
