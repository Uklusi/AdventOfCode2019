result = 0

with open("input.txt", "r") as input:
    data = input.read().strip()

intCodeTape = [int(n) for n in data.split(",")]


class IntCodeInterpreter:
    def __init__(self, intCodeTape):
        self.pos = 0
        self.tape = intCodeTape
    
    def _intCode1(self):
        posIn1 = self.tape[self.pos + 1]
        posIn2 = self.tape[self.pos + 2]
        posOut = self.tape[self.pos + 3]
        num1 = self.tape[posIn1]
        num2 = self.tape[posIn2]
        self.tape[posOut] = num1 + num2
        self.pos += 4
        return True

    def _intCode2(self):
        posIn1 = self.tape[self.pos + 1]
        posIn2 = self.tape[self.pos + 2]
        posOut = self.tape[self.pos + 3]
        num1 = self.tape[posIn1]
        num2 = self.tape[posIn2]
        self.tape[posOut] = num1 * num2
        self.pos += 4
        return True

    def _intCode99(self):
        return False

    def step(self):
        code = self.tape[self.pos]
        if code == 1:
            return self._intCode1()
        elif code == 2:
            return self._intCode2()
        elif code == 99:
            return self._intCode99()
        else:
            raise(
                ValueError(
                    "Unknown code: {} at position {}".format(code, self.pos)
                )
            )


intCodeTape[1] = 12
intCodeTape[2] = 2

program = IntCodeInterpreter(intCodeTape)

while(program.step()):
    pass

result = program.tape[0]

with open("output1.txt", "w") as output:
    output.write(str(result))
    print(str(result))
