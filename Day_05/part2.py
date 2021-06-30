from intCode.intCodeInterpreter import IntCodeInterpreter, readTape

intCodeTape = readTape("input.txt")

program = IntCodeInterpreter(intCodeTape)

program.run()
